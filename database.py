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

def guardar_lavada(
    gamusero,
    placa,
    valor_lavada,
    observaciones,
    coin=False,
    nombre_cliente="",
    telefono_cliente=""
):
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
        "nombre_cliente": nombre_cliente,
        "telefono_cliente": telefono_cliente,
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
# OPERADORES / GAMUSEROS
# =========================

def obtener_operadores():
    """
    Obtiene la lista de operadores activos desde Supabase.
    """

    try:
        response = (
            supabase
            .table("operadores")
            .select("nombre")
            .eq("activo", True)
            .order("nombre")
            .execute()
        )

        data = response.data or []

        return [
            item["nombre"]
            for item in data
            if item.get("nombre")
        ]

    except Exception:
        return []


def guardar_operador(nombre_operador):
    """
    Guarda un operador en Supabase.
    Si ya existe, no lo duplica.
    """

    nombre_operador = nombre_operador.strip().title()

    if not nombre_operador:
        return

    existente = (
        supabase
        .table("operadores")
        .select("id, nombre")
        .ilike("nombre", nombre_operador)
        .execute()
    )

    if existente.data:
        id_operador = existente.data[0]["id"]

        supabase.table("operadores").update({
            "activo": True
        }).eq("id", id_operador).execute()

    else:
        supabase.table("operadores").insert({
            "nombre": nombre_operador,
            "activo": True
        }).execute()


def obtener_operadores_admin():
    """Obtiene operadores activos e inactivos para su administración."""

    response = (
        supabase
        .table("operadores")
        .select("id, nombre, activo")
        .order("nombre")
        .execute()
    )

    return response.data or []


def actualizar_operador(id_operador, nuevo_nombre):
    """Actualiza el nombre de un operador sin alterar el historial de lavadas."""

    nuevo_nombre = nuevo_nombre.strip().title()
    if not nuevo_nombre:
        raise ValueError("El nombre del lavador no puede estar vacío.")

    existentes = obtener_operadores_admin()
    duplicado = any(
        int(operador["id"]) != int(id_operador)
        and str(operador.get("nombre") or "").strip().casefold()
        == nuevo_nombre.casefold()
        for operador in existentes
    )
    if duplicado:
        raise ValueError("Ya existe un lavador con ese nombre.")

    supabase.table("operadores").update({
        "nombre": nuevo_nombre
    }).eq("id", int(id_operador)).execute()


def reactivar_operador(id_operador):
    """Vuelve a habilitar un operador previamente retirado."""

    supabase.table("operadores").update({
        "activo": True
    }).eq("id", int(id_operador)).execute()


def eliminar_operador(id_operador):
    """Elimina definitivamente un operador, sin alterar lavadas históricas."""

    supabase.table("operadores").delete().eq("id", int(id_operador)).execute()


def obtener_precios_lavada(solo_activos=True):
    """Obtiene los precios configurados para registrar lavadas."""

    query = (
        supabase
        .table("precios_lavada")
        .select("id, valor, activo")
    )
    if solo_activos:
        query = query.eq("activo", True)

    response = query.order("valor").execute()
    return response.data or []


def guardar_precio_lavada(valor):
    """Agrega un precio disponible para nuevas lavadas."""

    valor = int(valor)
    if valor <= 0:
        raise ValueError("El precio debe ser mayor que cero.")

    supabase.table("precios_lavada").insert({
        "valor": valor,
        "activo": True
    }).execute()


def actualizar_precio_lavada(id_precio, valor):
    """Actualiza un precio configurado."""

    valor = int(valor)
    if valor <= 0:
        raise ValueError("El precio debe ser mayor que cero.")

    supabase.table("precios_lavada").update({
        "valor": valor
    }).eq("id", int(id_precio)).execute()


def eliminar_precio_lavada(id_precio):
    """Elimina definitivamente un precio, sin alterar lavadas históricas."""

    precios_activos = obtener_precios_lavada()
    precio_actual = next(
        (
            precio
            for precio in precios_activos
            if int(precio["id"]) == int(id_precio)
        ),
        None
    )

    if precio_actual and len(precios_activos) <= 1:
        raise ValueError("Debe quedar al menos un precio disponible.")

    supabase.table("precios_lavada").delete().eq("id", int(id_precio)).execute()


def reactivar_precio_lavada(id_precio):
    """Vuelve a habilitar un precio previamente retirado."""

    supabase.table("precios_lavada").update({
        "activo": True
    }).eq("id", int(id_precio)).execute()


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


# =========================
# GASTOS
# =========================

def guardar_gasto(
    fecha,
    concepto,
    categoria,
    valor,
    metodo_pago,
    observaciones=""
):
    """
    Registra un gasto en Supabase.
    """

    usuario_actual = st.session_state.get(
        "usuario",
        "Sin usuario"
    )

    fecha_hora_colombia = datetime.now(
        ZoneInfo("America/Bogota")
    )

    data = {
        "fecha": str(fecha),
        "hora": fecha_hora_colombia.strftime("%H:%M:%S"),
        "concepto": concepto.strip(),
        "categoria": categoria,
        "valor": int(valor),
        "metodo_pago": metodo_pago,
        "observaciones": observaciones.strip(),
        "registrado_por": usuario_actual
    }

    supabase.table("gastos").insert(data).execute()


def obtener_gastos_fecha(fecha):
    """
    Obtiene los gastos registrados para una fecha.
    """

    try:
        response = (
            supabase
            .table("gastos")
            .select("*")
            .eq("fecha", str(fecha))
            .order("hora", desc=True)
            .execute()
        )

        return response.data or []

    except Exception:
        return []


def eliminar_gasto(id_gasto):
    """
    Elimina un gasto por su ID.
    """

    supabase.table("gastos").delete().eq(
        "id",
        int(id_gasto)
    ).execute()

def obtener_lavados_por_rango(fecha_inicio, fecha_fin):
    """
    Consulta directamente en Supabase las lavadas del rango
    seleccionado y pagina los resultados para evitar el
    límite predeterminado de 1000 registros.
    """

    fecha_inicio_texto = fecha_inicio.strftime("%Y-%m-%d")
    fecha_fin_texto = fecha_fin.strftime("%Y-%m-%d")

    registros = []

    tamano_pagina = 1000
    desde = 0

    while True:
        hasta = desde + tamano_pagina - 1

        response = (
            supabase
            .table("lavados")
            .select("*")
            .gte("fecha", fecha_inicio_texto)
            .lte("fecha", fecha_fin_texto)
            .order("id", desc=False)
            .range(desde, hasta)
            .execute()
        )

        lote = response.data or []

        registros.extend(lote)

        if len(lote) < tamano_pagina:
            break

        desde += tamano_pagina

    return pd.DataFrame(registros)