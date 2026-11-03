import streamlit as st
import pandas as pd
from database import (
    guardar_lavada,
    obtener_lavados,
    obtener_operadores,
    guardar_operador,
    obtener_operadores_admin,
    actualizar_operador,
    desactivar_operador,
    reactivar_operador,
    obtener_precios_lavada,
    guardar_precio_lavada,
    actualizar_precio_lavada,
    desactivar_precio_lavada,
    reactivar_precio_lavada
)
from utils import formato_pesos


def mostrar_administracion():
    st.markdown("### Administración")

    with st.expander("Administrar lavadores y precios", expanded=False):
        st.caption(
            "Los cambios de nombre y precios aplican a nuevos registros; "
            "el historial de lavadas se conserva."
        )

        st.subheader("Lavadores")
        try:
            operadores = obtener_operadores_admin()
        except Exception as error:
            st.error("No se pudo cargar la lista de lavadores.")
            st.exception(error)
            operadores = []

        if operadores:
            operadores_por_id = {
                int(operador["id"]): operador
                for operador in operadores
            }
            id_operador = st.selectbox(
                "Lavador",
                options=list(operadores_por_id),
                format_func=lambda id_actual: (
                    f"{operadores_por_id[id_actual]['nombre']} "
                    f"({'Activo' if operadores_por_id[id_actual]['activo'] else 'Inactivo'})"
                ),
                key="admin_operador_seleccionado"
            )
            operador = operadores_por_id[id_operador]

            with st.form(f"form_editar_operador_{id_operador}"):
                nuevo_nombre = st.text_input(
                    "Nombre",
                    value=operador["nombre"],
                    key=f"nombre_operador_{id_operador}"
                )
                guardar_operador_cambios = st.form_submit_button(
                    "Guardar cambios",
                    use_container_width=True
                )

            if guardar_operador_cambios:
                try:
                    actualizar_operador(id_operador, nuevo_nombre)
                    st.success("Lavador actualizado correctamente.")
                    st.rerun()
                except Exception as error:
                    st.error("No se pudo actualizar el lavador.")
                    st.exception(error)

            if operador["activo"]:
                confirmar_desactivacion = st.checkbox(
                    f"Confirmo retirar a {operador['nombre']} de la lista.",
                    key=f"confirmar_desactivar_operador_{id_operador}"
                )
                if st.button(
                    "Eliminar lavador de la lista",
                    disabled=not confirmar_desactivacion,
                    key=f"desactivar_operador_{id_operador}"
                ):
                    try:
                        desactivar_operador(id_operador)
                        st.success("Lavador retirado de la lista.")
                        st.rerun()
                    except Exception as error:
                        st.error("No se pudo retirar el lavador.")
                        st.exception(error)
            else:
                if st.button(
                    "Reactivar lavador",
                    key=f"reactivar_operador_{id_operador}"
                ):
                    try:
                        reactivar_operador(id_operador)
                        st.success("Lavador reactivado correctamente.")
                        st.rerun()
                    except Exception as error:
                        st.error("No se pudo reactivar el lavador.")
                        st.exception(error)
        else:
            st.info("No hay lavadores registrados para administrar.")

        st.divider()
        st.subheader("Precios de lavadas")
        try:
            precios = obtener_precios_lavada(solo_activos=False)
        except Exception as error:
            st.error(
                "No se pudieron cargar los precios. "
                "Verifica que la tabla precios_lavada esté creada en Supabase."
            )
            st.exception(error)
            precios = []

        if precios:
            precios_por_id = {
                int(precio["id"]): precio
                for precio in precios
            }
            id_precio = st.selectbox(
                "Precio configurado",
                options=list(precios_por_id),
                format_func=lambda id_actual: (
                    f"{formato_pesos(precios_por_id[id_actual]['valor'])} "
                    f"({'Activo' if precios_por_id[id_actual]['activo'] else 'Inactivo'})"
                ),
                key="admin_precio_seleccionado"
            )
            precio = precios_por_id[id_precio]

            with st.form(f"form_editar_precio_{id_precio}"):
                nuevo_precio = st.number_input(
                    "Valor",
                    min_value=1,
                    step=1000,
                    value=int(precio["valor"]),
                    key=f"valor_precio_{id_precio}"
                )
                guardar_precio_cambios = st.form_submit_button(
                    "Guardar precio",
                    use_container_width=True
                )

            if guardar_precio_cambios:
                try:
                    actualizar_precio_lavada(id_precio, nuevo_precio)
                    st.success("Precio actualizado correctamente.")
                    st.rerun()
                except Exception as error:
                    st.error("No se pudo actualizar el precio.")
                    st.exception(error)

            if precio["activo"]:
                confirmar_eliminacion_precio = st.checkbox(
                    f"Confirmo retirar el precio {formato_pesos(precio['valor'])}.",
                    key=f"confirmar_desactivar_precio_{id_precio}"
                )
                if st.button(
                    "Eliminar precio de la lista",
                    disabled=not confirmar_eliminacion_precio,
                    key=f"desactivar_precio_{id_precio}"
                ):
                    try:
                        desactivar_precio_lavada(id_precio)
                        st.success("Precio retirado de la lista.")
                        st.rerun()
                    except Exception as error:
                        st.error("No se pudo retirar el precio.")
                        st.exception(error)
            else:
                if st.button(
                    "Reactivar precio",
                    key=f"reactivar_precio_{id_precio}"
                ):
                    try:
                        reactivar_precio_lavada(id_precio)
                        st.success("Precio reactivado correctamente.")
                        st.rerun()
                    except Exception as error:
                        st.error("No se pudo reactivar el precio.")
                        st.exception(error)
        else:
            st.info("Aún no hay precios configurados.")

        with st.form("form_agregar_precio"):
            precio_nuevo = st.number_input(
                "Agregar precio",
                min_value=1,
                step=1000,
                value=8000,
                key="admin_nuevo_precio"
            )
            agregar_precio = st.form_submit_button(
                "Agregar precio",
                use_container_width=True
            )

        if agregar_precio:
            try:
                guardar_precio_lavada(precio_nuevo)
                st.success("Precio agregado correctamente.")
                st.rerun()
            except Exception as error:
                st.error("No se pudo agregar el precio.")
                st.exception(error)


