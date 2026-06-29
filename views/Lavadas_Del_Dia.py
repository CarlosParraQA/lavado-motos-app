import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from html import escape

from database import (
    obtener_lavados,
    eliminar_registro,
    actualizar_nombre_gamusero,
    actualizar_coin_lavada,
    actualizar_metodo_pago_lavada,
    actualizar_valor_lavada
)

from utils import formato_pesos


def aplicar_estilos_lavadas():
    st.markdown(
        """
        <style>
            /* =========================
               TABLA LAVADAS - ESTILO FORMAL
            ========================= */

            .tabla-header-lavadas {
                background-color: #111827;
                border-top: 1px solid #374151;
                border-bottom: 1px solid #374151;
                padding: 10px 8px;
                font-size: 12px;
                font-weight: 800;
                color: #9ca3af;
                min-height: 42px;
                display: flex;
                align-items: center;
                text-transform: uppercase;
                letter-spacing: 0.04em;
            }

            .texto-tabla-lavadas {
                background-color: transparent;
                min-height: 46px;
                display: flex;
                align-items: center;
                padding: 8px 8px;
                font-size: 14px;
                font-weight: 600;
                color: #f9fafb;
                border-bottom: 1px solid #1f2937;
                word-break: break-word;
            }

            .coin-si {
                min-height: 46px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 8px 8px;
                color: #22c55e;
                font-size: 22px;
                font-weight: 900;
                border-bottom: 1px solid #1f2937;
            }

            .coin-no {
                min-height: 46px;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 8px 8px;
                color: #ef4444;
                font-size: 22px;
                font-weight: 900;
                border-bottom: 1px solid #1f2937;
            }

            /* Botón Modificar */
            div[data-testid="stButton"] > button[kind="primary"] {
                background-color: #f97316 !important;
                color: white !important;
                border: 1px solid #f97316 !important;
                border-radius: 5px !important;
                min-height: 36px !important;
                padding: 6px 10px !important;
                font-weight: 900 !important;
                box-shadow: none !important;
                margin-top: 4px !important;
            }

            div[data-testid="stButton"] > button[kind="primary"]:hover {
                background-color: #ea580c !important;
                border-color: #ea580c !important;
                color: white !important;
            }

            div[data-testid="stButton"] > button[kind="primary"] p,
            div[data-testid="stButton"] > button[kind="primary"] span {
                font-size: 13px !important;
                font-weight: 900 !important;
                line-height: 1 !important;
            }

            /* Botones normales dentro del modal */
            div[data-testid="stDialog"] div[data-testid="stButton"] > button {
                min-height: 42px !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def valor_seguro(valor, texto_vacio="Sin registrar"):
    if pd.isna(valor):
        return texto_vacio

    valor = str(valor).strip()

    if valor == "":
        return texto_vacio

    return escape(valor)


def mostrar_lavadas_del_dia():
    aplicar_estilos_lavadas()

    # =========================
    # ENCABEZADO
    # =========================

    fecha_hoy = datetime.now(ZoneInfo("America/Bogota")).strftime("%Y-%m-%d")

    st.header(f"Lavadas registradas: {fecha_hoy}")

    df = obtener_lavados()

    if df.empty:
        st.warning("Todavía no hay lavadas registradas hoy. 😥")
        return

    df["fecha"] = df["fecha"].astype(str)

    df_hoy = df[df["fecha"] == fecha_hoy].copy()

    # =========================
    # VALIDACIÓN SIN REGISTROS
    # =========================

    if df_hoy.empty:
        st.warning("Todavía no hay lavadas registradas hoy. 😥")
        return

    # =========================
    # NORMALIZAR COLUMNAS
    # =========================

    columnas_default = {
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

    for columna, valor_default in columnas_default.items():
        if columna not in df_hoy.columns:
            df_hoy[columna] = valor_default

    df_hoy["gamusero"] = df_hoy["gamusero"].fillna("Sin asignar").astype(str)
    df_hoy["nombre_cliente"] = df_hoy["nombre_cliente"].fillna("").astype(str)
    df_hoy["telefono_cliente"] = df_hoy["telefono_cliente"].fillna("").astype(str)
    df_hoy["placa"] = df_hoy["placa"].fillna("").astype(str)
    df_hoy["hora"] = df_hoy["hora"].fillna("").astype(str)
    df_hoy["coin"] = df_hoy["coin"].fillna(False).astype(bool)
    df_hoy["metodo_pago"] = df_hoy["metodo_pago"].fillna("Efectivo").astype(str)
    df_hoy["observaciones"] = df_hoy["observaciones"].fillna("").astype(str)

    columnas_numericas = [
        "valor_lavada",
        "pago_gamusero",
        "ganancia_negocio"
    ]

    for columna in columnas_numericas:
        df_hoy[columna] = pd.to_numeric(
            df_hoy[columna],
            errors="coerce"
        ).fillna(0).astype(int)

    # =========================
    # FILTRO POR PERSONAL
    # =========================

    gamuseros = ["Todos"] + sorted(
        df_hoy["gamusero"].dropna().unique().tolist()
    )

    filtro_gamusero = st.selectbox(
        "Filtrar por personal",
        gamuseros
    )

    if filtro_gamusero != "Todos":
        df_hoy = df_hoy[df_hoy["gamusero"] == filtro_gamusero].copy()

    # =========================
    # MÉTRICAS
    # =========================

    total_lavado = int(df_hoy["valor_lavada"].sum())
    total_pago = int(df_hoy["pago_gamusero"].sum())
    total_negocio = int(df_hoy["ganancia_negocio"].sum())

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
    st.caption("Usa el botón Modificar para editar la lavada o eliminar el registro.")

    df_mostrar = df_hoy.copy()

    df_mostrar = df_mostrar.sort_values(
        by=["fecha", "hora", "id"],
        ascending=[False, False, False]
    )

    # =========================
    # POPUP / MODAL
    # =========================

    @st.dialog("Modificar lavada")
    def abrir_popup_lavada(registro):
        id_lavada = int(registro["id"])
        nombre_actual = str(registro["gamusero"])
        coin_actual = bool(registro["coin"])
        metodo_pago_actual = str(registro.get("metodo_pago", "Efectivo"))

        if metodo_pago_actual not in ["Efectivo", "Nequi"]:
            metodo_pago_actual = "Efectivo"

        valor_actual = int(registro["valor_lavada"])
        pago_actual = int(registro["pago_gamusero"])
        ganancia_actual = int(registro["ganancia_negocio"])

        st.write(f"**Lavada #:** {id_lavada}")
        st.write(f"**Fecha:** {registro['fecha']}")
        st.write(f"**Hora:** {registro['hora']}")
        st.write(
            f"**Cliente:** {registro['nombre_cliente'] if registro['nombre_cliente'] else 'Sin registrar'}"
        )
        st.write(
            f"**Teléfono:** {registro['telefono_cliente'] if registro['telefono_cliente'] else 'Sin registrar'}"
        )
        st.write(f"**Placa:** {registro['placa']}")
        st.write(f"**Valor:** {formato_pesos(valor_actual)}")
        st.write(f"**40% personal:** {formato_pesos(pago_actual)}")
        st.write(f"**60% negocio:** {formato_pesos(ganancia_actual)}")

        opciones_valor = [
            valor for valor in range(20000, 60001, 5000)
            if valor > valor_actual
        ]

        cambiar_valor = False
        nuevo_valor_lavada = None

        if opciones_valor:
            cambiar_valor = st.checkbox("Cambiar valor de la lavada")

            if cambiar_valor:
                nuevo_valor_lavada = st.selectbox(
                    "Nuevo valor de la lavada",
                    opciones_valor,
                    format_func=formato_pesos
                )
        else:
            st.info("Esta lavada ya tiene el valor máximo permitido.")

        if registro["observaciones"]:
            st.write(f"**Observaciones:** {registro['observaciones']}")

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

                    if cambiar_valor and nuevo_valor_lavada is not None:
                        actualizar_valor_lavada(
                            id_registro=id_lavada,
                            nuevo_valor_lavada=nuevo_valor_lavada
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
    # TABLA PERSONALIZADA FORMAL
    # =========================

    col_accion, col_id, col_hora, col_personal, col_cliente, col_telefono, col_placa, col_valor, col_coin, col_pago = st.columns(
        [1.05, 0.8, 0.9, 1.55, 1.55, 1.45, 1.0, 1.0, 0.7, 1.1],
        gap="small"
    )

    with col_accion:
        st.markdown(
            '<div class="tabla-header-lavadas">Acción</div>',
            unsafe_allow_html=True
        )

    with col_id:
        st.markdown(
            '<div class="tabla-header-lavadas">Lavada #</div>',
            unsafe_allow_html=True
        )

    with col_hora:
        st.markdown(
            '<div class="tabla-header-lavadas">Hora</div>',
            unsafe_allow_html=True
        )

    with col_personal:
        st.markdown(
            '<div class="tabla-header-lavadas">Personal</div>',
            unsafe_allow_html=True
        )

    with col_cliente:
        st.markdown(
            '<div class="tabla-header-lavadas">Cliente</div>',
            unsafe_allow_html=True
        )

    with col_telefono:
        st.markdown(
            '<div class="tabla-header-lavadas">Teléfono</div>',
            unsafe_allow_html=True
        )

    with col_placa:
        st.markdown(
            '<div class="tabla-header-lavadas">Placa</div>',
            unsafe_allow_html=True
        )

    with col_valor:
        st.markdown(
            '<div class="tabla-header-lavadas">Valor</div>',
            unsafe_allow_html=True
        )

    with col_coin:
        st.markdown(
            '<div class="tabla-header-lavadas">Coin</div>',
            unsafe_allow_html=True
        )

    with col_pago:
        st.markdown(
            '<div class="tabla-header-lavadas">Pago</div>',
            unsafe_allow_html=True
        )

    for _, registro in df_mostrar.iterrows():
        col_accion, col_id, col_hora, col_personal, col_cliente, col_telefono, col_placa, col_valor, col_coin, col_pago = st.columns(
            [1.05, 0.8, 0.9, 1.55, 1.55, 1.45, 1.0, 1.0, 0.7, 1.1],
            gap="small"
        )

        id_lavada = int(registro["id"])

        with col_accion:
            if st.button(
                "Modificar",
                key=f"modificar_lavada_{id_lavada}",
                use_container_width=True,
                type="primary"
            ):
                abrir_popup_lavada(registro)

        with col_id:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{id_lavada}</div>',
                unsafe_allow_html=True
            )

        with col_hora:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{valor_seguro(registro["hora"], "")}</div>',
                unsafe_allow_html=True
            )

        with col_personal:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{valor_seguro(registro["gamusero"])}</div>',
                unsafe_allow_html=True
            )

        with col_cliente:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{valor_seguro(registro["nombre_cliente"])}</div>',
                unsafe_allow_html=True
            )

        with col_telefono:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{valor_seguro(registro["telefono_cliente"])}</div>',
                unsafe_allow_html=True
            )

        with col_placa:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{valor_seguro(registro["placa"], "")}</div>',
                unsafe_allow_html=True
            )

        with col_valor:
            valor_lavada = int(registro["valor_lavada"])

            st.markdown(
                f'<div class="texto-tabla-lavadas">{formato_pesos(valor_lavada)}</div>',
                unsafe_allow_html=True
            )

        with col_coin:
            if bool(registro["coin"]):
                st.markdown(
                    '<div class="coin-si">✓</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    '<div class="coin-no">✕</div>',
                    unsafe_allow_html=True
                )

        with col_pago:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{valor_seguro(registro["metodo_pago"], "Efectivo")}</div>',
                unsafe_allow_html=True
            )