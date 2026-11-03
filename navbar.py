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
        return base64.b64encode(
            archivo.read()
        ).decode("utf-8")


# =========================================================
# ESTILOS GENERALES
# =========================================================

def aplicar_estilos():
    st.markdown(
        """
        <style>
            :root {
                --moto-bg: #101113;
                --moto-surface: #1b1d21;
                --moto-surface-raised: #24272c;
                --moto-border: #383c43;
                --moto-text: #f5f5f4;
                --moto-muted: #aaa49d;
                --moto-orange: #f15a24;
                --moto-orange-hover: #ff7338;
                --moto-yellow: #ffc247;
                --moto-success: #45b87a;
                --moto-danger: #ef6a5b;
            }

            html, body, [data-testid="stAppViewContainer"], .stApp {
                background-color: var(--moto-bg) !important;
                color: var(--moto-text) !important;
            }

            [data-testid="stMain"] > div {
                background:
                    radial-gradient(ellipse at 50% -25%, rgba(241, 90, 36, 0.09), transparent 55%),
                    var(--moto-bg);
            }

            [data-testid="stSidebar"] {
                display: none !important;
            }
            [data-testid="collapsedControl"] {
                display: none !important;
            }
            header[data-testid="stHeader"] {
                display: none !important;
            }

            .block-container {
                max-width: 96% !important;
                padding-top: 1rem !important;
                padding-left: 1rem !important;
                padding-right: 1rem !important;
            }

            [data-testid="stMarkdown"],
            [data-testid="stText"],
            [data-testid="stCaption"],
            [data-testid="stWidgetLabel"],
            [data-testid="stMarkdownContainer"] {
                color: var(--moto-text);
            }

            h1, h2, h3, h4, h5, h6,
            [data-testid="stHeading"] {
                color: var(--moto-text) !important;
                letter-spacing: -0.02em;
            }

            [data-testid="stCaption"],
            [data-testid="stCaptionContainer"] {
                color: var(--moto-muted) !important;
            }

            a, [data-testid="stMarkdownContainer"] a {
                color: var(--moto-orange-hover) !important;
            }

            hr {
                border-color: var(--moto-border) !important;
            }

            .header-card {
                border: 1px solid var(--moto-border);
                border-radius: 16px;
                padding: 10px 14px;
                margin-bottom: 8px;
                background: linear-gradient(110deg, rgba(241, 90, 36, 0.08), var(--moto-surface) 38%);
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
                color: var(--moto-text);
                margin: 0;
                line-height: 1.1;
            }

            .navbar-subtitle {
                font-size: 16px;
                color: var(--moto-muted);
                margin-top: 3px;
                line-height: 1.2;
            }

            .user-box {
                font-size: 18px;
                color: var(--moto-text);
                font-weight: 800;
                text-align: center;
                min-height: 42px;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 6px;
                white-space: nowrap;
                border: 1px solid var(--moto-border);
                border-radius: 12px;
                padding: 8px 12px;
                background-color: var(--moto-surface);
            }

            div[data-testid="stButton"] > button,
            div[data-testid="stFormSubmitButton"] > button,
            div[data-testid="stDownloadButton"] > button {
                background: var(--moto-surface-raised) !important;
                color: var(--moto-text) !important;
                border-radius: 12px !important;
                border: 1px solid var(--moto-border) !important;
                min-height: 46px !important;
                padding: 10px 16px !important;
                width: 100% !important;
                box-shadow: none !important;
                transition: background-color 140ms ease, border-color 140ms ease, transform 140ms ease !important;
            }

            div[data-testid="stButton"] > button:hover,
            div[data-testid="stFormSubmitButton"] > button:hover,
            div[data-testid="stDownloadButton"] > button:hover {
                background: var(--moto-surface) !important;
                border-color: var(--moto-orange) !important;
                color: var(--moto-text) !important;
                transform: translateY(-1px);
            }

            div[data-testid="stButton"] > button[kind="primary"],
            div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
                background: var(--moto-orange) !important;
                border-color: var(--moto-orange) !important;
                color: #171310 !important;
            }

            div[data-testid="stButton"] > button[kind="primary"]:hover,
            div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
                background: var(--moto-orange-hover) !important;
                border-color: var(--moto-orange-hover) !important;
                color: #171310 !important;
            }

            div[data-testid="stButton"] > button p,
            div[data-testid="stButton"] > button span,
            div[data-testid="stFormSubmitButton"] > button p,
            div[data-testid="stDownloadButton"] > button p {
                font-size: 15px !important;
                font-weight: 700 !important;
                line-height: 1.1 !important;
            }

            input, textarea,
            [data-baseweb="input"] > div,
            [data-baseweb="textarea"],
            [data-baseweb="select"] > div,
            [data-baseweb="base-input"] {
                background-color: var(--moto-surface) !important;
                color: var(--moto-text) !important;
                border-color: var(--moto-border) !important;
                border-radius: 10px !important;
            }

            input::placeholder, textarea::placeholder {
                color: var(--moto-muted) !important;
            }

            input:focus, textarea:focus,
            [data-baseweb="input"]:focus-within,
            [data-baseweb="textarea"]:focus-within,
            [data-baseweb="select"]:focus-within {
                border-color: var(--moto-orange) !important;
                box-shadow: 0 0 0 1px var(--moto-orange) !important;
            }

            [data-baseweb="popover"],
            [data-baseweb="menu"],
            [role="listbox"] {
                background-color: var(--moto-surface-raised) !important;
                color: var(--moto-text) !important;
                border: 1px solid var(--moto-border) !important;
            }

            [role="option"]:hover,
            [role="option"][aria-selected="true"] {
                background-color: rgba(241, 90, 36, 0.2) !important;
            }

            [data-testid="stVerticalBlockBorderWrapper"] > div {
                border-color: var(--moto-border) !important;
                border-radius: 14px !important;
                background-color: rgba(27, 29, 33, 0.72);
            }

            [data-testid="stExpander"] {
                background-color: var(--moto-surface);
                border: 1px solid var(--moto-border) !important;
                border-radius: 12px !important;
            }

            [data-testid="stExpander"] summary:hover {
                color: var(--moto-orange-hover) !important;
            }

            [data-baseweb="tab-list"] {
                gap: 8px;
                border-bottom: 1px solid var(--moto-border);
            }

            [data-baseweb="tab"] {
                color: var(--moto-muted) !important;
            }

            [data-baseweb="tab"][aria-selected="true"] {
                color: var(--moto-orange-hover) !important;
                border-bottom-color: var(--moto-orange) !important;
            }

            [data-testid="stDialog"] {
                background-color: var(--moto-surface) !important;
                border: 1px solid var(--moto-border) !important;
                border-radius: 18px !important;
            }

            [data-testid="stMetric"] {
                background: linear-gradient(145deg, var(--moto-surface-raised), var(--moto-surface));
                border: 1px solid var(--moto-border);
                border-radius: 12px;
                padding: 14px;
            }

            [data-testid="stMetricLabel"] {
                color: var(--moto-muted) !important;
            }

            [data-testid="stMetricValue"] {
                color: var(--moto-orange-hover) !important;
            }

            [data-testid="stDataFrame"],
            [data-testid="stTable"] {
                border: 1px solid var(--moto-border);
                border-radius: 12px;
                overflow: hidden;
            }

            [data-testid="stDataFrame"] *,
            [data-testid="stTable"] * {
                color: var(--moto-text);
            }

            [data-testid="stDataEditor"] {
                border: 1px solid var(--moto-border);
                border-radius: 12px;
                overflow: hidden;
            }

            [data-testid="stFileUploaderDropzone"] {
                background-color: var(--moto-surface) !important;
                border: 1px dashed var(--moto-border) !important;
                border-radius: 12px !important;
            }

            [data-testid="stSlider"] [role="slider"] {
                background-color: var(--moto-orange) !important;
                border-color: var(--moto-orange) !important;
            }

            [data-testid="stProgress"] [data-testid="stProgressBar"] > div {
                background-color: var(--moto-orange) !important;
            }

            [data-testid="stAlert"] {
                border-radius: 12px !important;
                border: 1px solid var(--moto-border) !important;
                background-color: var(--moto-surface) !important;
            }

            [data-testid="stCheckbox"] label,
            [data-testid="stRadio"] label {
                color: var(--moto-text) !important;
            }

            [data-testid="stCheckbox"] input:checked + div,
            [data-testid="stRadio"] input:checked + div {
                background-color: var(--moto-orange) !important;
                border-color: var(--moto-orange) !important;
            }

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

                div[data-testid="stButton"] > button {
                    min-height: 42px !important;
                    padding: 8px 8px !important;
                }

                div[data-testid="stButton"] > button p,
                div[data-testid="stButton"] > button span {
                    font-size: 13px !important;
                    font-weight: 800 !important;
                }

                .user-box {
                    font-size: 12px !important;
                    padding: 6px !important;
                    min-height: 34px !important;
                }
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
    Muestra el encabezado y las opciones según el rol.

    Admin y socio:
        - Inicio
        - Registrar
        - Servicios del Día
        - Pagos y Cierre de Caja

    Operador:
        - Registrar
        - Servicios del Día
        - Pagos y Cierre de Caja
    """

    usuario_actual = (
        st.session_state
        .get("usuario", "")
        .strip()
        .lower()
    )

    rol_actual = (
        st.session_state.get("rol")
        or usuario_actual
    ).strip().lower()

    st.session_state.rol = rol_actual

    roles_validos = [
        "admin",
        "socio",
        "operador"
    ]

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

    logo_base64 = cargar_logo_base64(
        "assets/logo.png"
    )

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

    col_logo, col_usuario = st.columns(
        [4, 1.35]
    )

    with col_logo:
        st.markdown(
            f"""
<div class="header-card">
    <div class="header-brand">
        {logo_html}
        <div class="header-text">
            <div class="navbar-title">
                Moto Space Wash
            </div>
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

    # El operador no puede entrar al Inicio.
    if (
        rol_actual == "operador"
        and st.session_state.get("vista") == "Inicio"
    ):
        st.session_state.vista = "Registrar"

    # Admin y socio vuelven a Inicio si la vista no existe.
    if (
        rol_actual in ["admin", "socio"]
        and st.session_state.get("vista") not in opciones
    ):
        st.session_state.vista = "Inicio"

    # El operador vuelve a Registrar si la vista no existe.
    # Cierre sí está permitido porque está dentro de opciones.
    if (
        rol_actual == "operador"
        and st.session_state.get("vista") not in opciones
    ):
        st.session_state.vista = "Registrar"

    # =====================================================
    # BOTONES DE NAVEGACIÓN
    # =====================================================

    columnas = st.columns(
        proporciones_columnas
    )

    for columna, (clave, etiqueta) in zip(
        columnas,
        opciones.items()
    ):
        with columna:
            if st.button(
                etiqueta,
                use_container_width=True,
                key=f"nav_{clave}",
                type=(
                    "primary"
                    if st.session_state.vista == clave
                    else "secondary"
                )
            ):
                st.session_state.vista = clave
                st.rerun()

    st.divider()