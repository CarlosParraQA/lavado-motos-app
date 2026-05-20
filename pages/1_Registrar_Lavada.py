import streamlit as st

st.set_page_config(
    page_title="Lavadas del día",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from navbar import ocultar_sidebar, navbar
from database import guardar_lavada
from utils import formato_pesos
from auth import login, logout

login()

ocultar_sidebar()
navbar()

logout()

st.header("Registrar nueva lavada")

# =========================
# CAMPOS DEL FORMULARIO
# =========================

col1, col2 = st.columns(2)

with col1:
    gamusero = st.text_input("Nombre del Responsable (Gamusero)")
    placa = st.text_input("Placa de la moto")

with col2:
    valor_lavada = st.selectbox(
        "Valor de la lavada",
        [6000, 15000, 20000, 30000, 35000],
        format_func=lambda x: formato_pesos(x)
    )

    observaciones = st.text_area(
        "Observaciones",
        placeholder="Opcional"
    )

# =========================
# CÁLCULOS EN TIEMPO REAL
# =========================

pago_calculado = int(valor_lavada * 0.40)
ganancia_calculada = int(valor_lavada * 0.60)

# =========================
# RESUMEN VISUAL
# =========================

st.write("")

with st.container(border=True):
    st.subheader("Resumen de la lavada")

    col_resumen1, col_resumen2, col_resumen3 = st.columns(3)

    with col_resumen1:
        st.metric(
            label="Valor lavada",
            value=formato_pesos(valor_lavada)
        )

    with col_resumen2:
        st.metric(
            label="40% para gamusero",
            value=formato_pesos(pago_calculado)
        )

    with col_resumen3:
        st.metric(
            label="60% para negocio",
            value=formato_pesos(ganancia_calculada)
        )

# =========================
# GUARDAR REGISTRO
# =========================

st.write("")

if st.button("Guardar lavada", use_container_width=True):
    if not gamusero.strip():
        st.error("Debes ingresar el nombre del gamusero.")
    else:
        guardar_lavada(
            gamusero=gamusero.strip().title(),
            placa=placa.strip().upper(),
            valor_lavada=valor_lavada,
            observaciones=observaciones.strip()
        )

        st.success("Lavada registrada correctamente.")