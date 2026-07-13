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


# =========================================================
# ESTILOS
# =========================================================

def aplicar_estilos_lavadas():
    st.markdown(
        """
        <style>
            /* =========================
               TABLA DE LAVADAS
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
                padding: 4px;
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
                padding: 4px;
                color: #ef4444;
                font-size: 22px;
                font-weight: 900;
                border-bottom: 1px solid #1f2937;
            }

            /* =========================
               BOTÓN MODIFICAR
            ========================= */

            div[data-testid="stButton"] > button[kind="primary"] {
                background-color: #8F3221 !important;
                color: white !important;
                border: 1px solid #8F3221 !important;
                border-radius: 1px !important;
                min-height: 34px !important;
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

            /* Botones dentro del modal */
            div[data-testid="stDialog"]
            div[data-testid="stButton"] > button {
                min-height: 42px !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================

def valor_seguro(valor, texto_vacio="Sin registrar"):
    """
    Evita mostrar valores vacíos, nulos o HTML sin escapar.
    """

    if pd.isna(valor):
        return texto_vacio

    valor = str(valor).strip()

    if valor == "":
        return texto_vacio

    return escape(valor)


def normalizar_dataframe_lavadas(df):
    """
    Agrega columnas faltantes y normaliza los tipos de datos.
    """

    if df is None or df.empty:
        return pd.DataFrame()

    df = df.copy()

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
        if columna not in df.columns:
            df[columna] = valor_default

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

    for columna, valor_default in columnas_texto.items():
        df[columna] = (
            df[columna]
            .fillna(valor_default)
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
# RESUMEN DE LAVADAS
# =========================================================

def mostrar_resumen_lavadas(df_hoy):
    """
    Muestra en una sola fila el total de lavadas
    y la cantidad realizada por cada colaborador.
    """

    total_lavadas = len(df_hoy)

    resumen_colaboradores = (
        df_hoy
        .groupby(
            "gamusero",
            dropna=False
        )
        .size()
        .reset_index(name="cantidad_lavadas")
        .sort_values(
            by=[
                "cantidad_lavadas",
                "gamusero"
            ],
            ascending=[
                False,
                True
            ]
        )
        .reset_index(drop=True)
    )

    st.subheader("Resumen de lavadas del día")

    # Total general + cada colaborador
    cantidad_tarjetas = 1 + len(resumen_colaboradores)

    columnas = st.columns(cantidad_tarjetas)

    # Primera tarjeta: total general
    with columnas[0]:
        with st.container(border=True):
            st.metric(
                label="🏍️ Total de lavadas",
                value=total_lavadas
            )

    # Siguientes tarjetas: colaboradores
    for indice, fila in resumen_colaboradores.iterrows():
        colaborador = str(
            fila["gamusero"]
        ).strip()

        if not colaborador:
            colaborador = "Sin asignar"

        cantidad_lavadas = int(
            fila["cantidad_lavadas"]
        )

        with columnas[indice + 1]:
            with st.container(border=True):
                st.metric(
                    label=f"👤 {colaborador}",
                    value=cantidad_lavadas
                )

# =========================================================
# VISTA PRINCIPAL
# =========================================================

def mostrar_lavadas_del_dia():
    aplicar_estilos_lavadas()

    fecha_hoy = datetime.now(
        ZoneInfo("America/Bogota")
    ).strftime("%Y-%m-%d")

    fecha_visual = datetime.now(
        ZoneInfo("America/Bogota")
    ).strftime("%d/%m/%Y")

    # =====================================================
    # CONSULTAR INFORMACIÓN
    # =====================================================

    try:
        df = obtener_lavados()

    except Exception as error:
        st.error(
            "No se pudo cargar la información de las lavadas."
        )
        st.exception(error)
        return

    if df is None or df.empty:
        st.warning(
            "Todavía no hay lavadas registradas hoy. 😥"
        )
        return

    df = normalizar_dataframe_lavadas(df)

    df_hoy = df.loc[
        df["fecha"] == fecha_hoy
    ].copy()

    if df_hoy.empty:
        st.warning(
            "Todavía no hay lavadas registradas hoy. 😥"
        )
        return

    # =====================================================
    # RESUMEN GENERAL
    # =====================================================

    mostrar_resumen_lavadas(df_hoy)

    st.divider()

    # =====================================================
    # FILTRO POR PERSONAL
    # =====================================================

    gamuseros = [
        "Todos"
    ] + sorted(
        df_hoy["gamusero"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    filtro_gamusero = st.selectbox(
        "Filtrar detalle por personal",
        options=gamuseros,
        key="filtro_gamusero_lavadas"
    )

    # El resumen se calcula antes del filtro.
    # El filtro solo modifica la tabla inferior.
    df_filtrado = df_hoy.copy()

    if filtro_gamusero != "Todos":
        df_filtrado = df_filtrado.loc[
            df_filtrado["gamusero"]
            == filtro_gamusero
        ].copy()

    st.divider()

    # =====================================================
    # TABLA DE LAVADAS
    # =====================================================

    st.subheader("Detalle de lavadas")

    st.caption(
        "Usa el botón Modificar para editar la lavada "
        "o eliminar el registro."
    )

    df_mostrar = (
        df_filtrado
        .sort_values(
            by=[
                "fecha",
                "hora",
                "id"
            ],
            ascending=[
                False,
                False,
                False
            ]
        )
        .copy()
    )

    # =====================================================
    # MODAL PARA MODIFICAR UNA LAVADA
    # =====================================================

    @st.dialog("Modificar lavada")
    def abrir_popup_lavada(registro):
        id_lavada = int(
            registro["id"]
        )

        nombre_actual = str(
            registro["gamusero"]
        )

        coin_actual = bool(
            registro["coin"]
        )

        metodo_pago_actual = str(
            registro.get(
                "metodo_pago",
                "Efectivo"
            )
        )

        if metodo_pago_actual not in [
            "Efectivo",
            "Nequi"
        ]:
            metodo_pago_actual = "Efectivo"

        valor_actual = int(
            registro["valor_lavada"]
        )

        st.write(
            f"**Lavada #:** {id_lavada}"
        )

        st.write(
            f"**Fecha:** {registro['fecha']}"
        )

        st.write(
            f"**Hora:** {registro['hora']}"
        )

        cliente = (
            registro["nombre_cliente"]
            if registro["nombre_cliente"]
            else "Sin registrar"
        )

        telefono = (
            registro["telefono_cliente"]
            if registro["telefono_cliente"]
            else "Sin registrar"
        )

        st.write(
            f"**Cliente:** {cliente}"
        )

        st.write(
            f"**Teléfono:** {telefono}"
        )

        st.write(
            f"**Placa:** {registro['placa']}"
        )

        st.write(
            f"**Valor actual:** "
            f"{formato_pesos(valor_actual)}"
        )

        # =================================================
        # CAMBIO DE VALOR
        # =================================================

        opciones_valor = [
            valor
            for valor in range(
                20000,
                60001,
                5000
            )
            if valor > valor_actual
        ]

        cambiar_valor = False
        nuevo_valor_lavada = None

        if opciones_valor:
            cambiar_valor = st.checkbox(
                "Cambiar valor de la lavada"
            )

            if cambiar_valor:
                nuevo_valor_lavada = st.selectbox(
                    "Nuevo valor de la lavada",
                    options=opciones_valor,
                    format_func=formato_pesos
                )

        else:
            st.info(
                "Esta lavada ya tiene el valor "
                "máximo permitido."
            )

        # =================================================
        # INFORMACIÓN EDITABLE
        # =================================================

        observaciones = str(
            registro.get(
                "observaciones",
                ""
            )
        ).strip()

        if observaciones:
            st.write(
                f"**Observaciones:** {observaciones}"
            )

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
            options=[
                "Efectivo",
                "Nequi"
            ],
            index=(
                0
                if metodo_pago_actual == "Efectivo"
                else 1
            )
        )

        col_guardar, col_eliminar = st.columns(2)

        # =================================================
        # GUARDAR CAMBIOS
        # =================================================

        with col_guardar:
            if st.button(
                "Guardar cambios",
                use_container_width=True,
                key=f"guardar_lavada_{id_lavada}"
            ):
                nombre_limpio = (
                    nuevo_nombre
                    .strip()
                    .title()
                )

                if not nombre_limpio:
                    st.error(
                        "El nombre no puede estar vacío."
                    )
                    return

                actualizar_nombre_gamusero(
                    id_registro=id_lavada,
                    nuevo_nombre=nombre_limpio
                )

                actualizar_coin_lavada(
                    id_registro=id_lavada,
                    coin=nuevo_coin
                )

                actualizar_metodo_pago_lavada(
                    id_registro=id_lavada,
                    metodo_pago=nuevo_metodo_pago
                )

                if (
                    cambiar_valor
                    and nuevo_valor_lavada is not None
                ):
                    actualizar_valor_lavada(
                        id_registro=id_lavada,
                        nuevo_valor_lavada=nuevo_valor_lavada
                    )

                st.success(
                    "Lavada actualizada correctamente."
                )

                st.rerun()

        # =================================================
        # ELIMINAR REGISTRO
        # =================================================

        with col_eliminar:
            rol_actual = (
                st.session_state.get("rol")
                or st.session_state.get(
                    "usuario",
                    ""
                )
            ).strip().lower()

            if rol_actual == "admin":
                if st.button(
                    "Eliminar lavada",
                    use_container_width=True,
                    key=f"eliminar_lavada_{id_lavada}"
                ):
                    eliminar_registro(
                        id_lavada
                    )

                    st.success(
                        "Registro eliminado correctamente."
                    )

                    st.rerun()

            else:
                st.info(
                    "Solo el administrador puede eliminar."
                )

    # =====================================================
    # ENCABEZADOS DE LA TABLA
    # =====================================================

    (
        col_accion,
        col_id,
        col_hora,
        col_personal,
        col_cliente,
        col_telefono,
        col_placa,
        col_valor,
        col_coin,
        col_pago
    ) = st.columns(
        [
            1.05,
            0.8,
            0.9,
            1.55,
            1.55,
            1.45,
            1.0,
            1.0,
            0.7,
            1.1
        ],
        gap="small"
    )

    with col_accion:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Acción'
            '</div>',
            unsafe_allow_html=True
        )

    with col_id:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Lavada #'
            '</div>',
            unsafe_allow_html=True
        )

    with col_hora:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Hora'
            '</div>',
            unsafe_allow_html=True
        )

    with col_personal:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Personal'
            '</div>',
            unsafe_allow_html=True
        )

    with col_cliente:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Cliente'
            '</div>',
            unsafe_allow_html=True
        )

    with col_telefono:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Teléfono'
            '</div>',
            unsafe_allow_html=True
        )

    with col_placa:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Placa'
            '</div>',
            unsafe_allow_html=True
        )

    with col_valor:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Valor'
            '</div>',
            unsafe_allow_html=True
        )

    with col_coin:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Coin'
            '</div>',
            unsafe_allow_html=True
        )

    with col_pago:
        st.markdown(
            '<div class="tabla-header-lavadas">'
            'Pago'
            '</div>',
            unsafe_allow_html=True
        )

    # =====================================================
    # FILAS DE LA TABLA
    # =====================================================

    for _, registro in df_mostrar.iterrows():
        (
            col_accion,
            col_id,
            col_hora,
            col_personal,
            col_cliente,
            col_telefono,
            col_placa,
            col_valor,
            col_coin,
            col_pago
        ) = st.columns(
            [
                1.05,
                0.8,
                0.9,
                1.55,
                1.55,
                1.45,
                1.0,
                1.0,
                0.7,
                1.1
            ],
            gap="small"
        )

        id_lavada = int(
            registro["id"]
        )

        with col_accion:
            if st.button(
                "Modificar",
                key=f"modificar_lavada_{id_lavada}",
                use_container_width=True,
                type="primary"
            ):
                abrir_popup_lavada(
                    registro
                )

        with col_id:
            st.markdown(
                f"""
                <div class="texto-tabla-lavadas">
                    {id_lavada}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_hora:
            hora = valor_seguro(
                registro["hora"],
                ""
            )

            st.markdown(
                f"""
                <div class="texto-tabla-lavadas">
                    {hora}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_personal:
            personal = valor_seguro(
                registro["gamusero"]
            )

            st.markdown(
                f"""
                <div class="texto-tabla-lavadas">
                    {personal}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_cliente:
            cliente = valor_seguro(
                registro["nombre_cliente"]
            )

            st.markdown(
                f"""
                <div class="texto-tabla-lavadas">
                    {cliente}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_telefono:
            telefono = valor_seguro(
                registro["telefono_cliente"]
            )

            st.markdown(
                f"""
                <div class="texto-tabla-lavadas">
                    {telefono}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_placa:
            placa = valor_seguro(
                registro["placa"],
                ""
            )

            st.markdown(
                f"""
                <div class="texto-tabla-lavadas">
                    {placa}
                </div>
                """,
                unsafe_allow_html=True
            )

        with col_valor:
            valor_lavada = int(
                registro["valor_lavada"]
            )

            st.markdown(
                f"""
                <div class="texto-tabla-lavadas">
                    {formato_pesos(valor_lavada)}
                </div>
                """,
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
            metodo_pago = valor_seguro(
                registro["metodo_pago"],
                "Efectivo"
            )

            st.markdown(
                f"""
                <div class="texto-tabla-lavadas">
                    {metodo_pago}
                </div>
                """,
                unsafe_allow_html=True
            )