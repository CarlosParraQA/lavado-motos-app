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
    Consulta los pagos realizados a empleados dentro
    del rango de fechas seleccionado.
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
# NORMALIZAR DATOS DE LAVADAS
# =========================================================

def preparar_dataframe_lavados(df):
    """
    Agrega las columnas faltantes y normaliza los datos
    para evitar errores al construir el historial.
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
# NUEVO INICIO
# =========================================================

def mostrar_inicio():
    """
    Muestra el historial, resumen financiero y detalle
    de lavadas como página principal.
    """

    st.header("Historial general")

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
            "La fecha inicial no puede ser mayor que la fecha final."
        )
        return

    fecha_inicio_texto = fecha_inicio.strftime("%Y-%m-%d")
    fecha_fin_texto = fecha_fin.strftime("%Y-%m-%d")

    df_filtrado = df.loc[
        (df["fecha"] >= fecha_inicio_texto)
        & (df["fecha"] <= fecha_fin_texto)
    ].copy()

    if df_filtrado.empty:
        st.warning(
            "No hay registros en el rango de fechas seleccionado."
        )
        return

    # =====================================================
    # RESUMEN FINANCIERO
    # =====================================================

    total_vendido = int(
        df_filtrado["valor_lavada"].sum()
    )

    df_pagos = obtener_pagos_empleados(
        fecha_inicio_texto,
        fecha_fin_texto
    )

    if df_pagos.empty:
        total_pagado_empleados = 0
        total_pagado_encargado = 0
        total_pagado_general = 0

    else:
        columnas_pagos_default = {
            "fecha": "",
            "empleado": "",
            "rol": "",
            "cantidad_servicios": 0,
            "total_realizado": 0,
            "valor_pagar": 0,
            "pagado_por": ""
        }

        for columna, valor_defecto in columnas_pagos_default.items():
            if columna not in df_pagos.columns:
                df_pagos[columna] = valor_defecto

        df_pagos["rol"] = (
            df_pagos["rol"]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

        df_pagos["valor_pagar"] = (
            pd.to_numeric(
                df_pagos["valor_pagar"],
                errors="coerce"
            )
            .fillna(0)
        )

        df_pagos["total_realizado"] = (
            pd.to_numeric(
                df_pagos["total_realizado"],
                errors="coerce"
            )
            .fillna(0)
        )

        total_pagado_empleados = int(
            df_pagos.loc[
                df_pagos["rol"] == "gamusero",
                "valor_pagar"
            ].sum()
        )

        total_pagado_encargado = int(
            df_pagos.loc[
                df_pagos["rol"] == "encargado",
                "valor_pagar"
            ].sum()
        )

        total_pagado_general = int(
            df_pagos["valor_pagar"].sum()
        )

    ganancia_final_negocio = (
        total_vendido - total_pagado_general
    )

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
                "Pagado a empleados",
                formato_pesos(total_pagado_empleados)
            )

    with col3:
        with st.container(border=True):
            st.metric(
                "Pagado al encargado",
                formato_pesos(total_pagado_encargado)
            )

    with col4:
        with st.container(border=True):
            st.metric(
                "Ganancia final del negocio",
                formato_pesos(ganancia_final_negocio)
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

        df_pagos_mostrar = pd.DataFrame()

    else:
        df_pagos_mostrar = df_pagos.copy()

        df_pagos_mostrar["valor_pagar"] = (
            df_pagos_mostrar["valor_pagar"]
            .apply(formato_pesos)
        )

        df_pagos_mostrar["total_realizado"] = (
            df_pagos_mostrar["total_realizado"]
            .apply(formato_pesos)
        )

        columnas_pagos = [
            "fecha",
            "empleado",
            "rol",
            "cantidad_servicios",
            "total_realizado",
            "valor_pagar",
            "pagado_por"
        ]

        df_pagos_mostrar = (
            df_pagos_mostrar[columnas_pagos]
            .rename(
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

    columnas_detalle = [
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

    df_detalle = (
        df_detalle[columnas_detalle]
        .sort_values(
            by=["fecha", "hora", "id"],
            ascending=[False, False, False]
        )
        .rename(
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
    )

    df_detalle["Coin"] = df_detalle["Coin"].apply(
        lambda valor: "Sí" if valor else "No"
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

    st.divider()

    # =====================================================
    # EXPORTAR A EXCEL
    # =====================================================

    resumen_financiero = pd.DataFrame(
        [
            {
                "Total vendido": total_vendido,
                "Pagado a empleados": total_pagado_empleados,
                "Pagado al encargado": total_pagado_encargado,
                "Total pagado": total_pagado_general,
                "Ganancia final negocio": ganancia_final_negocio
            }
        ]
    )

    resumen_financiero_mostrar = (
        resumen_financiero.copy()
    )

    for columna in resumen_financiero_mostrar.columns:
        resumen_financiero_mostrar[columna] = (
            resumen_financiero_mostrar[columna]
            .apply(formato_pesos)
        )

    buffer = BytesIO()

    with pd.ExcelWriter(
        buffer,
        engine="openpyxl"
    ) as writer:

        resumen_financiero_mostrar.to_excel(
            writer,
            sheet_name="Resumen financiero",
            index=False
        )

        if not df_pagos_mostrar.empty:
            df_pagos_mostrar.to_excel(
                writer,
                sheet_name="Pagos realizados",
                index=False
            )

        df_detalle.to_excel(
            writer,
            sheet_name="Historial detallado",
            index=False
        )

    buffer.seek(0)

    st.download_button(
        label="Descargar historial en Excel",
        data=buffer,
        file_name=(
            f"historial_lavado_motos_"
            f"{fecha_inicio_texto}_a_{fecha_fin_texto}.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
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
    in ["Inicio", "Cierre", "Historial"]
):
    st.session_state.vista = "Registrar"
    st.rerun()


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
    if rol_actual not in ["admin", "socio"]:
        st.session_state.vista = "Registrar"
        st.rerun()

    mostrar_cierre_del_dia()


elif vista == "Historial":
    # Ya no existe como vista separada.
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