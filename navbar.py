import base64
from pathlib import Path

import streamlit as st

from auth import cerrar_sesion


# =========================================================
# CARGAR LOGO
# =========================================================

def cargar_logo_base64(ruta_logo="assets/logo.png"):
    """
    Convierte el logo en Base64 para mostrarlo dentro del encabezado.
    Si el archivo no existe, retorna una cadena vacía.
    """

    logo_path = Path(ruta_logo)

    if not logo_path.exists():
        return ""

    with open(logo_path, "rb") as archivo:
        return base64.b64encode(archivo.read()).decode("utf-8")


# =========================================================
# ESTILOS GENERALES
# =========================================================

def aplicar_estilos():
    st.markdown(
        """
        <style>
            /* Ocultar sidebar y encabezado nativo de Streamlit */
            [data-testid="stSidebar"] {
                display: none !important;
            }

            [data-testid="collapsedControl"] {
                display: none !important;
            }

            header[data-testid="stHeader"] {
                display: none !important;
            }

            /* Contenedor principal */
            .block-container {
                max-width: 96% !important;
                padding-top: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            /* Encabezado principal */
            .header-card {
                border: 1px solid #374151;
                border-radius: 14px;
                padding: 10px 14px;
                margin-bottom: 8px;
                background-color: transparent;
                min-height: 88px;
                display: flex;
                align-items: center;
            }

            .header-brand {
                display: flex;
                align-items: center;
                gap: 12px;
                width: 100%;
            }

            .header-logo {
                width: 68px;
                height: 68px;
                object-fit: contain;
                flex-shrink: 0;
            }

            .header-text {
                display: flex;
                flex-direction: column;
                justify-content: center;
            }

            .navbar-title {
                font-size: 30px;
                font-weight: 800;
                color: white;
                margin: 0;
                line-height: 1.1;
            }

            .navbar-subtitle {
                font-size: 16px;
                color: #9ca3af;
                margin-top: 3px;
                line-height: 1.2;
            }

            /* Información del usuario */
            .user-box {
                font-size: 18px;
                color: #e5e7eb;
                font-weight: 800;
                text-align: center;
                min-height: 42px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 6px;
                white-space: nowrap;
                border: 1px solid #374151;
                border-radius: 12px;
                padding: 8px 12px;
                background-color: transparent;
            }

            /* Botones generales */
            div[data-testid="stButton"] > button {
                background-color: #374151 !important;
                color: white !important;
                border-radius: 12px !important;
                border: 1px solid #374151 !important;
                min-height: 54px !important;
                padding: 12px 18px !important;
                width: 100% !important;
            }

            div[data-testid="stButton"] > button:hover {
                background-color: #4b5563 !important;
                border-color: #6b7280 !important;
            }

            /* Texto interno de los botones */
            div[data-testid="stButton"] > button p,
            div[data-testid="stButton"] > button span {
                font-size: 18px !important;
                font-weight: 900 !important;
                line-height: 1.1 !important;
            }

            /* Diseño para dispositivos móviles */
            @media (max-width: 768px) {
                .block-container {
                    max-width: 100% !important;
                    padding-top: 0.7rem !important;
                    padding-left: 0.7rem !important;
                    padding-right: 0.7rem !important;
                }

                .header-card {
                    padding: 8px 10px !important;
                    min-height: 74px !important;
                    margin-bottom: 6px !important;
                }

                .header-brand {
                    gap: 8px !important;
                }

                .header-logo {
                    width: 54px !important;
                    height: 54px !important;
                }

                .navbar-title {
                    font-size: 20px !important;
                    line-height: 1.1 !important;
                    white-space: nowrap;
                }

                .navbar-subtitle {
                    font-size: 11px !important;
                    line-height: 1.2 !important;
                }

                .user-box {
                    font-size: 12px !important;
                    padding: 6px 6px !important;
                    min-height: 34px !important;
                    margin-bottom: 4px !important;
                }

                div[data-testid="stButton"] > button {
                    min-height: 42px !important;
                    padding: 8px 8px !important;
                }

                div[data-testid="stButton"] > button p,
                div[data-testid="stButton"] > button span {
                    font-size: 13px !important;
                    font-weight: 800 !important;
                }
            }
            /* =========================
   BOTÓN DESCARGAR EXCEL
========================= */

div.st-key-descargar_historial_excel
div[data-testid="stDownloadButton"] > button {
    background-color: #16a34a !important;
    color: white !important;
    border: 1px solid #16a34a !important;
    border-radius: 12px !important;
    min-height: 56px !important;
    padding: 12px 24px !important;
    font-size: 19px !important;
    font-weight: 900 !important;
}

div.st-key-descargar_historial_excel
div[data-testid="stDownloadButton"] > button:hover {
    background-color: #15803d !important;
    border-color: #15803d !important;
    color: white !important;
    transform: scale(1.02);
}

div.st-key-descargar_historial_excel
div[data-testid="stDownloadButton"] > button p,
div.st-key-descargar_historial_excel
div[data-testid="stDownloadButton"] > button span {
    font-size: 19px !important;
    font-weight: 900 !important;
}
        </style>
        """,
        unsafe_allow_html=True
    )


