import streamlit as st
import pandas as pd
from database import guardar_lavada, obtener_lavados
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
            [6000, 15000, 20000, 30000, 35000, 60000],
            format_func=lambda x: formato_pesos(x)
        )

        observaciones = st.text_area(
            "Observaciones",
            placeholder="Opcional"
        )

        coin = st.checkbox("¿Se le dio Coin?", value=False)

    pago_calculado = int(valor_lavada * 0.40)
    ganancia_calculada = int(valor_lavada * 0.60)

    resumen_lavada = pd.DataFrame({
        "Valor lavada": [formato_pesos(valor_lavada)],
        "40% gamusero": [formato_pesos(pago_calculado)],
        "60% negocio": [formato_pesos(ganancia_calculada)],
        "Coin": ["Sí" if coin else "No"]
    })

    st.subheader("Resumen de la lavada")
    st.table(resumen_lavada.style.hide(axis="index"))

    if st.button("Guardar lavada", use_container_width=True):
        from datetime import datetime
        from zoneinfo import ZoneInfo

        placa_normalizada = placa.strip().upper()
        gamusero_normalizado = gamusero.strip().title()
        fecha_hoy = datetime.now(ZoneInfo("America/Bogota")).date().strftime("%Y-%m-%d")

        if not gamusero_normalizado:
            st.error("Debes ingresar el nombre del gamusero.")
            return

        if not placa_normalizada:
            st.error("Debes ingresar la placa de la moto.")
            return

        df_lavados = obtener_lavados()

        if not df_lavados.empty:
            df_lavados["fecha"] = df_lavados["fecha"].astype(str)
            df_lavados["placa"] = df_lavados["placa"].astype(str).str.upper().str.strip()

            placa_ya_registrada = df_lavados[
                (df_lavados["fecha"] == fecha_hoy) &
                (df_lavados["placa"] == placa_normalizada)
            ]

            if not placa_ya_registrada.empty:
                st.error(
                    f"La placa {placa_normalizada} ya tiene una lavada registrada hoy. "
                    "No se puede registrar dos veces el mismo día."
                )
                return

        try:
            guardar_lavada(
                gamusero=gamusero_normalizado,
                placa=placa_normalizada,
                valor_lavada=valor_lavada,
                observaciones=observaciones.strip(),
                coin=coin
            )

            st.success("Lavada registrada correctamente.")

        except Exception as error:
            st.error(
                f"No se pudo guardar la lavada. La placa {placa_normalizada} "
                "ya puede estar registrada para el día de hoy."
            )
            st.exception(error)