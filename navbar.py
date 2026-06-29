import streamlit as st
from pathlib import Path
import base64
from auth import cerrar_sesion


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
            /* Ocultar header superior de Streamlit */
            header[data-testid="stHeader"] {
                display: none !important;
            }

            /* Contenedor principal */
            .block-container {
                max-width: 96% !important;
                padding-top: 1.2rem !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
            }

            /* Sidebar izquierdo */
            section[data-testid="stSidebar"] {
                background-color: #111827 !important;
                border-right: 1px solid #374151 !important;
            }

            section[data-testid="stSidebar"] > div {
                padding-top: 1.2rem !important;
            }

            /* Logo */
            .sidebar-logo {
                width: 95px;
                height: 95px;
                object-fit: contain;
                display: block;
                margin: 0 auto 12px auto;
            }

            .sidebar-title {
                font-size: 24px;
                font-weight: 800;
                color: white;
                text-align: center;
                margin-bottom: 2px;
                line-height: 1.1;
            }

            .sidebar-subtitle {
                font-size: 13px;
                color: #9ca3af;
                text-align: center;
                margin-bottom: 20px;
                line-height: 1.2;
            }

            .sidebar-user {
                background-color: #1f2937;
                border: 1px solid #374151;
                border-radius: 12px;
                padding: 12px 10px;
                color: #e5e7eb;
                font-size: 16px;
                font-weight: 700;
                text-align: center;
                margin-bottom: 16px;
                word-break: break-word;
            }

            .sidebar-section-title {
                color: #9ca3af;
                font-size: 12px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.08em;
                margin: 18px 0 8px 0;
            }

            /* Botones SOLO del sidebar */
            section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
                background-color: #374151 !important;
                color: white !important;
                border-radius: 12px !important;
                border: 1px solid #4b5563 !important;
                min-height: 54px !important;
                padding: 12px 14px !important;
                width: 100% !important;
                margin-bottom: 6px !important;
            }

            /* Texto interno de los botones */
            section[data-testid="stSidebar"] div[data-testid="stButton"] > button p,
            section[data-testid="stSidebar"] div[data-testid="stButton"] > button span {
                font-size: 17px !important;
                font-weight: 800 !important;
                line-height: 1.1 !important;
            }

            /* Hover */
            section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
                background-color: #4b5563 !important;
                border-color: #6b7280 !important;
            }

            /* Botón cerrar sesión */
            .logout-space {
                margin-top: 18px;
            }

            /* Responsive */
            @media (max-width: 768px) {
                .block-container {
                    max-width: 100% !important;
                    padding-top: 0.8rem !important;
                    padding-left: 1rem !important;
                    padding-right: 1rem !important;
                }

                .sidebar-logo {
                    width: 72px !important;
                    height: 72px !important;
                }

                .sidebar-title {
                    font-size: 20px !important;
                }

                .sidebar-subtitle {
                    font-size: 12px !important;
                }

                section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
                    min-height: 46px !important;
                    padding: 10px 10px !important;
                }

                section[data-testid="stSidebar"] div[data-testid="stButton"] > button p,
                section[data-testid="stSidebar"] div[data-testid="stButton"] > button span {
                    font-size: 14px !important;
                    font-weight: 800 !important;
                }
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def navbar():
    usuario_actual = st.session_state.get("usuario", "Sin usuario")
    logo_base64 = cargar_logo_base64("assets/logo.png")

    if "vista" not in st.session_state:
        st.session_state.vista = "Inicio"

    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="sidebar-logo">'
    else:
        logo_html = '<div style="font-size:55px; text-align:center;">🏍️</div>'

    opciones = {
        "Inicio": "Inicio",
        "Registrar": "Registrar Nuevo Servicio",
        "Lavadas": "Servicios del Día",
        "Cierre": "Pago a Empleados",
        "Historial": "Historial General"
    }

    with st.sidebar:
        st.markdown(
            f"""
            {logo_html}
            <div class="sidebar-title">Moto Space Wash</div>
            <div class="sidebar-subtitle">Sistema de registro de lavadas</div>

            <div class="sidebar-user">
                👤 {usuario_actual}
            </div>

            <div class="sidebar-section-title">Menú principal</div>
            """,
            unsafe_allow_html=True
        )

        for clave, etiqueta in opciones.items():
            texto_boton = f"✅ {etiqueta}" if st.session_state.vista == clave else etiqueta

            if st.button(
                texto_boton,
                use_container_width=True,
                key=f"nav_{clave}"
            ):
                st.session_state.vista = clave
                st.rerun()

        st.markdown('<div class="logout-space"></div>', unsafe_allow_html=True)

        if st.button("Cerrar sesión", use_container_width=True):
            cerrar_sesion()