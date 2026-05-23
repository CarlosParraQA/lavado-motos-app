import streamlit as st


def cargar_sesion_desde_token():
    """
    Recupera la sesión usando el token guardado en la URL.
    """

    if st.session_state.get("logout_manual", False):
        return False

    if st.session_state.get("logueado", False):
        return True

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


def login():
    """
    Login con usuarios guardados en st.secrets.
    Mantiene la sesión usando token en la URL.
    """

    if "logueado" not in st.session_state:
        st.session_state.logueado = False

    if "usuario" not in st.session_state:
        st.session_state.usuario = ""

    if "logout_manual" not in st.session_state:
        st.session_state.logout_manual = False

    if cargar_sesion_desde_token():
        return True

    if st.session_state.logueado:
        return True

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

                if token_usuario:
                    st.query_params["token"] = token_usuario

                st.success("Ingreso exitoso.")
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos.")

    st.stop()


def logout():
    """
    Cierra la sesión del usuario.
    """

    with st.sidebar:
        st.divider()
        st.write(f"👤 Usuario: **{st.session_state.usuario}**")

        if st.button("Cerrar sesión"):
            st.session_state.logueado = False
            st.session_state.usuario = ""
            st.session_state.logout_manual = True

            st.query_params.clear()

            st.rerun()