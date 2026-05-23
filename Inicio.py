import streamlit as st

st.set_page_config(
    page_title="Moto Space Wash",
    page_icon="🏍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from database import crear_tabla
from auth import login
from navbar import aplicar_estilos, navbar

from views.Registrar_Lavada import mostrar_registrar_lavada
from views.Lavadas_Del_Dia import mostrar_lavadas_del_dia
from views.Cierre_Del_Dia import mostrar_cierre_del_dia
from views.Historial_General import mostrar_historial_general


login()

aplicar_estilos()
navbar()

crear_tabla()

vista = st.session_state.get("vista", "Inicio")

if vista == "Inicio":
    st.title("🏍️ Registro de Lavado de Motos - Moto Space Wash")
    st.caption("Control de lavadas por gamusero y cálculo automático del 40% diario.")

    st.info(
        """
        Bienvenido al sistema de registro de lavadas.

        Usa el menú superior para:
        - Registrar una lavada.
        - Ver las lavadas del día.
        - Hacer el cierre diario.
        - Consultar el historial general.
        """
    )

elif vista == "Registrar":
    mostrar_registrar_lavada()

elif vista == "Lavadas":
    mostrar_lavadas_del_dia()

elif vista == "Cierre":
    mostrar_cierre_del_dia()

elif vista == "Historial":
    mostrar_historial_general()