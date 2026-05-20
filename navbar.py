import streamlit as st
from pathlib import Path


def aplicar_estilos():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none !important;
            }

            [data-testid="collapsedControl"] {
                display: none !important;
            }

            header[data-testid="stHeader"] {
                display: none !important;
            }

            .block-container {
                max-width: 96% !important;
                padding-top: 1.5rem !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
            }

            .navbar-box {
                background-color: #1f2937;
                padding: 16px 26px;
                border-radius: 14px;
                margin-bottom: 16px;
                border: 1px solid #374151;
            }

            .navbar-title {
                font-size: 35px;
                font-weight: 700;
                color: white;
                margin-bottom: 4px;
            }

            .navbar-subtitle {
                font-size: 20px;
                color: #e5e619;
            }

            .user-box {
                background-color: #111827;
                border: 1px solid #374151;
                border-radius: 12px;
                padding: 10px 14px;
                font-size: 14px;
                color: #e5e7eb;
                text-align: center;
                min-height: 38px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            div[data-testid="stButton"] > button {
                border-radius: 10px;
                border: 1px solid #374151;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def cerrar_sesion():
    st.session_state.logueado = False
    st.session_state.usuario = ""
    st.session_state.vista = "Inicio"
    st.rerun()


def navbar():
    usuario_actual = st.session_state.get("usuario", "Sin usuario")
    logo_path = Path("assets/logo.png")

    with st.container(border=True):
        col_logo, col_title = st.columns([0.08, 0.92])

        with col_logo:
            if logo_path.exists():
                st.image(str(logo_path), width=100)
            else:
                st.markdown("### 🏍️")

        with col_title:
            st.markdown(
                f"""
                <div class="navbar-title">Moto Space Wash</div>
                <div class="navbar-subtitle">
                    Sistema de registro de lavadas | Usuario: <strong>{usuario_actual}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

    opciones = {
        "Inicio": "Inicio",
        "Registrar": "Registrar lavada",
        "Lavadas": "Lavadas del día",
        "Cierre": "Próximamente nuevo módulo",
        "Historial": "Historial general"
    }

    if "vista" not in st.session_state:
        st.session_state.vista = "Inicio"

    col1, col2, col3, col4, col5, col_user, col_logout = st.columns(
        [1, 1.4, 1.4, 1.8, 1.5, 1.2, 1]
    )

    columnas = [col1, col2, col3, col4, col5]

    for col, (clave, etiqueta) in zip(columnas, opciones.items()):
        with col:
            if st.button(
                etiqueta,
                use_container_width=True,
                key=f"nav_{clave}"
            ):
                st.session_state.vista = clave
                st.rerun()

    with col_user:
        st.markdown(
            f"""
            <div class="user-box">
                👤 {usuario_actual}
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_logout:
        if st.button("Cerrar sesión", use_container_width=True):
            cerrar_sesion()

    st.divider()