import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from database import obtener_lavados, supabase
from utils import formato_pesos


PAGO_FIJO_OPERADOR = 60000


def obtener_pagos_fecha(fecha):
    try:
        response = (
            supabase
            .table("pagos_empleados")
            .select("*")
            .eq("fecha", fecha)
            .execute()
        )
        return response.data or []
    except Exception:
        return []


def registrar_pago(fecha, empleado, rol, cantidad_servicios, total_realizado, valor_pagar):
    usuario_actual = st.session_state.get("usuario", "Sin usuario")

    fecha_hora_colombia = datetime.now(ZoneInfo("America/Bogota"))

    data = {
        "fecha": fecha,
        "empleado": empleado,
        "rol": rol,
        "cantidad_servicios": int(cantidad_servicios),
        "total_realizado": int(total_realizado),
        "valor_pagar": int(valor_pagar),
        "pagado_por": usuario_actual,
        "fecha_pago": fecha_hora_colombia.isoformat()
    }

    supabase.table("pagos_empleados").insert(data).execute()


def pago_ya_realizado(pagos_realizados, empleado, fecha):
    for pago in pagos_realizados:
        if pago.get("empleado") == empleado and pago.get("fecha") == fecha:
            return True

    return False


def abrir_confirmacion_pago(registro):
    @st.dialog("Confirmar pago")
    def confirmar():
        st.warning("Vas a registrar este pago como realizado.")

        st.write(f"**Empleado:** {registro['empleado']}")
        st.write(f"**Rol:** {registro['rol']}")
        st.write(f"**Fecha:** {registro['fecha']}")
        st.write(f"**Servicios realizados:** {registro['cantidad_servicios']}")
        st.write(f"**Total realizado:** {formato_pesos(registro['total_realizado'])}")
        st.write(f"**Valor a pagar:** {formato_pesos(registro['valor_pagar'])}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Confirmar pago", use_container_width=True):
                try:
                    registrar_pago(
                        fecha=registro["fecha"],
                        empleado=registro["empleado"],
                        rol=registro["rol"],
                        cantidad_servicios=registro["cantidad_servicios"],
                        total_realizado=registro["total_realizado"],
                        valor_pagar=registro["valor_pagar"]
                    )

                    st.success("Pago registrado correctamente.")
                    st.rerun()

                except Exception as error:
                    st.error("No se pudo registrar el pago.")
                    st.info("Puede que ese empleado ya esté pagado para esta fecha.")
                    st.exception(error)

        with col2:
            if st.button("Cancelar", use_container_width=True):
                st.rerun()

    confirmar()


def mostrar_cierre_del_dia():
    st.header("Pago a empleados")
    st.caption(
        "Consulta lo realizado por cada empleado y registra el pago correspondiente."
    )

    fecha_hoy = datetime.now(ZoneInfo("America/Bogota")).date()

    fecha_seleccionada = st.date_input(
        "Selecciona la fecha a pagar",
        value=fecha_hoy
    )

    fecha_texto = fecha_seleccionada.strftime("%Y-%m-%d")

    df = obtener_lavados()

    if df.empty:
        st.warning("Todavía no hay lavadas registradas.")
        return

    df_fecha = df[df["fecha"] == fecha_texto]

    pagos_realizados = obtener_pagos_fecha(fecha_texto)

    nombre_operador = st.text_input(
        "Nombre del operador",
        value="Operador"
    ).strip().title()

    registros_pago = []

    if not df_fecha.empty:
        resumen = (
            df_fecha
            .groupby("gamusero")
            .agg(
                cantidad_servicios=("id", "count"),
                total_realizado=("valor_lavada", "sum"),
                valor_pagar=("pago_gamusero", "sum")
            )
            .reset_index()
        )

        resumen = resumen.rename(columns={
            "gamusero": "empleado"
        })

        resumen["rol"] = "Gamusero"

        registros_pago = resumen.to_dict("records")
    else:
        st.warning("No hay lavadas registradas para esta fecha.")

    registros_pago.append({
        "empleado": nombre_operador,
        "rol": "Operador",
        "cantidad_servicios": 0,
        "total_realizado": 0,
        "valor_pagar": PAGO_FIJO_OPERADOR
    })

    total_servicios = 0 if df_fecha.empty else int(df_fecha["id"].count())
    total_realizado = sum(int(item["total_realizado"]) for item in registros_pago)
    total_a_pagar = sum(int(item["valor_pagar"]) for item in registros_pago)

    col1, col2, col3 = st.columns(3)

    col1.metric("Servicios del día", total_servicios)
    col2.metric("Total realizado", formato_pesos(total_realizado))
    col3.metric("Total a pagar", formato_pesos(total_a_pagar))

    st.divider()

    st.subheader("Detalle de pago por empleado")

    for registro in registros_pago:
        empleado = registro["empleado"]
        rol = registro["rol"]
        cantidad_servicios = int(registro["cantidad_servicios"])
        total_realizado_empleado = int(registro["total_realizado"])
        valor_pagar = int(registro["valor_pagar"])

        ya_pagado = pago_ya_realizado(
            pagos_realizados,
            empleado,
            fecha_texto
        )

        with st.container(border=True):
            col_info, col_estado, col_accion = st.columns([2, 1, 1])

            with col_info:
                st.markdown(f"### {empleado}")
                st.write(f"**Rol:** {rol}")
                st.write(f"**Servicios realizados:** {cantidad_servicios}")
                st.write(f"**Total realizado:** {formato_pesos(total_realizado_empleado)}")
                st.write(f"**Valor a pagar:** {formato_pesos(valor_pagar)}")

            with col_estado:
                if ya_pagado:
                    st.button(
                        "Pagado",
                        disabled=True,
                        use_container_width=True,
                        key=f"pagado_{empleado}_{fecha_texto}"
                    )
                else:
                    if st.button(
                        "Pagar",
                        use_container_width=True,
                        key=f"pagar_{empleado}_{fecha_texto}"
                    ):
                        registro_confirmacion = {
                            "fecha": fecha_texto,
                            "empleado": empleado,
                            "rol": rol,
                            "cantidad_servicios": cantidad_servicios,
                            "total_realizado": total_realizado_empleado,
                            "valor_pagar": valor_pagar
                        }

                        abrir_confirmacion_pago(registro_confirmacion)