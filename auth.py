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


def mostrar_formulario_login():
    """
    Muestra el formulario de login y detiene la app.
    """

    st.title("🔐 Accede al sistema de registros - Space Wash")
    st.caption("Ingresa tus credenciales para continuar.")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")

        ingresar = st.form_submit_button("Ingresar", use_container_width=True)

        if ingresar:
            usuarios = st.secrets["usuarios"]
            tokens_sesion = st.secrets.get("tokens_sesion", {})

            if usuario in usuarios and clave == usuarios[usuario]:
                st.session_state.logueado = True
                st.session_state.usuario = usuario
                st.session_state.logout_manual = False

                token_usuario = tokens_sesion.get(usuario)

                st.query_params.clear()

                if token_usuario:
                    st.query_params["token"] = token_usuario

                st.success("Ingreso exitoso.")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    st.stop()


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

    # Si viene de cerrar sesión, siempre muestra login y bloquea el resto de la app
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

    # Si no hay sesión ni token, muestra login
    mostrar_formulario_login()


def cerrar_sesion():
    """
    Cierra sesión y evita que el token vuelva a iniciar automáticamente.
    """

    st.session_state.logueado = False
    st.session_state.usuario = ""
    st.session_state.logout_manual = True

    st.query_params.clear()
    st.query_params["logout"] = "1"

    st.rerun()