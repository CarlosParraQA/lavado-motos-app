import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from database import obtener_lavados, eliminar_registro, actualizar_nombre_gamusero, actualizar_coin_lavada, actualizar_metodo_pago_lavada
from utils import formato_pesos


def mostrar_lavadas_del_dia():
    # =========================
    # ENCABEZADO
    # =========================

    fecha_hoy = datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d")

    st.header(f"Lavadas registradas: {fecha_hoy}")

    df = obtener_lavados()

    df_hoy = df[df["fecha"] == fecha_hoy] if not df.empty else pd.DataFrame()

    # =========================
    # VALIDACIÓN SIN REGISTROS
    # =========================

    if df_hoy.empty:
        st.warning("Todavía no hay lavadas registradas hoy. 😥")
        return

    # =========================
    # FILTRO POR PERSONAL
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
    st.caption("Selecciona una fila para modificar el nombre o eliminar el registro.")

    df_mostrar = df_hoy.copy()

    if "coin" not in df_mostrar.columns:
        df_mostrar["coin"] = False

    if "metodo_pago" not in df_mostrar.columns:
        df_mostrar["metodo_pago"] = "Efectivo"

    df_mostrar["coin"] = df_mostrar["coin"].fillna(False).astype(bool)
    df_mostrar["metodo_pago"] = df_mostrar["metodo_pago"].fillna("Efectivo")

    # Formatear valores monetarios
    df_mostrar["valor_lavada"] = df_mostrar["valor_lavada"].apply(formato_pesos)
    df_mostrar["pago_gamusero"] = df_mostrar["pago_gamusero"].apply(formato_pesos)
    df_mostrar["ganancia_negocio"] = df_mostrar["ganancia_negocio"].apply(formato_pesos)

    # Seleccionar columnas completas
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
            "metodo_pago",
            "coin",
            "observaciones"
        ]
    ]

    # Renombrar columnas
    df_mostrar = df_mostrar.rename(columns={
        "id": "Lavada #",
        "fecha": "Fecha",
        "hora": "Hora",
        "gamusero": "Personal",
        "placa": "Placa",
        "valor_lavada": "Valor",
        "pago_gamusero": "40%",
        "ganancia_negocio": "60%",
        "observaciones": "Observaciones",
        "coin": "Coin",
        "metodo_pago": "Método de pago"
    })

    # Tabla compacta para evitar scroll horizontal
    df_tabla = df_mostrar[
        [
            "Lavada #",
            "Hora",
            "Personal",
            "Placa",
            "Valor",
            "Coin",
            "Método de pago"
        ]
    ]

    # =========================
    # POPUP / MODAL
    # =========================

    @st.dialog("Modificar lavada")
    def abrir_popup_lavada(registro):
        id_lavada = int(registro["Lavada #"])
        nombre_actual = registro["Personal"]
        coin_actual = bool(registro["Coin"])
        metodo_pago_actual = registro.get("Método de pago", "Efectivo")

        if metodo_pago_actual not in ["Efectivo", "Nequi"]:
            metodo_pago_actual = "Efectivo"

        st.write(f"**Lavada #:** {id_lavada}")
        st.write(f"**Fecha:** {registro['Fecha']}")
        st.write(f"**Hora:** {registro['Hora']}")
        st.write(f"**Placa:** {registro['Placa']}")
        st.write(f"**Valor:** {registro['Valor']}")
        st.write(f"**40% personal:** {registro['40%']}")
        st.write(f"**60% negocio:** {registro['60%']}")

        if registro["Observaciones"]:
            st.write(f"**Observaciones:** {registro['Observaciones']}")

        nuevo_nombre = st.text_input(
            "Nombre del personal",
            value=nombre_actual
        )
        nuevo_coin = st.checkbox(
            "¿Se le dio coin?",
            value=coin_actual
        )
        nuevo_metodo_pago = st.selectbox(
            "Método de pago",
            ["Efectivo", "Nequi"],
            index=0 if metodo_pago_actual == "Efectivo" else 1
        )
        col_guardar, col_eliminar = st.columns(2)

        with col_guardar:
            if st.button("Guardar cambios", use_container_width=True):
                if not nuevo_nombre.strip():
                    st.error("El nombre no puede estar vacío.")
                else:
                    actualizar_nombre_gamusero(
                        id_registro=id_lavada,
                        nuevo_nombre=nuevo_nombre.strip().title()
                    )

                    actualizar_coin_lavada(
                        id_registro=id_lavada,
                        coin=nuevo_coin
                    )
                    actualizar_metodo_pago_lavada(
                        id_registro=id_lavada,
                        metodo_pago=nuevo_metodo_pago
                    )

                    st.success("Lavada actualizada correctamente.")
                    st.rerun()

        with col_eliminar:
            usuario_actual = st.session_state.get("usuario", "").strip().lower()

            if usuario_actual == "admin":
                if st.button("Eliminar lavada", use_container_width=True):
                    eliminar_registro(id_lavada)
                    st.success("Registro eliminado correctamente.")
                    st.rerun()
            else:
                st.info("Solo admin puede eliminar.")

    # =========================
    # TABLA SELECCIONABLE
    # =========================

    evento_tabla = st.dataframe(
        df_tabla,
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={
            "Lavada #": st.column_config.NumberColumn(
                "Lavada #",
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
            "Coin": st.column_config.CheckboxColumn(
                "C",
                width="small",
            ), 
            "Método de pago": st.column_config.TextColumn(
                "Método de pago",
                width="small"
            ),
        }
    )

    # Abrir popup cuando se seleccione una fila
    filas_seleccionadas = evento_tabla.selection.rows

    if filas_seleccionadas:
        indice_fila = filas_seleccionadas[0]

        id_seleccionado = df_tabla.iloc[indice_fila]["Lavada #"]

        registro_seleccionado = df_mostrar[
            df_mostrar["Lavada #"] == id_seleccionado
        ].iloc[0]

        abrir_popup_lavada(registro_seleccionado)