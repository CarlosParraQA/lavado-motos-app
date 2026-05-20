import streamlit as st
from pathlib import Path
import base64


def cargar_logo_base64(ruta_logo="assets/logo.png"):
    logo_path = Path(ruta_logo)

    if not logo_path.exists():
        return ""

    with open(logo_path, "rb") as file:
        return base64.b64encode(file.read()).decode()


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

            .header-card {
                border: 1px solid #374151;
                border-radius: 14px;
                padding: 18px 22px;
                margin-bottom: 20px;
                background-color: transparent;
            }

            .header-content {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 20px;
            }

            .brand-content {
                display: flex;
                align-items: center;
                gap: 18px;
            }

            .brand-logo {
                width: 100px;
                height: 100px;
                object-fit: contain;
                flex-shrink: 0;
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

            .header-actions {
                display: flex;
                align-items: center;
                gap: 12px;
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
                white-space: nowrap;
            }

            div[data-testid="stButton"] > button {
                border-radius: 10px;
                border: 1px solid #374151;
            }

            /* =========================
               AJUSTES PARA CELULAR
            ========================= */
            @media (max-width: 768px) {
                .block-container {
                    max-width: 100% !important;
                    padding-top: 0.7rem !important;
                    padding-left: 0.7rem !important;
                    padding-right: 0.7rem !important;
                }

                .header-card {
                    padding: 14px 16px;
                    margin-bottom: 16px;
                }

                .header-content {
                    flex-direction: column;
                    align-items: stretch;
                    gap: 14px;
                }

                .brand-content {
                    flex-direction: row;
                    align-items: center;
                    gap: 12px;
                }

                .brand-logo {
                    width: 68px;
                    height: 68px;
                }

                .navbar-title {
                    font-size: 26px !important;
                    margin-bottom: 2px !important;
                }

                .navbar-subtitle {
                    font-size: 14px !important;
                }

                .header-actions {
                    width: 100%;
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 10px;
                }

                .user-box {
                    font-size: 13px !important;
                    padding: 8px 10px !important;
                    min-height: 36px !important;
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
    logo_base64 = cargar_logo_base64("assets/logo.png")

    if logo_base64:
        logo_html = f"""
        <img src="data:image/png;base64,{logo_base64}" class="brand-logo">
        """
    else:
        logo_html = """
        <div class="brand-logo" style="font-size: 42px; display:flex; align-items:center;">
            🏍️
        </div>
        """

    # =========================
    # HEADER SUPERIOR
    # =========================

    st.markdown(
        f"""
        <div class="header-card">
            <div class="header-content">
                <div class="brand-content">
                    {logo_html}
                    <div>
                        <div class="navbar-title">Moto Space Wash</div>
                        <div class="navbar-subtitle">Sistema de registro de lavadas</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

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