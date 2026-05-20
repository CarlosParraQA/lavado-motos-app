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
                padding-top: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            .navbar-title {
                font-size: 35px;
                font-weight: 700;
                color: white;
                margin-bottom: 4px;
                line-height: 1.1;
            }

            .navbar-subtitle {
                font-size: 20px;
                color: #9ca3af;
                line-height: 1.2;
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
                margin-bottom: 8px;
                white-space: nowrap;
            }

            div[data-testid="stButton"] > button {
                border-radius: 10px;
                border: 1px solid #374151;
            }

            @media (max-width: 768px) {
                .block-container {
                    max-width: 100% !important;
                    padding-top: 0.7rem !important;
                    padding-left: 0.7rem !important;
                    padding-right: 0.7rem !important;
                }

                .navbar-title {
                    font-size: 22px !important;
                    margin-bottom: 2px !important;
                    white-space: nowrap;
                }

                .navbar-subtitle {
                    font-size: 12px !important;
                    white-space: nowrap;
                }

                .user-box {
                    font-size: 12px !important;
                    padding: 8px 10px !important;
                    min-height: 34px !important;
                    margin-bottom: 4px !important;
                }

                div[data-testid="stImage"] img {
                    max-width: 70px !important;
                    height: auto !important;
                }

                div[data-testid="stButton"] > button {
                    min-height: 40px !important;
                    padding: 6px 8px !important;
                    font-size: 14px !important;
                }
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

    # =========================
    # HEADER SUPERIOR
    # =========================

    with st.container(border=True):
        col_logo, col_title = st.columns(
            [0.28, 0.72],
            vertical_alignment="center"
        )

        with col_logo:
            if logo_path.exists():
                st.image(str(logo_path), width=55)
            else:
                st.markdown("### 🏍️")

        with col_title:
            st.markdown(
                """
                <div class="navbar-title">Moto Space Wash</div>
                <div class="navbar-subtitle">Sistema de registro de lavadas</div>
                """,
                unsafe_allow_html=True
            )

    # =========================
    # USUARIO Y CERRAR SESIÓN
    # =========================

    col_user, col_logout = st.columns([1, 1])

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

    # =========================
    # BOTONES DE NAVEGACIÓN
    # =========================

    opciones = {
        "Inicio": "Inicio",
        "Registrar": "Registrar Nuevo Servicio",
        "Lavadas": "Servicios del Día",
        "Cierre": "Próximamente nuevo módulo",
        "Historial": "Historial General"
    }

    if "vista" not in st.session_state:
        st.session_state.vista = "Inicio"

    col1, col2, col3, col4, col5 = st.columns(
        [1, 1.4, 1.4, 1.8, 1.5]
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

    st.divider()