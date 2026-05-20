import streamlit as st


def ocultar_sidebar():
    st.markdown(
        """
        <style>
            /* Oculta el sidebar */
            [data-testid="stSidebar"] {
                display: none !important;
            }

            /* Oculta el botón de abrir/cerrar sidebar */
            [data-testid="collapsedControl"] {
                display: none !important;
            }

            /* Usa más ancho de pantalla */
            .block-container {
                max-width: 96% !important;
                padding-top: 1.5rem !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
            }

            /* Reduce espacios superiores */
            header[data-testid="stHeader"] {
                display: none !important;
            }

            /* Evita tanto movimiento visual */
            .main {
                overflow-x: hidden;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def navbar():
    st.markdown(
        """
        <style>
            .navbar-container {
                background-color: #1f2937;
                padding: 16px 26px;
                border-radius: 14px;
                margin-bottom: 18px;
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

        <div class="navbar-container">
            <div class="navbar-title">🏍️ Moto Space Wash</div>
            <div class="navbar-subtitle">Sistema de registro de lavadas</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.page_link("Inicio.py", label="🏠 Inicio")

    with col2:
        st.page_link("pages/1_Registrar_Lavada.py", label="🌸 Registrar lavada")

    with col3:
        st.page_link("pages/2_Lavadas_Del_Dia.py", label="📋 Lavadas del día")

    with col4:
        st.page_link("pages/3_Cierre_Del_Dia.py", label="💰 Cierre del día")

    with col5:
        st.page_link("pages/4_Historial_General.py", label="📊 Historial")

    st.divider()