import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Moto Space Wash",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from database import crear_tabla, obtener_lavados
from auth import login
from navbar import aplicar_estilos, navbar
from utils import formato_pesos

from views.Registrar_Lavada import mostrar_registrar_lavada
from views.Lavadas_Del_Dia import mostrar_lavadas_del_dia
from views.Cierre_Del_Dia import mostrar_cierre_del_dia
from views.Historial_General import mostrar_historial_general


def preparar_dataframe_lavados(df):
    """
    Normaliza columnas para evitar errores si algún campo viene vacío
    o si alguna columna aún no existe en Supabase.
    """

    if df.empty:
        return df

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

    df["fecha"] = df["fecha"].astype(str)
    df["hora"] = df["hora"].astype(str)
    df["gamusero"] = df["gamusero"].fillna("Sin asignar").astype(str)
    df["placa"] = df["placa"].fillna("").astype(str)
    df["nombre_cliente"] = df["nombre_cliente"].fillna("").astype(str)
    df["telefono_cliente"] = df["telefono_cliente"].fillna("").astype(str)
    df["metodo_pago"] = df["metodo_pago"].fillna("Efectivo").astype(str)
    df["observaciones"] = df["observaciones"].fillna("").astype(str)
    df["coin"] = df["coin"].fillna(False).astype(bool)

    columnas_numericas = [
        "valor_lavada",
        "pago_gamusero",
        "ganancia_negocio"
    ]

    for columna in columnas_numericas:
        df[columna] = pd.to_numeric(
            df[columna],
            errors="coerce"
        ).fillna(0).astype(int)

    return df


def mostrar_inicio_sin_registros():
    st.info(
        "Todavía no hay lavadas registradas. Cuando se registre el primer servicio, "
        "aquí aparecerá el resumen de la operación."
    )

    st.divider()

    st.markdown("### ¿Qué puedes hacer desde este sistema?")

    col1, col2, col3 = st.columns(3)

    with col1:
        with st.container(border=True):
            st.markdown("#### 🏍️ Registrar servicios")
            st.write(
                "Registra lavadas por colaborador, placa, cliente, valor, método de pago y entrega de coin."
            )

    with col2:
        with st.container(border=True):
            st.markdown("#### 💰 Control de pagos")
            st.write(
                "Calcula automáticamente el pago del personal y la ganancia del negocio."
            )

    with col3:
        with st.container(border=True):
            st.markdown("#### 📊 Seguimiento general")
            st.write(
                "Consulta las lavadas del día, pagos pendientes, historial general y exporta reportes en Excel."
            )


