import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from database import obtener_lavados
from utils import formato_pesos
from io import BytesIO


def mostrar_historial_general():
    st.header("Historial general de lavadas")

    # Obtener registros
    df = obtener_lavados()

    if df.empty:
        st.warning("No hay registros guardados.")
        return

    # =========================
    # FILTRO POR FECHAS
    # =========================

    fecha_colombia = datetime.now(ZoneInfo("America/Bogota")).date()

    col1, col2 = st.columns(2)

    with col1:
        fecha_inicio = st.date_input(
            "Fecha inicial",
            value=fecha_colombia,
            key="historial_fecha_inicio"
        )

    with col2:
        fecha_fin = st.date_input(
            "Fecha final",
            value=fecha_colombia,
            key="historial_fecha_fin"
        )

    fecha_inicio_texto = fecha_inicio.strftime("%Y-%m-%d")
    fecha_fin_texto = fecha_fin.strftime("%Y-%m-%d")

    # Filtrar por rango de fechas
    df_filtrado = df[
        (df["fecha"] >= fecha_inicio_texto) &
        (df["fecha"] <= fecha_fin_texto)
    ]

    if df_filtrado.empty:
        st.warning("No hay registros en ese rango de fechas.")
        return

    # =========================
    # MÉTRICAS GENERALES
    # =========================

    total_lavado = df_filtrado["valor_lavada"].sum()
    total_pago = df_filtrado["pago_gamusero"].sum()
    total_negocio = df_filtrado["ganancia_negocio"].sum()

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total lavado",
        formato_pesos(total_lavado)
    )

    col2.metric(
        "Total 40% personal",
        formato_pesos(total_pago)
    )

    col3.metric(
        "Total 60% negocio",
        formato_pesos(total_negocio)
    )

    st.divider()

    # =========================
    # RESUMEN POR PERSONAL
    # =========================

    st.subheader("Resumen por personal")

    resumen = df_filtrado.groupby("gamusero").agg(
        cantidad_lavadas=("id", "count"),
        total_lavado=("valor_lavada", "sum"),
        pago_40_personal=("pago_gamusero", "sum"),
        ganancia_60_negocio=("ganancia_negocio", "sum")
    ).reset_index()

    resumen_mostrar = resumen.copy()

    resumen_mostrar["total_lavado"] = resumen_mostrar["total_lavado"].apply(formato_pesos)
    resumen_mostrar["pago_40_personal"] = resumen_mostrar["pago_40_personal"].apply(formato_pesos)
    resumen_mostrar["ganancia_60_negocio"] = resumen_mostrar["ganancia_60_negocio"].apply(formato_pesos)

    resumen_mostrar = resumen_mostrar.rename(columns={
        "gamusero": "Personal",
        "cantidad_lavadas": "Lavadas",
        "total_lavado": "Total lavado",
        "pago_40_personal": "40%",
        "ganancia_60_negocio": "60%"
    })

    st.dataframe(
        resumen_mostrar,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Personal": st.column_config.TextColumn(
                "Personal",
                width="medium"
            ),
            "Lavadas": st.column_config.NumberColumn(
                "Lavadas",
                width="small"
            ),
            "Total lavado": st.column_config.TextColumn(
                "Total lavado",
                width="small"
            ),
            "40%": st.column_config.TextColumn(
                "40%",
                width="small"
            ),
            "60%": st.column_config.TextColumn(
                "60%",
                width="small"
            ),
        }
    )

    st.divider()

    # =========================
    # HISTORIAL DETALLADO
    # =========================

    st.subheader("Detalle de lavadas")

    df_detalle = df_filtrado.copy()

    # Formatear valores monetarios
    df_detalle["valor_lavada"] = df_detalle["valor_lavada"].apply(formato_pesos)
    df_detalle["pago_gamusero"] = df_detalle["pago_gamusero"].apply(formato_pesos)
    df_detalle["ganancia_negocio"] = df_detalle["ganancia_negocio"].apply(formato_pesos)

    # Seleccionar columnas
    df_detalle = df_detalle[
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

    # Renombrar columnas
    df_detalle = df_detalle.rename(columns={
        "id": "Lavada #",
        "fecha": "Fecha",
        "hora": "Hora",
        "gamusero": "Personal",
        "placa": "Placa",
        "valor_lavada": "Valor",
        "pago_gamusero": "40%",
        "ganancia_negocio": "60%",
        "observaciones": "Observaciones"
    })

    st.dataframe(
        df_detalle,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Lavada #": st.column_config.NumberColumn(
                "Lavada #",
                width="small"
            ),
            "Fecha": st.column_config.TextColumn(
                "Fecha",
                width="small"
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
            "Valor": st.column_config.TextColumn(
                "Valor",
                width="small"
            ),
            "40%": st.column_config.TextColumn(
                "40%",
                width="small"
            ),
            "60%": st.column_config.TextColumn(
                "60%",
                width="small"
            ),
            "Observaciones": st.column_config.TextColumn(
                "Observaciones",
                width="large"
            ),
        }
    )

    st.divider()

    # =========================
    # EXPORTAR A EXCEL
    # =========================

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        resumen_mostrar.to_excel(
            writer,
            sheet_name="Resumen por personal",
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
        file_name=f"historial_lavado_motos_{fecha_inicio_texto}_a_{fecha_fin_texto}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )