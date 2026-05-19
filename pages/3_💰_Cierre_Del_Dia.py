import streamlit as st
import pandas as pd
from datetime import date
from database import obtener_lavados, eliminar_registro
from utils import formato_pesos
from io import BytesIO
from auth import login, logout

login()
logout()

st.header("Cierre del día")

# Obtener registros de la base de datos
df = obtener_lavados()

if df.empty:
    st.warning("No hay registros para calcular cierre.")

else:
    # =========================
    # SELECCIÓN DE FECHA
    # =========================

    fecha_seleccionada = st.date_input(
        "Selecciona la fecha del cierre",
        value=date.today()
    )

    fecha_texto = fecha_seleccionada.strftime("%Y-%m-%d")

    # Filtrar registros por fecha seleccionada
    df_dia = df[df["fecha"] == fecha_texto]

    if df_dia.empty:
        st.warning("No hay lavadas registradas para esta fecha.")

    else:
        # =========================
        # RESUMEN AGRUPADO
        # =========================

        resumen = df_dia.groupby("gamusero").agg(
            cantidad_lavadas=("id", "count"),
            total_lavado=("valor_lavada", "sum"),
            pago_40_gamusero=("pago_gamusero", "sum"),
            ganancia_60_negocio=("ganancia_negocio", "sum")
        ).reset_index()

        # =========================
        # TOTALES GENERALES
        # =========================

        total_general = df_dia["valor_lavada"].sum()
        total_pagar = df_dia["pago_gamusero"].sum()
        total_negocio = df_dia["ganancia_negocio"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "Total vendido del día",
            formato_pesos(total_general)
        )

        col2.metric(
            "Total a pagar 40%",
            formato_pesos(total_pagar)
        )

        col3.metric(
            "Total negocio 60%",
            formato_pesos(total_negocio)
        )

        st.divider()

        # =========================
        # TABLA PAGO POR GAMUSERO
        # =========================

        st.subheader("Resumen correspondiente a cada persona y Negocio")

        resumen_mostrar = resumen.copy()

        # Formatear valores monetarios
        resumen_mostrar["total_lavado"] = resumen_mostrar["total_lavado"].apply(formato_pesos)
        resumen_mostrar["pago_40_gamusero"] = resumen_mostrar["pago_40_gamusero"].apply(formato_pesos)
        resumen_mostrar["ganancia_60_negocio"] = resumen_mostrar["ganancia_60_negocio"].apply(formato_pesos)

        # Renombrar columnas para mostrar en pantalla
        resumen_mostrar = resumen_mostrar.rename(columns={
            "gamusero": "Personal",
            "cantidad_lavadas": "Cantidad de lavadas",
            "total_lavado": "Total lavado",
            "pago_40_gamusero": "40% personal",
            "ganancia_60_negocio": "60% negocio"
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
                "Cantidad de lavadas": st.column_config.NumberColumn(
                    "Cantidad de lavadas",
                    width="medium"
                ),
                "Total lavado": st.column_config.TextColumn(
                    "Total lavado",
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
            }
        )

        st.divider()

        # =========================
        # DETALLE DE LAVADAS DEL DÍA
        # =========================

        st.subheader("Detalle de lavadas del día")

        df_detalle = df_dia.copy()

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
            "valor_lavada": "Valor lavada",
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
        # Solo admin puede eliminar
        # =========================

        usuario_actual = st.session_state.get("usuario", "").strip().lower()

        if usuario_actual == "admin":
            st.subheader("Eliminar registro del cierre")

            st.info("Para eliminar una lavada, copia el número de la columna Lavada # y escríbelo abajo.")

            id_eliminar = st.number_input(
                "Lavada # a eliminar",
                min_value=1,
                step=1,
                key="eliminar_cierre"
            )

            if st.button("Eliminar registro seleccionado", key="btn_eliminar_cierre"):
                if id_eliminar in df_dia["id"].values:
                    eliminar_registro(int(id_eliminar))
                    st.success("Registro eliminado correctamente.")
                    st.rerun()
                else:
                    st.error("Ese registro no existe en las lavadas de esta fecha.")

        else:
            st.info("Solo el usuario administrador puede eliminar registros.")

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
                sheet_name="Lavadas del dia",
                index=False
            )

        buffer.seek(0)

        st.download_button(
            label="Descargar cierre en Excel",
            data=buffer,
            file_name=f"cierre_lavado_motos_{fecha_texto}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )