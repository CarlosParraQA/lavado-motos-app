import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

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
            /* Botón Modificar */
            div[data-testid="stButton"] > button[kind="primary"] {
                background-color: #f97316 !important;
                color: white !important;
                border: 1px solid #f97316 !important;
                border-radius: 10px !important;
                min-height: 44px !important;
                padding: 10px 14px !important;
                font-weight: 900 !important;
            }

            div[data-testid="stButton"] > button[kind="primary"]:hover {
                background-color: #ea580c !important;
                border-color: #ea580c !important;
                color: white !important;
            }

            div[data-testid="stButton"] > button[kind="primary"] p,
            div[data-testid="stButton"] > button[kind="primary"] span {
                font-size: 15px !important;
                font-weight: 900 !important;
            }

            .tabla-header-lavadas {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 10px;
                padding: 10px 8px;
                font-weight: 900;
                color: #d1d5db;
                margin-bottom: 6px;
            }

            .fila-lavada {
                border-bottom: 1px solid #1f2937;
                padding: 4px 0;
            }

            .coin-si {
                color: #22c55e;
                font-size: 22px;
                font-weight: 900;
                text-align: center;
            }

            .coin-no {
                color: #ef4444;
                font-size: 22px;
                font-weight: 900;
                text-align: center;
            }

            .texto-tabla-lavadas {
                display: flex;
                align-items: center;
                min-height: 44px;
                font-weight: 700;
                color: #f9fafb;
                word-break: break-word;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def mostrar_lavadas_del_dia():
    aplicar_estilos_lavadas()

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

    gamuseros = ["Todos"] + sorted(df_hoy["gamusero"].dropna().unique().tolist())

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
    # PREPARAR TABLA
    # =========================

    st.subheader("Detalle de lavadas")
    st.caption("Presiona el botón Modificar para editar o eliminar una lavada.")

    df_mostrar = df_hoy.copy()

    columnas_default = {
        "coin": False,
        "metodo_pago": "Efectivo",
        "nombre_cliente": "",
        "telefono_cliente": "",
        "observaciones": ""
    }

    for columna, valor in columnas_default.items():
        if columna not in df_mostrar.columns:
            df_mostrar[columna] = valor

    df_mostrar["coin"] = df_mostrar["coin"].fillna(False).astype(bool)
    df_mostrar["metodo_pago"] = df_mostrar["metodo_pago"].fillna("Efectivo").astype(str)
    df_mostrar["nombre_cliente"] = df_mostrar["nombre_cliente"].fillna("").astype(str)
    df_mostrar["telefono_cliente"] = df_mostrar["telefono_cliente"].fillna("").astype(str)
    df_mostrar["observaciones"] = df_mostrar["observaciones"].fillna("").astype(str)

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
        nombre_actual = registro["gamusero"]
        coin_actual = bool(registro["coin"])
        metodo_pago_actual = registro.get("metodo_pago", "Efectivo")

        if metodo_pago_actual not in ["Efectivo", "Nequi"]:
            metodo_pago_actual = "Efectivo"

        valor_formateado = formato_pesos(int(registro["valor_lavada"]))
        pago_formateado = formato_pesos(int(registro["pago_gamusero"]))
        negocio_formateado = formato_pesos(int(registro["ganancia_negocio"]))

        st.write(f"**Lavada #:** {id_lavada}")
        st.write(f"**Fecha:** {registro['fecha']}")
        st.write(f"**Hora:** {registro['hora']}")
        st.write(f"**Cliente:** {registro['nombre_cliente'] if registro['nombre_cliente'] else 'Sin registrar'}")
        st.write(f"**Teléfono:** {registro['telefono_cliente'] if registro['telefono_cliente'] else 'Sin registrar'}")
        st.write(f"**Placa:** {registro['placa']}")
        st.write(f"**Valor:** {valor_formateado}")
        st.write(f"**40% personal:** {pago_formateado}")
        st.write(f"**60% negocio:** {negocio_formateado}")

        valor_actual = int(registro["valor_lavada"])

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
    # TABLA PERSONALIZADA CON BOTÓN MODIFICAR
    # =========================

    col_accion, col_id, col_hora, col_personal, col_cliente, col_telefono, col_placa, col_valor, col_coin, col_pago = st.columns(
        [1.1, 0.8, 0.9, 1.6, 1.6, 1.5, 1.1, 1.1, 0.8, 1.2]
    )

    with col_accion:
        st.markdown('<div class="tabla-header-lavadas">Acción</div>', unsafe_allow_html=True)
    with col_id:
        st.markdown('<div class="tabla-header-lavadas">Lavada #</div>', unsafe_allow_html=True)
    with col_hora:
        st.markdown('<div class="tabla-header-lavadas">Hora</div>', unsafe_allow_html=True)
    with col_personal:
        st.markdown('<div class="tabla-header-lavadas">Personal</div>', unsafe_allow_html=True)
    with col_cliente:
        st.markdown('<div class="tabla-header-lavadas">Cliente</div>', unsafe_allow_html=True)
    with col_telefono:
        st.markdown('<div class="tabla-header-lavadas">Teléfono</div>', unsafe_allow_html=True)
    with col_placa:
        st.markdown('<div class="tabla-header-lavadas">Placa</div>', unsafe_allow_html=True)
    with col_valor:
        st.markdown('<div class="tabla-header-lavadas">Valor</div>', unsafe_allow_html=True)
    with col_coin:
        st.markdown('<div class="tabla-header-lavadas">Coin</div>', unsafe_allow_html=True)
    with col_pago:
        st.markdown('<div class="tabla-header-lavadas">Pago</div>', unsafe_allow_html=True)

    for _, registro in df_mostrar.iterrows():
        col_accion, col_id, col_hora, col_personal, col_cliente, col_telefono, col_placa, col_valor, col_coin, col_pago = st.columns(
            [1.1, 0.8, 0.9, 1.6, 1.6, 1.5, 1.1, 1.1, 0.8, 1.2]
        )

        with col_accion:
            if st.button(
                "Modificar",
                key=f"modificar_lavada_{int(registro['id'])}",
                use_container_width=True,
                type="primary"
            ):
                abrir_popup_lavada(registro)

        with col_id:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{int(registro["id"])}</div>',
                unsafe_allow_html=True
            )

        with col_hora:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{registro["hora"]}</div>',
                unsafe_allow_html=True
            )

        with col_personal:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{registro["gamusero"]}</div>',
                unsafe_allow_html=True
            )

        with col_cliente:
            cliente = registro["nombre_cliente"] if registro["nombre_cliente"] else "Sin registrar"
            st.markdown(
                f'<div class="texto-tabla-lavadas">{cliente}</div>',
                unsafe_allow_html=True
            )

        with col_telefono:
            telefono = registro["telefono_cliente"] if registro["telefono_cliente"] else "Sin registrar"
            st.markdown(
                f'<div class="texto-tabla-lavadas">{telefono}</div>',
                unsafe_allow_html=True
            )

        with col_placa:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{registro["placa"]}</div>',
                unsafe_allow_html=True
            )

        with col_valor:
            st.markdown(
                f'<div class="texto-tabla-lavadas">{formato_pesos(int(registro["valor_lavada"]))}</div>',
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
                f'<div class="texto-tabla-lavadas">{registro["metodo_pago"]}</div>',
                unsafe_allow_html=True
            )