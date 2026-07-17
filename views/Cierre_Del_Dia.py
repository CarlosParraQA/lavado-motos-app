import streamlit as st
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

from database import (
    obtener_lavados,
    guardar_gasto,
    obtener_gastos_fecha,
    eliminar_gasto,
    supabase
)
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


def obtener_pago_realizado(pagos_realizados, empleado, fecha):
    """
    Retorna el pago guardado en Supabase para ese colaborador y fecha.
    Si no existe, retorna None.
    """

    for pago in pagos_realizados:
        if pago.get("empleado") == empleado and pago.get("fecha") == fecha:
            return pago

    return None


def pago_ya_realizado(pagos_realizados, empleado, fecha):
    return obtener_pago_realizado(pagos_realizados, empleado, fecha) is not None


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


def abrir_confirmacion_pago(registro):
    @st.dialog("Confirmar pago")
    def confirmar():
        st.warning("Vas a registrar este pago como realizado.")

        st.write(f"**Empleado:** {registro['empleado']}")
        st.write(f"**Rol:** {registro['rol']}")
        st.write(f"**Fecha:** {registro['fecha']}")
        st.write(f"**Servicios realizados:** {registro['cantidad_servicios']}")
        st.write(f"**Total realizado:** {formato_pesos(registro['total_realizado'])}")

        if registro.get("porcentaje_pago") is not None:
            st.write(f"**Porcentaje aplicado:** {registro['porcentaje_pago']}%")

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


def calcular_porcentaje_desde_pago(total_realizado, valor_pagado):
    """
    Calcula el porcentaje aproximado según el valor realmente pagado.
    Sirve para mostrar 50% después de recargar la página.
    """

    try:
        total_realizado = int(total_realizado)
        valor_pagado = int(valor_pagado)

        if total_realizado <= 0:
            return 0

        porcentaje = round((valor_pagado / total_realizado) * 100)

        return porcentaje

    except Exception:
        return 40


def abrir_formulario_gasto(fecha):
    @st.dialog("Registrar gasto")
    def formulario_gasto():
        st.caption(
            f"El gasto quedará registrado para la fecha {fecha}."
        )

        concepto = st.text_input(
            "Concepto del gasto",
            placeholder="Ejemplo: Compra de jabón"
        )

        categoria = st.selectbox(
            "Categoría",
            [
                "Insumos",
                "Mantenimiento",
                "Servicios",
                "Transporte",
                "Alimentación",
                "Nómina",
                "Otro"
            ]
        )

        valor = st.number_input(
            "Valor del gasto",
            min_value=0,
            step=1000,
            format="%d"
        )

        metodo_pago = st.selectbox(
            "Método de pago",
            [
                "Efectivo",
                "Nequi",
                "Daviplata",
                "Transferencia",
                "Otro"
            ]
        )

        observaciones = st.text_area(
            "Observaciones",
            placeholder="Información adicional del gasto"
        )

        col_guardar, col_cancelar = st.columns(2)

        with col_guardar:
            if st.button(
                "Guardar gasto",
                type="primary",
                use_container_width=True
            ):
                if not concepto.strip():
                    st.warning(
                        "Debes escribir el concepto del gasto."
                    )
                    return

                if valor <= 0:
                    st.warning(
                        "El valor debe ser mayor a cero."
                    )
                    return

                try:
                    guardar_gasto(
                        fecha=fecha,
                        concepto=concepto,
                        categoria=categoria,
                        valor=valor,
                        metodo_pago=metodo_pago,
                        observaciones=observaciones
                    )

                    st.success(
                        "Gasto registrado correctamente."
                    )

                    st.rerun()

                except Exception as error:
                    st.error(
                        "No se pudo registrar el gasto."
                    )
                    st.exception(error)

        with col_cancelar:
            if st.button(
                "Cancelar",
                use_container_width=True
            ):
                st.rerun()

    formulario_gasto()

