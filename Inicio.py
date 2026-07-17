import streamlit as st
import pandas as pd

from datetime import datetime
from zoneinfo import ZoneInfo
from io import BytesIO

from database import crear_tabla, obtener_lavados, supabase
from auth import login
from navbar import aplicar_estilos, navbar
from utils import formato_pesos

from views.Registrar_Lavada import mostrar_registrar_lavada
from views.Lavadas_Del_Dia import mostrar_lavadas_del_dia
from views.Cierre_Del_Dia import mostrar_cierre_del_dia


# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Moto Space Wash",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CONSULTAR PAGOS DE EMPLEADOS
# =========================================================

def obtener_pagos_empleados(fecha_inicio, fecha_fin):
    """
    Consulta los pagos realizados dentro del rango de fechas.
    """

    try:
        response = (
            supabase
            .table("pagos_empleados")
            .select("*")
            .gte("fecha", fecha_inicio)
            .lte("fecha", fecha_fin)
            .execute()
        )

        return pd.DataFrame(response.data or [])

    except Exception:
        return pd.DataFrame()

# =========================================================
# CONSULTAR GASTOS
# =========================================================

def obtener_gastos(fecha_inicio, fecha_fin):
    """
    Consulta los gastos registrados dentro del rango de fechas.
    """

    try:
        response = (
            supabase
            .table("gastos")
            .select("*")
            .gte("fecha", fecha_inicio)
            .lte("fecha", fecha_fin)
            .execute()
        )

        return pd.DataFrame(response.data or [])

    except Exception:
        return pd.DataFrame()
    
# =========================================================
# NORMALIZAR DATOS DE LAVADAS
# =========================================================