# =========================================================
# BARRA DE NAVEGACIÓN
# =========================================================

def navbar():
    """
    Muestra el encabezado y las opciones de navegación según el rol.

    Admin y socio:
        - Inicio
        - Registrar
        - Servicios del día
        - Cierre de caja

    Operador:
        - Registrar
        - Servicios del día
        - Cierre de caja
    """

    usuario_actual = (
        st.session_state
        .get("usuario", "")
        .strip()
        .lower()
    )

    # Primero intenta obtener el rol guardado.
    # Si está vacío, utiliza el nombre del usuario como rol.
    rol_actual = (
        st.session_state.get("rol")
        or usuario_actual
    ).strip().lower()

    # Guardamos nuevamente el rol para mantenerlo disponible.
    st.session_state.rol = rol_actual

    # Validar que el usuario tenga un rol permitido.
    roles_validos = ["admin", "socio", "operador"]

    if rol_actual not in roles_validos:
        st.error(
            "El usuario no tiene un rol válido. "
            "Cierra sesión e ingresa nuevamente."
        )

        if st.button(
            "Cerrar sesión",
            use_container_width=True,
            key="cerrar_sesion_rol_invalido"
        ):
            cerrar_sesion()

        st.stop()

    logo_base64 = cargar_logo_base64("assets/logo.png")

    if logo_base64:
        logo_html = (
            f'<img src="data:image/png;base64,{logo_base64}" '
            f'class="header-logo">'
        )
    else:
        logo_html = """
            <div
                class="header-logo"
                style="
                    font-size: 42px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                "
            >
                🏍️
            </div>
        """

    # =====================================================
    # ENCABEZADO SUPERIOR
    # =====================================================

    col_logo, col_usuario = st.columns([4, 1.35])

    with col_logo:
        st.markdown(
            f"""
    <div class="header-card">
        <div class="header-brand">
            {logo_html}
            <div class="header-text">
                <div class="navbar-title">Moto Space Wash</div>
                <div class="navbar-subtitle">
                    Sistema de registro de lavadas
                </div>
            </div>
        </div>
    </div>
    """,
            unsafe_allow_html=True
        )

    with col_usuario:
        st.markdown(
            f"""
            <div class="user-box">
                👤 {usuario_actual.capitalize()}
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Cerrar sesión",
            use_container_width=True,
            key="boton_cerrar_sesion"
        ):
            cerrar_sesion()

    # =====================================================
    # OPCIONES SEGÚN EL ROL
    # =====================================================

    if rol_actual in ["admin", "socio"]:
        opciones = {
            "Inicio": "Inicio",
            "Registrar": "Registrar Nuevo Servicio",
            "Lavadas": "Servicios del Día",
            "Cierre": "Pagos y Cierre de Caja"
        }

        proporciones_columnas = [
            1.2,
            1.8,
            1.8,
            2.2
        ]

    else:
        opciones = {
            "Registrar": "Registrar Nuevo Servicio",
            "Lavadas": "Servicios del Día",
            "Cierre": "Pagos y Cierre de Caja"
        }

        proporciones_columnas = [
            1.8,
            1.8,
            2.2
        ]

    # =====================================================
    # DEFINIR VISTA INICIAL
    # =====================================================

    if "vista" not in st.session_state:
        if rol_actual == "operador":
            st.session_state.vista = "Registrar"
        else:
            st.session_state.vista = "Inicio"

    # Si el operador quedó anteriormente en Inicio,
    # se redirige automáticamente a Registrar.
    if (
        rol_actual == "operador"
        and st.session_state.get("vista") == "Inicio"
    ):
        st.session_state.vista = "Registrar"

    # Si admin o socio tienen una vista inexistente,
    # se envían nuevamente al Inicio.
    if (
        rol_actual in ["admin", "socio"]
        and st.session_state.get("vista") not in opciones
    ):
        st.session_state.vista = "Inicio"

    # Si el operador tiene una vista que no le corresponde,
    # se envía a Registrar.
    if (
        rol_actual == "operador"
        and st.session_state.get("vista") not in opciones
    ):
        st.session_state.vista = "Registrar"

    # =====================================================
    # BOTONES DE NAVEGACIÓN
    # =====================================================

    columnas = st.columns(proporciones_columnas)

    for columna, (clave, etiqueta) in zip(
        columnas,
        opciones.items()
    ):
        with columna:
            if st.button(
                etiqueta,
                use_container_width=True,
                key=f"nav_{clave}"
            ):
                st.session_state.vista = clave
                st.rerun()

    st.divider()