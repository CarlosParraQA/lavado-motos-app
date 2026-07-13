import streamlit as st
import pandas as pd

from datetime import datetime
from zoneinfo import ZoneInfo

from database import crear_tabla, obtener_lavados
from auth import login
from navbar import aplicar_estilos, navbar
from utils import formato_pesos

from views.Registrar_Lavada import mostrar_registrar_lavada
from views.Lavadas_Del_Dia import mostrar_lavadas_del_dia
from views.Cierre_Del_Dia import mostrar_cierre_del_dia
from views.Historial_General import mostrar_historial_general


# =========================================================
# CONFIGURACIÓN DE LA APLICACIÓN
# =========================================================

st.set_page_config(
    page_title="Moto Space Wash",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# PREPARACIÓN DE DATOS
# =========================================================

def preparar_dataframe_lavados(df):
    """
    Normaliza las columnas de lavados para evitar errores cuando
    existen valores vacíos o columnas faltantes en la base de datos.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

    columnas_por_defecto = {
        "id": 0,
        "fecha": "",
        "hora": "",
        "gamusero": "Sin asignar",
        "placa": "",
        "nombre_cliente": "",
        "telefono_cliente": "",
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
        "placa": "",
        "nombre_cliente": "",
        "telefono_cliente": "",
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

    df["coin"] = df["coin"].fillna(False).astype(bool)

    return df


# =========================================================
# INICIO SIN REGISTROS
# =========================================================

def mostrar_inicio_sin_registros():
    st.info(
        "Todavía no hay lavadas registradas. Cuando se registre el "
        "primer servicio, aquí aparecerá el resumen de la operación."
    )

    st.divider()

    st.markdown("### ¿Qué puedes hacer desde este sistema?")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("#### 🏍️ Registrar servicios")
            st.write(
                "Registra las lavadas realizadas, la placa, el cliente, "
                "el valor, el método de pago y la entrega de coin."
            )

    with col2:
        with st.container(border=True):
            st.markdown("#### 💰 Control de pagos")
            st.write(
                "Calcula automáticamente el pago del personal y la "
                "ganancia correspondiente al negocio."
            )

    with col3:
        with st.container(border=True):
            st.markdown("#### 📋 Seguimiento general")
            st.write(
                "Consulta las lavadas del día, los pagos pendientes, "
                "el historial general y los reportes disponibles."
            )


# =========================================================
# RESUMEN DE PAGOS DEL DÍA
# =========================================================

def mostrar_resumen_pagos(df_hoy):
    metodo_pago = (
        df_hoy["metodo_pago"]
        .fillna("")
        .str.strip()
        .str.lower()
    )

    total_efectivo = int(
        df_hoy.loc[
            metodo_pago == "efectivo",
            "valor_lavada"
        ].sum()
    )

    total_nequi = int(
        df_hoy.loc[
            metodo_pago == "nequi",
            "valor_lavada"
        ].sum()
    )

    total_servicios = len(df_hoy)

    col_efectivo, col_nequi, col_estado = st.columns(3)

    with col_efectivo:
        with st.container(border=True):
            st.markdown("#### 💵 Efectivo")
            st.markdown(f"### {formato_pesos(total_efectivo)}")

    with col_nequi:
        with st.container(border=True):
            st.markdown("#### 📱 Nequi")
            st.markdown(f"### {formato_pesos(total_nequi)}")

    with col_estado:
        with st.container(border=True):
            st.markdown("#### 🧾 Estado operativo")

            if total_servicios == 1:
                texto_servicios = "1 servicio registrado"
            else:
                texto_servicios = (
                    f"{total_servicios} servicios registrados"
                )

            st.markdown(f"### {texto_servicios}")


# =========================================================
# ÚLTIMOS SERVICIOS
# =========================================================

def mostrar_ultimos_servicios(df_hoy):
    st.markdown("### Últimos servicios registrados")

    columnas_mostrar = [
        "hora",
        "placa",
        "gamusero",
        "nombre_cliente",
        "valor_lavada",
        "metodo_pago",
        "coin"
    ]

    columnas_existentes = [
        columna
        for columna in columnas_mostrar
        if columna in df_hoy.columns
    ]

    if "id" in df_hoy.columns:
        ultimos = (
            df_hoy
            .sort_values(
                by="id",
                ascending=False
            )
            .head(8)
            [columnas_existentes]
            .copy()
        )
    else:
        ultimos = (
            df_hoy[columnas_existentes]
            .tail(8)
            .iloc[::-1]
            .copy()
        )

    if "valor_lavada" in ultimos.columns:
        ultimos["valor_lavada"] = (
            ultimos["valor_lavada"]
            .apply(formato_pesos)
        )

    if "coin" in ultimos.columns:
        ultimos["coin"] = ultimos["coin"].apply(
            lambda valor: "Sí" if valor else "No"
        )

    ultimos = ultimos.rename(
        columns={
            "hora": "Hora",
            "placa": "Placa",
            "gamusero": "Colaborador",
            "nombre_cliente": "Cliente",
            "valor_lavada": "Valor",
            "metodo_pago": "Método de pago",
            "coin": "Coin"
        }
    )

    st.dataframe(
        ultimos,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# RESUMEN POR COLABORADOR
# =========================================================

def mostrar_resumen_colaboradores(df_hoy):
    st.markdown("### Resumen por colaborador")

    resumen = (
        df_hoy
        .groupby(
            "gamusero",
            dropna=False
        )
        .agg(
            servicios=("id", "count"),
            total_realizado=("valor_lavada", "sum"),
            pago_estimado=("pago_gamusero", "sum")
        )
        .reset_index()
    )

    resumen["total_realizado"] = (
        resumen["total_realizado"]
        .apply(formato_pesos)
    )

    resumen["pago_estimado"] = (
        resumen["pago_estimado"]
        .apply(formato_pesos)
    )

    resumen = resumen.rename(
        columns={
            "gamusero": "Colaborador",
            "servicios": "Servicios",
            "total_realizado": "Total realizado",
            "pago_estimado": "Pago estimado"
        }
    )

    st.dataframe(
        resumen,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# PANEL PRINCIPAL
# =========================================================

def mostrar_inicio():
    fecha_hoy = datetime.now(
        ZoneInfo("America/Bogota")
    ).date()

    fecha_hoy_texto = fecha_hoy.strftime("%Y-%m-%d")
    fecha_hoy_visual = fecha_hoy.strftime("%d/%m/%Y")

    st.markdown("## Panel de control")

    st.caption(
        f"Resumen general de la operación del día - "
        f"{fecha_hoy_visual}"
    )

    try:
        df = obtener_lavados()

    except Exception as error:
        st.error(
            "No se pudo cargar la información de las lavadas."
        )
        st.exception(error)
        return

    if df is None or df.empty:
        mostrar_inicio_sin_registros()
        return

    df = preparar_dataframe_lavados(df)

    df_hoy = df.loc[
        df["fecha"] == fecha_hoy_texto
    ].copy()

    st.divider()

    if df_hoy.empty:
        st.warning(
            "Aún no hay servicios registrados para el día de hoy."
        )

        with st.container(border=True):
            st.markdown("### Estado del día")

            st.write(
                "La operación de hoy todavía no tiene lavadas "
                "registradas. Cuando se registre el primer servicio, "
                "aquí aparecerán los totales, los últimos servicios "
                "y el resumen por colaborador."
            )

        return

    mostrar_resumen_pagos(df_hoy)

    st.divider()

    col_izquierda, col_derecha = st.columns(
        [1.35, 1]
    )

    with col_izquierda:
        mostrar_ultimos_servicios(df_hoy)

    with col_derecha:
        mostrar_resumen_colaboradores(df_hoy)


# =========================================================
# INICIALIZACIÓN
# =========================================================

login()

aplicar_estilos()

crear_tabla()

navbar()


# =========================================================
# OBTENER USUARIO, ROL Y VISTA
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
# VALIDACIÓN DEL ROL
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
# PROTEGER LA VISTA INICIO
# =========================================================

if (
    rol_actual == "operador"
    and st.session_state.get("vista") == "Inicio"
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

    st.divider()

    mostrar_historial_general()


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
