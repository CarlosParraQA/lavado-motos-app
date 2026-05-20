import streamlit as st


def mostrar_cierre_del_dia():
    st.markdown(
        """
        <div style="
            background: linear-gradient(135deg, #1f2937, #111827);
            border: 1px solid #374151;
            border-radius: 18px;
            padding: 36px;
            margin-top: 20px;
            text-align: center;
        ">
            <h1 style="color: #ffffff; margin-bottom: 10px;">
                🚧 Módulo en mantenimiento
            </h1>

            <p style="color: #d1d5db; font-size: 18px; margin-bottom: 6px;">
                Estamos realizando ajustes en esta sección.
            </p>

            <p style="color: #9ca3af; font-size: 15px;">
                Próximamente estará disponible nuevamente el cierre del día.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.info(
        "Mientras esta sección está en mantenimiento, puedes seguir usando las opciones de "
        "**Registrar Lavada**, **Lavadas del Día** e **Historial General**."
    )