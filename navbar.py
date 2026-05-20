import streamlit as st


def ocultar_sidebar():
    st.markdown(
        """
        <style>
            [data-testid="stSidebar"] {
                display: none;
            }

            [data-testid="collapsedControl"] {
                display: none;
            }

            .block-container {
                max-width: 95% !important;
                padding-top: 2rem;
                padding-left: 2rem;
                padding-right: 2rem;
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
                display: flex;
                align-items: center;
                justify-content: space-between;
                background-color: #1f2937;
                padding: 14px 24px;
                border-radius: 14px;
                margin-bottom: 28px;
                border: 1px solid #374151;
            }

            .navbar-title {
                font-size: 22px;
                font-weight: 700;
                color: white;
            }

            .navbar-subtitle {
                font-size: 13px;
                color: #9ca3af;
            }
        </style>

        <div class="navbar-container">
            <div>
                <div class="navbar-title">🏍️ Moto Space Wash</div>
                <div class="navbar-subtitle">Sistema de registro de lavadas</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.page_link("Inicio.py", label="Inicio", icon="🏠")

    with col2:
        st.page_link("pages/1_Registrar_Lavada.py", label="Registrar lavada", icon="🌸")

    with col3:
        st.page_link("pages/2_Lavadas_Del_Dia.py", label="Lavadas del día", icon="📋")

    with col4:
        st.page_link("pages/3_Cierre_Del_Dia.py", label="Cierre del día", icon="💰")

    with col5:
        st.page_link("pages/4_Historial_General.py", label="Historial", icon="📊")

    st.divider()