import streamlit as st
import pandas as pd
from database import guardar_lavada
from utils import formato_pesos


def mostrar_registrar_lavada():
    st.header("Registrar nueva lavada")

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

    pago_calculado = int(valor_lavada * 0.40)
    ganancia_calculada = int(valor_lavada * 0.60)

    resumen_lavada = pd.DataFrame({
        "Valor lavada": [formato_pesos(valor_lavada)],
        "40% gamusero": [formato_pesos(pago_calculado)],
        "60% negocio": [formato_pesos(ganancia_calculada)]
    })

    st.subheader("Resumen de la lavada")
    st.table(resumen_lavada.style.hide(axis="index"))

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