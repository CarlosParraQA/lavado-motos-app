import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from database import obtener_lavados, supabase
from utils import formato_pesos
from io import BytesIO

def obtener_pagos_empleados(fecha_inicio, fecha_fin):
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

def mostrar_historial_general():
    st.header("Historial General del día")

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
    ].copy()

    if "coin" not in df_filtrado.columns:
        df_filtrado["coin"] = False

    df_filtrado["coin"] = df_filtrado["coin"].fillna(False).astype(bool)

    if df_filtrado.empty:
        st.warning("No hay registros en ese rango de fechas.")
        return

 # =========================
    # RESUMEN FINANCIERO
    # =========================

    total_lavado = df_filtrado["valor_lavada"].sum()

    df_pagos = obtener_pagos_empleados(
        fecha_inicio_texto,
        fecha_fin_texto
    )

    if df_pagos.empty:
        total_pagado_empleados = 0
        total_pagado_encargado = 0
        total_pagado_general = 0
    else:
        total_pagado_empleados = df_pagos[
            df_pagos["rol"].str.lower() == "gamusero"
        ]["valor_pagar"].sum()

        total_pagado_encargado = df_pagos[
            df_pagos["rol"].str.lower() == "encargado"
        ]["valor_pagar"].sum()

        total_pagado_general = df_pagos["valor_pagar"].sum()

    ganancia_final_negocio = total_lavado - total_pagado_general

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total vendido",
        formato_pesos(total_lavado)
    )

    col2.metric(
        "Pagado a empleados",
        formato_pesos(total_pagado_empleados)
    )

    col3.metric(
        "Pagado encargado",
        formato_pesos(total_pagado_encargado)
    )

    col4.metric(
        "Ganancia final negocio",
        formato_pesos(ganancia_final_negocio)
    )

    st.divider()

    # =========================
    # DETALLE DE PAGOS REALIZADOS
    # =========================

    st.subheader("Pagos realizados")

    if df_pagos.empty:
        st.info("No hay pagos registrados en este rango de fechas.")
    else:
        df_pagos_mostrar = df_pagos.copy()

        df_pagos_mostrar["valor_pagar"] = df_pagos_mostrar["valor_pagar"].apply(formato_pesos)
        df_pagos_mostrar["total_realizado"] = df_pagos_mostrar["total_realizado"].apply(formato_pesos)

        columnas_pagos = [
            "fecha",
            "empleado",
            "rol",
            "cantidad_servicios",
            "total_realizado",
            "valor_pagar",
            "pagado_por"
        ]

        df_pagos_mostrar = df_pagos_mostrar[columnas_pagos]

        df_pagos_mostrar = df_pagos_mostrar.rename(columns={
            "fecha": "Fecha",
            "empleado": "Empleado",
            "rol": "Rol",
            "cantidad_servicios": "Servicios",
            "total_realizado": "Total realizado",
            "valor_pagar": "Valor pagado",
            "pagado_por": "Pagado por",
        })

        st.dataframe(
            df_pagos_mostrar,
            use_container_width=True,
            hide_index=True
        )

    resumen_financiero_df = pd.DataFrame([{
        "Total vendido": total_lavado,
        "Pagado a empleados": total_pagado_empleados,
        "Pagado encargado": total_pagado_encargado,
        "Total pagado": total_pagado_general,
        "Ganancia final negocio": ganancia_final_negocio
    }])

    resumen_financiero_mostrar = resumen_financiero_df.copy()

    for columna in resumen_financiero_mostrar.columns:
        resumen_financiero_mostrar[columna] = resumen_financiero_mostrar[columna].apply(formato_pesos)

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
            "observaciones",
            "coin"
        ]
    ]

    # Renombrar columnas
    df_detalle = df_detalle.rename(columns={
        "id": "Lavada #",
        "fecha": "Fecha",
        "hora": "Hora",
        "gamusero": "Nombre del Trabajador",
        "placa": "Placa",
        "valor_lavada": "Valor",
        "pago_gamusero": "40% correspondiente al trabajador",
        "ganancia_negocio": "60% correspondiente al negocio",
        "observaciones": "Observaciones",
        "coin": "Coin"
    })

    df_detalle["Coin"] = df_detalle["Coin"].apply(lambda x: "Sí" if x else "No")

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
            "Nombre del Trabajador": st.column_config.TextColumn(
                "Nombre del Trabajador",
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
            "40% correspondiente al trabajador": st.column_config.TextColumn(
                "40% correspondiente al trabajador",
                width="medium"
            ),
            "60% correspondiente al negocio": st.column_config.TextColumn(
                "60% correspondiente al negocio",
                width="medium"
            ),
            "Observaciones": st.column_config.TextColumn(
                "Observaciones",
                width="medium"
            ),
            "Coin": st.column_config.TextColumn(
                "Coin",
                width="small"
            )
        }
    )

    st.divider()

    # =========================
    # EXPORTAR A EXCEL
    # =========================

    buffer = BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        resumen_financiero_mostrar.to_excel(
            writer,
            sheet_name="Resumen financiero",
            index=False
        )

        if not df_pagos.empty:
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
        file_name=f"historial_lavado_motos_{fecha_inicio_texto}_a_{fecha_fin_texto}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )