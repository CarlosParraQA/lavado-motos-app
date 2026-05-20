import streamlit as st


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

            .navbar-container {
                background-color: #1f2937;
                padding: 16px 26px;
                border-radius: 14px;
                margin-bottom: 16px;
                border: 1px solid #374151;
            }

            .navbar-title {
                font-size: 24px;
                font-weight: 700;
                color: white;
                margin-bottom: 4px;
            }

            .navbar-subtitle {
                font-size: 13px;
                color: #9ca3af;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def navbar():
    st.markdown(
        """
        <div class="navbar-container">
            <div class="navbar-title">🏍️ Moto Space Wash</div>
            <div class="navbar-subtitle">Sistema de registro de lavadas</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    opciones = {
        "Inicio": "🏠 Inicio",
        "Registrar": "🌸 Registrar lavada",
        "Lavadas": "📋 Lavadas del día",
        "Cierre": "💰 Cierre del día",
        "Historial": "📊 Historial"
    }

    if "vista" not in st.session_state:
        st.session_state.vista = "Inicio"

    cols = st.columns(len(opciones))

    for col, (clave, etiqueta) in zip(cols, opciones.items()):
        with col:
            if st.button(
                etiqueta,
                use_container_width=True,
                key=f"nav_{clave}"
            ):
                st.session_state.vista = clave
                st.rerun()

    st.divider()