def abrir_confirmacion_eliminar_gasto(gasto):
    @st.dialog("Eliminar gasto")
    def confirmar_eliminacion():
        st.warning(
            "¿Estás seguro de eliminar este gasto?"
        )

        st.write(
            f"**Concepto:** {gasto.get('concepto', '')}"
        )

        st.write(
            f"**Valor:** {formato_pesos(int(gasto.get('valor', 0) or 0))}"
        )

        col_eliminar, col_cancelar = st.columns(2)

        with col_eliminar:
            if st.button(
                "Eliminar",
                type="primary",
                use_container_width=True
            ):
                try:
                    eliminar_gasto(gasto["id"])

                    st.success(
                        "Gasto eliminado correctamente."
                    )

                    st.rerun()

                except Exception as error:
                    st.error(
                        "No se pudo eliminar el gasto."
                    )
                    st.exception(error)

        with col_cancelar:
            if st.button(
                "Cancelar",
                use_container_width=True
            ):
                st.rerun()

    confirmar_eliminacion()



def mostrar_cierre_del_dia():
    st.header("Pagos a Colaboradores y Cierre de Caja")
    st.caption(
        "Consulta lo realizado por cada colaborador y registra el pago correspondiente."
    )

    fecha_hoy = datetime.now(ZoneInfo("America/Bogota")).date()

    fecha_seleccionada = st.date_input(
        "Selecciona la fecha a pagar",
        value=fecha_hoy
    )

    fecha_texto = fecha_seleccionada.strftime("%Y-%m-%d")

    usuario_actual = st.session_state.get(
        "usuario",
        ""
    ).strip().lower()

    usuarios_autorizados_pago = [
        "admin",
        "socio"
    ]

    puede_gestionar_pagos = (
        usuario_actual in usuarios_autorizados_pago
    )

