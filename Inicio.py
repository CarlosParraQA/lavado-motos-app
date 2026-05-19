import streamlit as st
from database import crear_tabla
from auth import login, logout


st.set_page_config(
    page_title="Registro Lavado de Motos",
    page_icon="🏍️",
    layout="wide"
)

login()
logout()

crear_tabla()

st.title("🏍️ Registro de Lavado de Motos - Moto Space Wash")
st.caption("Control de lavadas por gamusero y cálculo automático del 40% diario.")

st.info(
    """
    Bienvenido al sistema de registro de lavadas.

    Usa el menú lateral para:
    - Registrar una lavada.
    - Ver las lavadas del día.
    - Hacer el cierre diario.
    - Consultar el historial general.
    """
)