def mostrar_registrar_lavada():
    st.header("Registrar nueva lavada")

    # =========================
    # MENSAJE AL AGREGAR OPERADOR
    # =========================

    if "mensaje_operador" in st.session_state:
        st.success(st.session_state["mensaje_operador"])
        del st.session_state["mensaje_operador"]

    # =========================
    # AGREGAR OPERADOR
    # =========================

    st.markdown("### 👤 Colaboradores")

    with st.expander("➕ Agregar colaborador a la lista", expanded=False):
        st.info(
            "Agrega el colaborador una sola vez. Luego aparecerá en la lista "
            "para seleccionarlo al registrar nuevas lavadas."
        )

        nuevo_operador = st.text_input(
            "Nombre del nuevo colaborador",
            placeholder="Ejemplo: Juan Pérez",
            key="nuevo_operador"
        )

        if st.button(
            "Guardar colaborador",
            use_container_width=True,
            key="btn_guardar_operador"
        ):
            nuevo_operador_normalizado = nuevo_operador.strip().title()

            if not nuevo_operador_normalizado:
                st.error("Debes ingresar el nombre del operador.")
                return

            try:
                guardar_operador(nuevo_operador_normalizado)

                st.session_state["mensaje_operador"] = (
                    f"Operador {nuevo_operador_normalizado} agregado correctamente."
                )

                st.rerun()

            except Exception as error:
                st.error("No se pudo guardar el operador.")
                st.exception(error)

    rol_actual = (
        st.session_state.get("rol")
        or st.session_state.get("usuario", "")
    ).strip().lower()
    if rol_actual == "admin":
        mostrar_administracion()

    st.divider()

    # =========================
    # FORMULARIO DE REGISTRO
    # =========================

    operadores = obtener_operadores()

    try:
        precios = obtener_precios_lavada()
    except Exception as error:
        st.error("No se pudieron cargar los precios de las lavadas.")
        st.exception(error)
        return

    if not precios:
        st.error(
            "No hay precios disponibles. Pide al administrador que configure "
            "al menos un precio."
        )
        return

    col1, col2 = st.columns(2)

    with col1:
        if operadores:
            gamusero = st.selectbox(
                "Nombre del responsable (Lavador)",
                ["Selecciona un operador"] + operadores
            )
        else:
            gamusero = "Selecciona un operador"
            st.warning("Primero debes agregar al menos un operador a la lista.")

        placa = st.text_input("Placa de la moto")
        nombre_cliente = st.text_input("Nombre del cliente")
        telefono_cliente = st.text_input("Teléfono del cliente")

    with col2:
        valor_lavada = st.selectbox(
            "Valor de la lavada",
            [int(precio["valor"]) for precio in precios],
            format_func=lambda x: formato_pesos(x)
        )

        observaciones = st.text_area(
            "Observaciones",
            placeholder="Opcional"
        )

        coin = st.checkbox("¿Se le dio Coin?", value=False)

    # =========================
    # RESUMEN DE LA LAVADA
    # =========================

    pago_calculado = int(valor_lavada * 0.40)
    ganancia_calculada = int(valor_lavada * 0.60)

    resumen_lavada = pd.DataFrame({
        "Operador": [
            gamusero
            if gamusero != "Selecciona un operador"
            else "Sin seleccionar"
        ],
        "Cliente": [
            nombre_cliente.strip().title()
            if nombre_cliente.strip()
            else "Sin registrar"
        ],
        "Teléfono": [
            telefono_cliente.strip()
            if telefono_cliente.strip()
            else "Sin registrar"
        ],
        "Valor lavada": [formato_pesos(valor_lavada)],
        "40% Lavador": [formato_pesos(pago_calculado)],
        "60% negocio": [formato_pesos(ganancia_calculada)],
        "Coin": ["Sí" if coin else "No"]
    })

    st.subheader("Resumen de la lavada")
    st.table(resumen_lavada.style.hide(axis="index"))

    # =========================
    # GUARDAR LAVADA
    # =========================

    if st.button("Guardar lavada", use_container_width=True):
        from datetime import datetime
        from zoneinfo import ZoneInfo

        placa_normalizada = placa.strip().upper()
        fecha_hoy = datetime.now(ZoneInfo("America/Bogota")).date().strftime("%Y-%m-%d")
        nombre_cliente_normalizado = nombre_cliente.strip().title()
        telefono_cliente_normalizado = telefono_cliente.strip()

        if gamusero == "Selecciona un operador":
            st.error("Debes seleccionar el lavador.")
            return

        gamusero_normalizado = gamusero.strip().title()

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
                coin=coin,
                nombre_cliente=nombre_cliente_normalizado,
                telefono_cliente=telefono_cliente_normalizado
            )

            st.success("Lavada registrada correctamente.")

        except Exception as error:
            st.error(
                f"No se pudo guardar la lavada. La placa {placa_normalizada} "
                "ya puede estar registrada para el día de hoy."
            )
            st.exception(error)