# =========================
# MÓDULO DE GASTOS
# =========================

    st.divider()

    col_titulo_gastos, col_boton_gastos = st.columns(
        [3, 1]
    )

    with col_titulo_gastos:
        st.subheader("Gastos del día")
        st.caption(
            "Registra y consulta los gastos correspondientes a la fecha seleccionada."
        )

    with col_boton_gastos:
        if puede_gestionar_pagos:
            if st.button(
                "➕ Registrar gasto",
                use_container_width=True
            ):
                abrir_formulario_gasto(fecha_texto)
        else:
            st.button(
                "Sin permiso",
                disabled=True,
                use_container_width=True,
                key="sin_permiso_gastos"
            )

    gastos_fecha = obtener_gastos_fecha(fecha_texto)

    total_gastos = sum(
        int(gasto.get("valor", 0) or 0)
        for gasto in gastos_fecha
    )

    st.metric(
        "Total de gastos",
        formato_pesos(total_gastos)
    )

    if not gastos_fecha:
        st.info(
            "No hay gastos registrados para esta fecha."
        )

    else:
        for gasto in gastos_fecha:
            concepto = gasto.get(
                "concepto",
                "Sin concepto"
            )

            categoria = gasto.get(
                "categoria",
                "Sin categoría"
            )

            valor = int(
                gasto.get("valor", 0) or 0
            )

            metodo_pago = gasto.get(
                "metodo_pago",
                "Sin información"
            )

            hora = gasto.get(
                "hora",
                ""
            )

            observaciones = gasto.get(
                "observaciones",
                ""
            )

            registrado_por = gasto.get(
                "registrado_por",
                ""
            )

            # IMPORTANTE:
            # Todo este bloque debe quedar dentro del for
            with st.container(border=True):

                col_info, col_valor, col_accion = st.columns(
                    [5, 1.5, 1.5],
                    vertical_alignment="center"
                )

                with col_info:
                    st.markdown(
                        f"### {concepto}"
                    )

                    detalles = []

                    if categoria:
                        detalles.append(
                            f"**Categoría:** {categoria}"
                        )

                    if metodo_pago:
                        detalles.append(
                            f"**Método de pago:** {metodo_pago}"
                        )

                    if hora:
                        detalles.append(
                            f"**Hora:** {hora}"
                        )

                    st.markdown(
                        " · ".join(detalles)
                    )

                    if observaciones:
                        st.caption(
                            f"Observaciones: {observaciones}"
                        )

                    if registrado_por:
                        st.caption(
                            f"Registrado por: {registrado_por}"
                        )

                with col_valor:
                    st.markdown(
                        f"""
                        <div style="
                            text-align: center;
                            font-size: 26px;
                            font-weight: 700;
                            padding-top: 8px;
                        ">
                            {formato_pesos(valor)}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with col_accion:
                    if puede_gestionar_pagos:
                        if st.button(
                            "🗑️ Eliminar",
                            key=f"eliminar_gasto_{gasto['id']}",
                            use_container_width=True
                        ):
                            abrir_confirmacion_eliminar_gasto(
                                gasto
                            )

    st.divider()

    es_domingo = fecha_seleccionada.weekday() == 6

    if puede_gestionar_pagos and es_domingo:
        st.success(
            "Puedes cambiar el porcentaje de pago de cada colaborador de forma individual."
        )

    elif puede_gestionar_pagos and not es_domingo:
        st.warning(
            "Solo los domingos se cambia el porcentaje de pago. Para esta fecha se aplica el 40%."
        )

    else:
        st.warning(
            "No tienes permiso para cambiar el porcentaje de pago. Solo admin o socio pueden hacerlo los domingos."
        )

    df = obtener_lavados()

    if df.empty:
        st.warning("Todavía no hay lavadas registradas.")
        return

    df["fecha"] = df["fecha"].astype(str)

    df_fecha = df[df["fecha"] == fecha_texto].copy()

    pagos_realizados = obtener_pagos_fecha(fecha_texto)

    nombre_operador = "Encargado"

    registros_pago = []

    if not df_fecha.empty:
        resumen = (
            df_fecha
            .groupby("gamusero")
            .agg(
                cantidad_servicios=("id", "count"),
                total_realizado=("valor_lavada", "sum")
            )
            .reset_index()
        )

        resumen = resumen.rename(columns={
            "gamusero": "empleado"
        })

        resumen["rol"] = "Gamusero"
        resumen["porcentaje_pago"] = 40
        resumen["valor_pagar"] = (
            resumen["total_realizado"] * 0.40
        ).round(0).astype(int)

        registros_pago = resumen.to_dict("records")

    else:
        st.warning("No hay lavadas registradas para esta fecha.")

    registros_pago.append({
        "empleado": nombre_operador,
        "rol": "Encargado",
        "cantidad_servicios": 0,
        "total_realizado": 0,
        "valor_pagar": PAGO_FIJO_OPERADOR,
        "porcentaje_pago": None
    })

    # =========================
    # APLICAR PAGOS GUARDADOS
    # =========================
    # Esta es la parte importante:
    # Si ya se pagó, toma el valor real guardado en Supabase.
    # Así, si pagaste 50%, al recargar no vuelve al 40%.

    for item in registros_pago:
        empleado = item["empleado"]
        rol = item["rol"]

        pago_guardado = obtener_pago_realizado(
            pagos_realizados,
            empleado,
            fecha_texto
        )

        if pago_guardado:
            item["cantidad_servicios"] = int(
                pago_guardado.get("cantidad_servicios", item["cantidad_servicios"]) or 0
            )

            item["total_realizado"] = int(
                pago_guardado.get("total_realizado", item["total_realizado"]) or 0
            )

            item["valor_pagar"] = int(
                pago_guardado.get("valor_pagar", item["valor_pagar"]) or 0
            )

            if rol == "Gamusero":
                item["porcentaje_pago"] = calcular_porcentaje_desde_pago(
                    item["total_realizado"],
                    item["valor_pagar"]
                )

        else:
            if rol == "Gamusero":
                key_porcentaje = f"porcentaje_pago_{empleado}_{fecha_texto}"

                porcentaje_guardado = int(
                    st.session_state.get(key_porcentaje, 40)
                )

                if porcentaje_guardado not in [40, 50]:
                    porcentaje_guardado = 40

                if puede_gestionar_pagos and es_domingo:
                    porcentaje_individual = porcentaje_guardado
                else:
                    porcentaje_individual = 40

                item["porcentaje_pago"] = porcentaje_individual
                item["valor_pagar"] = int(
                    round(
                        int(item["total_realizado"]) *
                        (porcentaje_individual / 100)
                    )
                )

    total_vendido = 0

    if not df_fecha.empty:
        total_vendido = int(
            df_fecha["valor_lavada"].sum()
        )

    total_pagos_realizados = sum(
        int(pago.get("valor_pagar", 0) or 0)
        for pago in pagos_realizados
    )

    saldo_caja = (
        total_vendido
        - total_pagos_realizados
        - total_gastos
    )

    st.subheader("Resumen de caja")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total vendido",
            formato_pesos(total_vendido)
        )

    with col2:
        st.metric(
            "Pagos realizados",
            formato_pesos(total_pagos_realizados)
        )

    with col3:
        st.metric(
            "Gastos",
            formato_pesos(total_gastos)
        )

    with col4:
        st.metric(
            "Saldo de caja",
            formato_pesos(saldo_caja)
        )

    st.divider()

    st.subheader("Detalle de pago por colaborador")

    for registro in registros_pago:
        empleado = registro["empleado"]
        rol = registro["rol"]
        cantidad_servicios = int(registro["cantidad_servicios"])
        total_realizado_empleado = int(registro["total_realizado"])
        valor_pagar = int(registro["valor_pagar"])
        porcentaje_pago = registro.get("porcentaje_pago")

        pago_guardado = obtener_pago_realizado(
            pagos_realizados,
            empleado,
            fecha_texto
        )

        ya_pagado = pago_guardado is not None

        with st.container(border=True):
            col_info, col_estado, col_accion = st.columns([2, 1, 1])

            with col_info:
                st.markdown(f"### {empleado}")
                st.write(f"**Rol:** {rol}")
                st.write(f"**Servicios realizados:** {cantidad_servicios}")
                st.write(
                    f"**Total realizado:** {formato_pesos(total_realizado_empleado)}"
                )

                if rol == "Gamusero":
                    key_porcentaje = f"porcentaje_pago_{empleado}_{fecha_texto}"

                    if ya_pagado:
                        st.write(
                            f"**Porcentaje aplicado:** {int(porcentaje_pago or 40)}%"
                        )

                    elif puede_gestionar_pagos and es_domingo:
                        valor_actual = int(porcentaje_pago or 40)

                        if valor_actual not in [40, 50]:
                            valor_actual = 40

                        porcentaje_pago = st.selectbox(
                            "Porcentaje a pagar",
                            options=[40, 50],
                            index=[40, 50].index(valor_actual),
                            key=key_porcentaje,
                            help="Este porcentaje aplica solo para este empleado."
                        )

                        valor_pagar = int(
                            round(
                                total_realizado_empleado *
                                (int(porcentaje_pago) / 100)
                            )
                        )

                    else:
                        st.write(
                            f"**Porcentaje aplicado:** {int(porcentaje_pago or 40)}%"
                        )

                st.write(f"**Valor a pagar:** {formato_pesos(valor_pagar)}")

                if ya_pagado:
                    st.caption(
                        "Este valor corresponde al pago realmente guardado en el sistema."
                    )

            with col_estado:
                if ya_pagado:
                    st.success("Pagado")
                else:
                    st.warning("Pendiente")

            with col_accion:
                puede_pagar = puede_gestionar_pagos

                if ya_pagado:
                    st.button(
                        "Pagado",
                        disabled=True,
                        use_container_width=True,
                        key=f"pagado_{empleado}_{fecha_texto}"
                    )

                elif not puede_pagar:
                    st.button(
                        "Sin permiso",
                        disabled=True,
                        use_container_width=True,
                        key=f"sin_permiso_{empleado}_{fecha_texto}"
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
                            "valor_pagar": valor_pagar,
                            "porcentaje_pago": porcentaje_pago
                        }

                        abrir_confirmacion_pago(registro_confirmacion)