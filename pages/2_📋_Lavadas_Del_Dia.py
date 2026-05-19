import streamlit as st
import pandas as pd
from datetime import datetime
from database import obtener_lavados, eliminar_registro
from utils import formato_pesos
from auth import login, logout

login()
logout()

# =========================
# ENCABEZADO
# =========================

fecha_hoy = datetime.now().strftime("%Y-%m-%d")

st.header(f"Lavadas registradas: {fecha_hoy}")

df = obtener_lavados()

df_hoy = df[df["fecha"] == fecha_hoy] if not df.empty else pd.DataFrame()

# =========================
# VALIDACIÓN SIN REGISTROS
# =========================

if df_hoy.empty:
    st.warning("Todavía no hay lavadas registradas hoy. 😥")

else:
    # =========================
    # FILTRO POR GAMUSERO
    # =========================

    gamuseros = ["Todos"] + sorted(df_hoy["gamusero"].unique().tolist())

    filtro_gamusero = st.selectbox(
        "Filtrar por personal",
        gamuseros
    )

    if filtro_gamusero != "Todos":
        df_hoy = df_hoy[df_hoy["gamusero"] == filtro_gamusero]

    # =========================
    # MÉTRICAS
    # =========================

    total_lavado = df_hoy["valor_lavada"].sum()
    total_pago = df_hoy["pago_gamusero"].sum()
    total_negocio = df_hoy["ganancia_negocio"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total lavado del día",
        formato_pesos(total_lavado)
    )

    col2.metric(
        "40% gamuseros",
        formato_pesos(total_pago)
    )

    col3.metric(
        "60% negocio",
        formato_pesos(total_negocio)
    )

    st.divider()

    # =========================
    # TABLA DE LAVADAS
    # =========================

    st.subheader("Detalle de lavadas")

    df_mostrar = df_hoy.copy()

    # Formatear valores monetarios
    df_mostrar["valor_lavada"] = df_mostrar["valor_lavada"].apply(formato_pesos)
    df_mostrar["pago_gamusero"] = df_mostrar["pago_gamusero"].apply(formato_pesos)
    df_mostrar["ganancia_negocio"] = df_mostrar["ganancia_negocio"].apply(formato_pesos)

    # Seleccionar columnas a mostrar
    df_mostrar = df_mostrar[
        [
            "id",
            "fecha",
            "hora",
            "gamusero",
            "placa",
            "valor_lavada",
            "pago_gamusero",
            "ganancia_negocio",
            "observaciones"
        ]
    ]

    # Cambiar nombres de columnas
    df_mostrar = df_mostrar.rename(columns={
        "id": "Lavada #",
        "fecha": "Fecha",
        "hora": "Hora",
        "gamusero": "Personal",
        "placa": "Placa",
        "valor_lavada": "Valor lavada",
        "pago_gamusero": "40% personal",
        "ganancia_negocio": "60% negocio",
        "observaciones": "Observaciones"
    })

    # Mostrar tabla con configuración visual
    st.dataframe(
        df_mostrar,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Lavada #": st.column_config.NumberColumn(
                "Lavada #",
                help="Identificador del registro",
                width="small"
            ),
            "Fecha": st.column_config.TextColumn(
                "Fecha",
                width="medium"
            ),
            "Hora": st.column_config.TextColumn(
                "Hora",
                width="small"
            ),
            "Personal": st.column_config.TextColumn(
                "Personal",
                width="medium"
            ),
            "Placa": st.column_config.TextColumn(
                "Placa",
                width="small"
            ),
            "Valor lavada": st.column_config.TextColumn(
                "Valor lavada",
                width="medium"
            ),
            "40% personal": st.column_config.TextColumn(
                "40% personal",
                width="medium"
            ),
            "60% negocio": st.column_config.TextColumn(
                "60% negocio",
                width="medium"
            ),
            "Observaciones": st.column_config.TextColumn(
                "Observaciones",
                width="large"
            ),
        }
    )

    st.divider()

    # =========================
    # ELIMINAR REGISTRO
    # =========================

    st.subheader("Eliminar registro")

    st.info("Para eliminar una lavada, copia el número de la columna Lavada # y escríbelo abajo.")

    id_eliminar = st.number_input(
        "Lavada a eliminar",
        min_value=1,
        step=1
    )

    if st.button("Eliminar registro seleccionado"):
        if id_eliminar in df_hoy["id"].values:
            eliminar_registro(int(id_eliminar))
            st.success("Registro eliminado correctamente.")
            st.rerun()
        else:
            st.error("Ese registro no existe en los registros mostrados.")