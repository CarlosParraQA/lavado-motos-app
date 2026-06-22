import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo
from supabase import create_client

# =========================
# CONEXIÓN A SUPABASE
# =========================

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# CREAR TABLA
# =========================

def crear_tabla():
    """
    La tabla ya fue creada en Supabase.
    Esta función queda vacía para que Inicio.py no genere error.
    """
    pass


# =========================
# GUARDAR LAVADA
# =========================

def guardar_lavada(gamusero, placa, valor_lavada, observaciones, coin=False):
    """
    Guarda una lavada en Supabase.
    Calcula automáticamente el 40% para el gamusero
    y el 60% para el negocio.
    """

    fecha_hora_colombia = datetime.now(ZoneInfo("America/Bogota"))

    fecha_actual = fecha_hora_colombia.strftime("%Y-%m-%d")
    hora_actual = fecha_hora_colombia.strftime("%H:%M:%S")

    pago_gamusero = int(valor_lavada * 0.40)
    ganancia_negocio = int(valor_lavada * 0.60)

    data = {
        "fecha": fecha_actual,
        "hora": hora_actual,
        "gamusero": gamusero,
        "placa": placa,
        "valor_lavada": valor_lavada,
        "pago_gamusero": pago_gamusero,
        "ganancia_negocio": ganancia_negocio,
        "observaciones": observaciones,
        "coin": bool(coin),
    }

    supabase.table("lavados").insert(data).execute()


# =========================
# OBTENER LAVADOS
# =========================

def obtener_lavados():
    """
    Obtiene todos los registros guardados en Supabase.
    """

    response = (
        supabase
        .table("lavados")
        .select("*")
        .order("fecha", desc=True)
        .order("hora", desc=True)
        .execute()
    )

    data = response.data

    if not data:
        return pd.DataFrame()

    return pd.DataFrame(data)


# =========================
# ELIMINAR REGISTRO
# =========================

def eliminar_registro(id_registro):
    """
    Elimina una lavada de Supabase por ID.
    """

    supabase.table("lavados").delete().eq("id", int(id_registro)).execute()

# =========================
# MODIFICAR REGISTRO
# =========================

def actualizar_nombre_gamusero(id_registro, nuevo_nombre):
    """
    Actualiza el nombre del gamusero/personal en Supabase.
    """

    supabase.table("lavados").update({
        "gamusero": nuevo_nombre
    }).eq("id", int(id_registro)).execute()

def actualizar_coin_lavada(id_registro, coin):
    supabase.table("lavados").update({
        "coin": bool(coin)
    }).eq("id", int(id_registro)).execute()

def actualizar_metodo_pago_lavada(id_registro, metodo_pago):
    supabase.table("lavados").update({
        "metodo_pago": metodo_pago
    }).eq("id", int(id_registro)).execute()

def actualizar_valor_lavada(id_registro, nuevo_valor_lavada):
    """
    Actualiza el valor de la lavada y recalcula automáticamente:
    - 40% para el personal
    - 60% para el negocio
    """

    nuevo_valor_lavada = int(nuevo_valor_lavada)
    pago_gamusero = int(nuevo_valor_lavada * 0.40)
    ganancia_negocio = int(nuevo_valor_lavada * 0.60)

    supabase.table("lavados").update({
        "valor_lavada": nuevo_valor_lavada,
        "pago_gamusero": pago_gamusero,
        "ganancia_negocio": ganancia_negocio
    }).eq("id", int(id_registro)).execute()