def preparar_dataframe_lavados(df):
    """
    Agrega columnas faltantes y normaliza los datos
    para evitar errores en la vista y en el Excel.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    columnas_por_defecto = {
        "id": 0,
        "fecha": "",
        "hora": "",
        "gamusero": "Sin asignar",
        "nombre_cliente": "",
        "telefono_cliente": "",
        "placa": "",
        "valor_lavada": 0,
        "pago_gamusero": 0,
        "ganancia_negocio": 0,
        "coin": False,
        "metodo_pago": "Efectivo",
        "observaciones": ""
    }

    for columna, valor_defecto in columnas_por_defecto.items():
        if columna not in df.columns:
            df[columna] = valor_defecto

    columnas_texto = {
        "fecha": "",
        "hora": "",
        "gamusero": "Sin asignar",
        "nombre_cliente": "",
        "telefono_cliente": "",
        "placa": "",
        "metodo_pago": "Efectivo",
        "observaciones": ""
    }

    for columna, valor_defecto in columnas_texto.items():
        df[columna] = (
            df[columna]
            .fillna(valor_defecto)
            .astype(str)
        )

    columnas_numericas = [
        "valor_lavada",
        "pago_gamusero",
        "ganancia_negocio"
    ]

    for columna in columnas_numericas:
        df[columna] = (
            pd.to_numeric(
                df[columna],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )

    df["coin"] = (
        df["coin"]
        .fillna(False)
        .astype(bool)
    )

    return df


# =========================================================
# NORMALIZAR DATOS DE PAGOS
# =========================================================

def preparar_dataframe_pagos(df_pagos):
    """
    Agrega columnas faltantes y normaliza los pagos.
    """

    columnas_por_defecto = {
        "fecha": "",
        "empleado": "",
        "rol": "",
        "cantidad_servicios": 0,
        "total_realizado": 0,
        "valor_pagar": 0,
        "pagado_por": ""
    }

    if df_pagos is None or df_pagos.empty:
        return pd.DataFrame(
            columns=list(columnas_por_defecto.keys())
        )

    df_pagos = df_pagos.copy()

    for columna, valor_defecto in columnas_por_defecto.items():
        if columna not in df_pagos.columns:
            df_pagos[columna] = valor_defecto

    columnas_texto = [
        "fecha",
        "empleado",
        "rol",
        "pagado_por"
    ]

    for columna in columnas_texto:
        df_pagos[columna] = (
            df_pagos[columna]
            .fillna("")
            .astype(str)
        )

    columnas_numericas = [
        "cantidad_servicios",
        "total_realizado",
        "valor_pagar"
    ]

    for columna in columnas_numericas:
        df_pagos[columna] = (
            pd.to_numeric(
                df_pagos[columna],
                errors="coerce"
            )
            .fillna(0)
        )

    return df_pagos


# =========================================================
# GENERAR ARCHIVO EXCEL
# =========================================================

def generar_excel_historial(
    df_filtrado,
    df_pagos,
    total_vendido,
    total_pagado_empleados,
    total_pagado_encargado,
    total_pagado_general,
    ganancia_final_negocio
):
    """
    Genera un Excel con tres hojas:

    1. Resumen financiero.
    2. Pagos realizados.
    3. Todos los servicios filtrados.
    """

    buffer = BytesIO()

    # =====================================================
    # HOJA 1: RESUMEN FINANCIERO
    # =====================================================

    resumen_financiero = pd.DataFrame(
        [
            {
                "Total vendido": total_vendido,
                "Pagado a empleados": total_pagado_empleados,
                "Pagado al encargado": total_pagado_encargado,
                "Total pagado": total_pagado_general,
                "Ganancia final del negocio": ganancia_final_negocio
            }
        ]
    )

    # =====================================================
    # HOJA 2: PAGOS REALIZADOS
    # =====================================================

    pagos_excel = preparar_dataframe_pagos(df_pagos)

    pagos_excel = pagos_excel[
        [
            "fecha",
            "empleado",
            "rol",
            "cantidad_servicios",
            "total_realizado",
            "valor_pagar",
            "pagado_por"
        ]
    ].copy()

    pagos_excel = pagos_excel.rename(
        columns={
            "fecha": "Fecha",
            "empleado": "Empleado",
            "rol": "Rol",
            "cantidad_servicios": "Servicios",
            "total_realizado": "Total realizado",
            "valor_pagar": "Valor pagado",
            "pagado_por": "Pagado por"
        }
    )

    # =====================================================
    # HOJA 3: SERVICIOS FILTRADOS
    # =====================================================

    servicios_excel = preparar_dataframe_lavados(
        df_filtrado
    )

    servicios_excel = servicios_excel[
        [
            "id",
            "fecha",
            "hora",
            "gamusero",
            "nombre_cliente",
            "telefono_cliente",
            "placa",
            "valor_lavada",
            "pago_gamusero",
            "ganancia_negocio",
            "coin",
            "metodo_pago",
            "observaciones"
        ]
    ].copy()

    servicios_excel = servicios_excel.sort_values(
        by=[
            "fecha",
            "hora",
            "id"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )

    servicios_excel["coin"] = (
        servicios_excel["coin"]
        .apply(
            lambda valor: "Sí" if bool(valor) else "No"
        )
    )

    servicios_excel["nombre_cliente"] = (
        servicios_excel["nombre_cliente"]
        .fillna("")
        .replace("", "Sin registrar")
    )

    servicios_excel["telefono_cliente"] = (
        servicios_excel["telefono_cliente"]
        .fillna("")
        .replace("", "Sin registrar")
    )

    servicios_excel["metodo_pago"] = (
        servicios_excel["metodo_pago"]
        .fillna("Efectivo")
        .replace("", "Efectivo")
    )

    servicios_excel = servicios_excel.rename(
        columns={
            "id": "Lavada #",
            "fecha": "Fecha",
            "hora": "Hora",
            "gamusero": "Nombre del trabajador",
            "nombre_cliente": "Cliente",
            "telefono_cliente": "Teléfono",
            "placa": "Placa",
            "valor_lavada": "Valor de la lavada",
            "pago_gamusero": "Pago del trabajador",
            "ganancia_negocio": "Ganancia del negocio",
            "coin": "Coin",
            "metodo_pago": "Método de pago",
            "observaciones": "Observaciones"
        }
    )

    # =====================================================
    # CREAR ARCHIVO
    # =====================================================

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:

        resumen_financiero.to_excel(
            writer,
            sheet_name="Resumen financiero",
            index=False
        )

        pagos_excel.to_excel(
            writer,
            sheet_name="Pagos realizados",
            index=False
        )

        servicios_excel.to_excel(
            writer,
            sheet_name="Servicios filtrados",
            index=False
        )

        # Ajustar ancho de las columnas
        for hoja in writer.book.worksheets:
            for columna in hoja.columns:
                ancho_maximo = 0
                letra_columna = columna[0].column_letter

                for celda in columna:
                    contenido = (
                        ""
                        if celda.value is None
                        else str(celda.value)
                    )

                    ancho_maximo = max(
                        ancho_maximo,
                        len(contenido)
                    )

                hoja.column_dimensions[
                    letra_columna
                ].width = min(
                    ancho_maximo + 2,
                    45
                )

    buffer.seek(0)

    return buffer.getvalue()


# =========================================================
# NUEVO INICIO
# =========================================================

def mostrar_inicio():
    """
    Muestra el resumen financiero, pagos realizados
    y detalle de servicios como página de Inicio.
    """

    st.header("Historial general")

    # =====================================================
    # CONSULTAR LAVADAS
    # =====================================================

    try:
        df = obtener_lavados()

    except Exception as error:
        st.error(
            "No se pudo cargar la información de las lavadas."
        )
        st.exception(error)
        return

    if df is None or df.empty:
        st.warning("No hay registros guardados.")
        return

    df = preparar_dataframe_lavados(df)

    # =====================================================
    # FILTRO POR FECHAS
    # =====================================================

    fecha_colombia = datetime.now(
        ZoneInfo("America/Bogota")
    ).date()

    col_fecha_inicio, col_fecha_fin = st.columns(2)

    with col_fecha_inicio:
        fecha_inicio = st.date_input(
            "Fecha inicial",
            value=fecha_colombia,
            key="inicio_fecha_inicio"
        )

    with col_fecha_fin:
        fecha_fin = st.date_input(
            "Fecha final",
            value=fecha_colombia,
            key="inicio_fecha_fin"
        )

    if fecha_inicio > fecha_fin:
        st.error(
            "La fecha inicial no puede ser mayor "
            "que la fecha final."
        )
        return

    fecha_inicio_texto = fecha_inicio.strftime(
        "%Y-%m-%d"
    )

    fecha_fin_texto = fecha_fin.strftime(
        "%Y-%m-%d"
    )

    df_filtrado = df.loc[
        (
            df["fecha"] >= fecha_inicio_texto
        )
        & (
            df["fecha"] <= fecha_fin_texto
        )
    ].copy()

    if df_filtrado.empty:
        st.warning(
            "No hay registros en el rango de fechas seleccionado."
        )
        return

    # =====================================================
    # CONSULTAR PAGOS
    # =====================================================

    df_pagos = obtener_pagos_empleados(
        fecha_inicio_texto,
        fecha_fin_texto
    )

    df_pagos = preparar_dataframe_pagos(
        df_pagos
    )

    # =====================================================
    # CONSULTAR GASTOS
    # =====================================================

    df_gastos = obtener_gastos(
        fecha_inicio_texto,
        fecha_fin_texto
    )

    if df_gastos is None or df_gastos.empty:
        df_gastos = pd.DataFrame()
        total_gastos = 0

    else:
        df_gastos = df_gastos.copy()

        if "valor" not in df_gastos.columns:
            df_gastos["valor"] = 0

        df_gastos["valor"] = (
            pd.to_numeric(
                df_gastos["valor"],
                errors="coerce"
            )
            .fillna(0)
            .astype(int)
        )

        total_gastos = int(
            df_gastos["valor"].sum()
        )

    # =====================================================
    # CALCULAR RESUMEN FINANCIERO
    # =====================================================

    total_vendido = int(
        df_filtrado["valor_lavada"].sum()
    )

    if df_pagos.empty:
        total_pagado_empleados = 0
        total_pagado_encargado = 0
        total_pagado_general = 0

    else:
        rol_normalizado = (
            df_pagos["rol"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        total_pagado_empleados = int(
            df_pagos.loc[
                rol_normalizado == "gamusero",
                "valor_pagar"
            ].sum()
        )

        total_pagado_encargado = int(
            df_pagos.loc[
                rol_normalizado == "encargado",
                "valor_pagar"
            ].sum()
        )

        total_pagado_general = int(
            df_pagos["valor_pagar"].sum()
        )

    ganancia_final_negocio = (
        total_vendido
        - total_pagado_general
        - total_gastos
    )

    # =====================================================
    # MÉTRICAS FINANCIERAS
    # =====================================================

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        with st.container(border=True):
            st.metric(
                "Total vendido",
                formato_pesos(total_vendido)
            )

    with col2:
        with st.container(border=True):
            st.metric(
                "Pagos realizados",
                formato_pesos(total_pagado_general)
            )

    with col3:
        with st.container(border=True):
            st.metric(
                "Gastos",
                formato_pesos(total_gastos)
            )

    with col4:
        with st.container(border=True):
            st.metric(
                "Ganancia final del negocio",
                formato_pesos(ganancia_final_negocio)
            )
            
    # =====================================================
    # BOTÓN DE DESCARGA
    # =====================================================

    archivo_excel = generar_excel_historial(
        df_filtrado=df_filtrado,
        df_pagos=df_pagos,
        total_vendido=total_vendido,
        total_pagado_empleados=total_pagado_empleados,
        total_pagado_encargado=total_pagado_encargado,
        total_pagado_general=total_pagado_general,
        ganancia_final_negocio=ganancia_final_negocio
    )

    col_izquierda, col_centro, col_derecha = st.columns(
        [1, 2, 1]
    )

    with col_centro:
        st.download_button(
            label="Reporte en Excel",
            data=archivo_excel,
            file_name=(
                f"historial_lavado_motos_"
                f"{fecha_inicio_texto}_a_"
                f"{fecha_fin_texto}.xlsx"
            ),
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
            use_container_width=True,
            key="descargar_historial_excel"
        )

    st.divider()

    # =====================================================
    # PAGOS REALIZADOS
    # =====================================================

    st.subheader("Pagos realizados")

    if df_pagos.empty:
        st.info(
            "No hay pagos registrados en este rango de fechas."
        )

    else:
        df_pagos_mostrar = df_pagos[
            [
                "fecha",
                "empleado",
                "rol",
                "cantidad_servicios",
                "total_realizado",
                "valor_pagar",
                "pagado_por"
            ]
        ].copy()

        df_pagos_mostrar["total_realizado"] = (
            df_pagos_mostrar["total_realizado"]
            .apply(formato_pesos)
        )

        df_pagos_mostrar["valor_pagar"] = (
            df_pagos_mostrar["valor_pagar"]
            .apply(formato_pesos)
        )

        df_pagos_mostrar = df_pagos_mostrar.rename(
            columns={
                "fecha": "Fecha",
                "empleado": "Empleado",
                "rol": "Rol",
                "cantidad_servicios": "Servicios",
                "total_realizado": "Total realizado",
                "valor_pagar": "Valor pagado",
                "pagado_por": "Pagado por"
            }
        )

        st.dataframe(
            df_pagos_mostrar,
            use_container_width=True,
            hide_index=True
        )

    st.divider()

    # =====================================================
    # DETALLE DE LAVADAS
    # =====================================================

    st.subheader("Detalle de lavadas")

    df_detalle = df_filtrado.copy()

    df_detalle["valor_lavada"] = (
        df_detalle["valor_lavada"]
        .apply(formato_pesos)
    )

    df_detalle["pago_gamusero"] = (
        df_detalle["pago_gamusero"]
        .apply(formato_pesos)
    )

    df_detalle["ganancia_negocio"] = (
        df_detalle["ganancia_negocio"]
        .apply(formato_pesos)
    )

    df_detalle = df_detalle[
        [
            "id",
            "fecha",
            "hora",
            "gamusero",
            "nombre_cliente",
            "telefono_cliente",
            "placa",
            "valor_lavada",
            "pago_gamusero",
            "ganancia_negocio",
            "coin",
            "metodo_pago",
            "observaciones"
        ]
    ].copy()

    df_detalle = df_detalle.sort_values(
        by=[
            "fecha",
            "hora",
            "id"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )

    df_detalle = df_detalle.rename(
        columns={
            "id": "Lavada #",
            "fecha": "Fecha",
            "hora": "Hora",
            "gamusero": "Nombre del trabajador",
            "nombre_cliente": "Cliente",
            "telefono_cliente": "Teléfono",
            "placa": "Placa",
            "valor_lavada": "Valor",
            "pago_gamusero": "Pago trabajador",
            "ganancia_negocio": "Ganancia negocio",
            "coin": "Coin",
            "metodo_pago": "Método de pago",
            "observaciones": "Observaciones"
        }
    )

    df_detalle["Coin"] = (
        df_detalle["Coin"]
        .apply(
            lambda valor: "Sí" if valor else "No"
        )
    )

    df_detalle["Cliente"] = (
        df_detalle["Cliente"]
        .replace("", "Sin registrar")
    )

    df_detalle["Teléfono"] = (
        df_detalle["Teléfono"]
        .replace("", "Sin registrar")
    )

    df_detalle["Método de pago"] = (
        df_detalle["Método de pago"]
        .replace("", "Efectivo")
        .fillna("Efectivo")
    )

    st.dataframe(
        df_detalle,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# INICIALIZACIÓN DE LA APP
# =========================================================

login()

aplicar_estilos()

crear_tabla()

navbar()


# =========================================================
# OBTENER USUARIO Y ROL
# =========================================================

usuario_actual = (
    st.session_state
    .get("usuario", "")
    .strip()
    .lower()
)

rol_actual = (
    st.session_state.get("rol")
    or usuario_actual
).strip().lower()

st.session_state.rol = rol_actual


# =========================================================
# VALIDAR ROL
# =========================================================

roles_validos = [
    "admin",
    "socio",
    "operador"
]

if rol_actual not in roles_validos:
    st.error(
        "El usuario no tiene un rol válido. "
        "Cierra sesión e ingresa nuevamente."
    )
    st.stop()


# =========================================================
# DEFINIR VISTA INICIAL
# =========================================================

if "vista" not in st.session_state:
    if rol_actual == "operador":
        st.session_state.vista = "Registrar"
    else:
        st.session_state.vista = "Inicio"


# =========================================================
# PROTEGER VISTAS DEL OPERADOR
# =========================================================

if (
    rol_actual == "operador"
    and st.session_state.get("vista")
    in [
        "Inicio",
        "Historial"
    ]
):
    st.session_state.vista = "Registrar"
    st.rerun()


# =========================================================
# OBTENER VISTA ACTUAL
# =========================================================

vista = st.session_state.get(
    "vista",
    "Registrar" if rol_actual == "operador" else "Inicio"
)


# =========================================================
# NAVEGACIÓN
# =========================================================

if vista == "Inicio":
    if rol_actual not in ["admin", "socio"]:
        st.session_state.vista = "Registrar"
        st.rerun()

    mostrar_inicio()


elif vista == "Registrar":
    mostrar_registrar_lavada()


elif vista == "Lavadas":
    mostrar_lavadas_del_dia()


elif vista == "Cierre":
    mostrar_cierre_del_dia()


elif vista == "Historial":
    if rol_actual in ["admin", "socio"]:
        st.session_state.vista = "Inicio"
    else:
        st.session_state.vista = "Registrar"

    st.rerun()


else:
    if rol_actual in ["admin", "socio"]:
        st.session_state.vista = "Inicio"
    else:
        st.session_state.vista = "Registrar"

    st.rerun()