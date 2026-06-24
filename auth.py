import streamlit as st


def cargar_sesion_desde_token():
    """
    Recupera sesión desde token en la URL.
    No recupera si el usuario acaba de cerrar sesión.
    """

    if st.session_state.get("logout_manual", False):
        return False

    token_url = st.query_params.get("token", "")

    if not token_url:
        return False

    tokens_sesion = st.secrets.get("tokens_sesion", {})

    for usuario, token_guardado in tokens_sesion.items():
        if token_url == token_guardado:
            st.session_state.logueado = True
            st.session_state.usuario = usuario
            return True

    return False


def procesar_login_empleados(usuario, clave):
    """
    Valida las credenciales del empleado.
    Si son correctas, inicia sesión y mantiene el token en la URL.
    """

    usuarios = st.secrets["usuarios"]
    tokens_sesion = st.secrets.get("tokens_sesion", {})

    if usuario in usuarios and clave == usuarios[usuario]:
        st.session_state.logueado = True
        st.session_state.usuario = usuario
        st.session_state.logout_manual = False
        st.session_state.mostrar_login_empleados = False
        st.session_state.pantalla_acceso = "inicio"

        token_usuario = tokens_sesion.get(usuario)

        st.query_params.clear()

        if token_usuario:
            st.query_params["token"] = token_usuario

        st.success("Ingreso exitoso.")
        st.rerun()

    else:
        st.error("Usuario o contraseña incorrectos.")


@st.dialog("🔐 Acceso empleados")
def modal_login_empleados():
    """
    Muestra el login actual dentro de un popup/modal.
    """

    st.caption("Ingresa tus credenciales para continuar al sistema interno.")

    with st.form("login_form_empleados"):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")

        ingresar = st.form_submit_button(
            "Ingresar",
            use_container_width=True
        )

        if ingresar:
            procesar_login_empleados(usuario, clave)

    if st.button("Volver", use_container_width=True, key="volver_login_empleados"):
        st.session_state.mostrar_login_empleados = False
        st.rerun()


def mostrar_pantalla_clientes():
    """
    Pantalla temporal para clientes.
    """

    st.title("👥 Clientes")

    st.info("🚧 Módulo en construcción.")

    st.write(
        "Muy pronto estará disponible este espacio para clientes."
    )

    if st.button("⬅️ Volver", use_container_width=True):
        st.session_state.pantalla_acceso = "inicio"
        st.rerun()

    st.stop()


def mostrar_selector_acceso():
    """
    Muestra dos tarjetas grandes:
    - Clientes
    - Empleados
    """

    if "pantalla_acceso" not in st.session_state:
        st.session_state.pantalla_acceso = "inicio"

    if "mostrar_login_empleados" not in st.session_state:
        st.session_state.mostrar_login_empleados = False

    if st.session_state.pantalla_acceso == "clientes":
        mostrar_pantalla_clientes()

    st.markdown(
        """
        <style>
            .contenedor-acceso {
                text-align: center;
                padding-top: 30px;
                padding-bottom: 25px;
            }

            .titulo-acceso {
                font-size: 38px;
                font-weight: 800;
                margin-bottom: 8px;
            }

            .subtitulo-acceso {
                font-size: 17px;
                color: #666;
                margin-bottom: 30px;
            }

            div.stButton button,
            div.stButton button > div {
                min-height: 260px !important;
                height: 260px !important;
                width: 100% !important;
            }

            div.stButton button,
            div.stButton button > div {
                border-radius: 24px !important;
                border: 2px solid #E5E7EB !important;
                background: linear-gradient(135deg, #ffffff 0%, #f7f7f7 100%) !important;
                font-size: 28px !important;
                font-weight: 800 !important;
                box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important;
                transition: all 0.2s ease-in-out !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                padding: 0 !important;
            }

            div.stButton button:hover,
            div.stButton button > div:hover {
                transform: translateY(-4px) !important;
                border-color: #FF7A00 !important;
                box-shadow: 0 12px 28px rgba(0,0,0,0.14) !important;
            }
        </style>

        <div class="contenedor-acceso">
            <div class="titulo-acceso">🏍️ Moto Space Wash</div>
            <div class="subtitulo-acceso">
                Selecciona el tipo de acceso para continuar
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button("👥\n\nClientes", use_container_width=True, key="clientes_acceso"):
        st.session_state.pantalla_acceso = "clientes"
        st.rerun()

    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)

    if st.button("👷\n\nEmpleados", use_container_width=True, key="empleados_acceso"):
        st.session_state.mostrar_login_empleados = True

    if st.session_state.mostrar_login_empleados:
        modal_login_empleados()

    st.stop()


def mostrar_formulario_login():
    """
    Ya no muestra el login directo.
    Ahora muestra primero la pantalla de Clientes / Empleados.
    """

    mostrar_selector_acceso()


def login():
    """
    Login con usuarios guardados en st.secrets.
    Mantiene sesión con token en la URL.
    """

    if "logueado" not in st.session_state:
        st.session_state.logueado = False

    if "usuario" not in st.session_state:
        st.session_state.usuario = ""

    if "logout_manual" not in st.session_state:
        st.session_state.logout_manual = False

    if "pantalla_acceso" not in st.session_state:
        st.session_state.pantalla_acceso = "inicio"

    if "mostrar_login_empleados" not in st.session_state:
        st.session_state.mostrar_login_empleados = False

    # Si viene de cerrar sesión, muestra nuevamente la pantalla de acceso
    if st.query_params.get("logout", "") == "1" or st.session_state.logout_manual:
        st.session_state.logueado = False
        st.session_state.usuario = ""
        mostrar_formulario_login()

    # Si ya está logueado en la sesión actual, deja pasar
    if st.session_state.logueado:
        return True

    # Si tiene token válido en URL, recupera sesión
    if cargar_sesion_desde_token():
        return True

    # Si no hay sesión ni token, muestra selector Clientes / Empleados
    mostrar_formulario_login()


def cerrar_sesion():
    """
    Cierra sesión y evita que el token vuelva a iniciar automáticamente.
    """

    st.session_state.logueado = False
    st.session_state.usuario = ""
    st.session_state.logout_manual = True
    st.session_state.pantalla_acceso = "inicio"
    st.session_state.mostrar_login_empleados = False

    st.query_params.clear()
    st.query_params["logout"] = "1"

    st.rerun()