def mostrar_inicio():
    fecha_hoy = datetime.now(ZoneInfo("America/Bogota")).date()
    fecha_hoy_texto = fecha_hoy.strftime("%Y-%m-%d")
    fecha_hoy_visual = fecha_hoy.strftime("%d/%m/%Y")

    st.markdown("## Panel de control")
    st.caption(f"Resumen general de la operación del día - {fecha_hoy_visual}")

    try:
        df = obtener_lavados()
    except Exception as error:
        st.error("No se pudo cargar la información de lavadas.")
        st.exception(error)
        return

    if df.empty:
        mostrar_inicio_sin_registros()
        return

    df = preparar_dataframe_lavados(df)

    df_hoy = df[df["fecha"] == fecha_hoy_texto].copy()

    total_servicios = len(df_hoy)
    total_vendido = int(df_hoy["valor_lavada"].sum()) if not df_hoy.empty else 0
    total_pago_gamusero = int(df_hoy["pago_gamusero"].sum()) if not df_hoy.empty else 0
    total_ganancia = int(df_hoy["ganancia_negocio"].sum()) if not df_hoy.empty else 0
    total_coins = int(df_hoy["coin"].sum()) if not df_hoy.empty else 0

    if not df_hoy.empty:
        metodo_pago_normalizado = df_hoy["metodo_pago"].str.strip().str.lower()

        total_efectivo = int(
            df_hoy[metodo_pago_normalizado == "efectivo"]["valor_lavada"].sum()
        )

        total_nequi = int(
            df_hoy[metodo_pago_normalizado == "nequi"]["valor_lavada"].sum()
        )
    else:
        total_efectivo = 0
        total_nequi = 0

    # =========================
    # MÉTRICAS PRINCIPALES
    # =========================

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Servicios hoy", total_servicios)
    col2.metric("Total vendido", formato_pesos(total_vendido))
    col3.metric("Pago personal", formato_pesos(total_pago_gamusero))
    col4.metric("Ganancia negocio", formato_pesos(total_ganancia))
    col5.metric("Coins entregadas", total_coins)

    st.divider()

    # =========================
    # SI NO HAY REGISTROS HOY
    # =========================

    if df_hoy.empty:
        st.warning("Aún no hay servicios registrados para el día de hoy.")

        with st.container(border=True):
            st.markdown("### Estado del día")
            st.write(
                "La operación de hoy todavía no tiene lavadas registradas. "
                "Cuando se registre el primer servicio, aquí aparecerán los totales, "
                "los últimos servicios y el resumen por colaborador."
            )

        return

    # =========================
    # RESUMEN DE PAGO
    # =========================

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
                st.markdown("### 1 servicio registrado")
            else:
                st.markdown(f"### {total_servicios} servicios registrados")

    st.divider()

    # =========================
    # TABLAS DE RESUMEN
    # =========================

    col_izq, col_der = st.columns([1.35, 1])

    with col_izq:
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
            columna for columna in columnas_mostrar
            if columna in df_hoy.columns
        ]

        ultimos = df_hoy[columnas_existentes].head(8).copy()

        if "valor_lavada" in ultimos.columns:
            ultimos["valor_lavada"] = ultimos["valor_lavada"].apply(formato_pesos)

        if "coin" in ultimos.columns:
            ultimos["coin"] = ultimos["coin"].apply(
                lambda valor: "Sí" if valor else "No"
            )

        ultimos = ultimos.rename(columns={
            "hora": "Hora",
            "placa": "Placa",
            "gamusero": "Colaborador",
            "nombre_cliente": "Cliente",
            "valor_lavada": "Valor",
            "metodo_pago": "Método de pago",
            "coin": "Coin"
        })

        st.dataframe(
            ultimos,
            use_container_width=True,
            hide_index=True
        )

    with col_der:
        st.markdown("### Resumen por colaborador")

        resumen_colaborador = (
            df_hoy
            .groupby("gamusero")
            .agg(
                servicios=("id", "count"),
                total_realizado=("valor_lavada", "sum"),
                pago_estimado=("pago_gamusero", "sum")
            )
            .reset_index()
        )

        resumen_colaborador["total_realizado"] = resumen_colaborador[
            "total_realizado"
        ].apply(formato_pesos)

        resumen_colaborador["pago_estimado"] = resumen_colaborador[
            "pago_estimado"
        ].apply(formato_pesos)

        resumen_colaborador = resumen_colaborador.rename(columns={
            "gamusero": "Colaborador",
            "servicios": "Servicios",
            "total_realizado": "Total realizado",
            "pago_estimado": "Pago estimado"
        })

        st.dataframe(
            resumen_colaborador,
            use_container_width=True,
            hide_index=True
        )


def mostrar_historial_en_inicio():
    st.divider()
    mostrar_historial_general()


# =========================
# INICIO DE LA APP
# =========================

login()

aplicar_estilos()
navbar()

crear_tabla()

vista = st.session_state.get("vista", "Inicio")

if vista == "Inicio":
    mostrar_inicio()
    mostrar_historial_en_inicio()

elif vista == "Registrar":
    mostrar_registrar_lavada()

elif vista == "Lavadas":
    mostrar_lavadas_del_dia()

elif vista == "Cierre":
    mostrar_cierre_del_dia()

elif vista == "Historial":
    st.session_state.vista = "Inicio"
    st.rerun()