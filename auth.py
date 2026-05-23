import streamlit as st
from streamlit_cookies_controller import CookieController


controller = CookieController()


def cargar_sesion_desde_cookie():
    """
    Recupera la sesión desde una cookie del navegador.
    """

    usuario_cookie = controller.get("spacewash_usuario")

    if usuario_cookie:
        st.session_state.logueado = True
        st.session_state.usuario = usuario_cookie
        return True

    return False


def login():
    """
    Login con usuarios guardados en st.secrets.
    Mantiene la sesión usando cookie del navegador.
    """

    if "logueado" not in st.session_state:
        st.session_state.logueado = False

    if "usuario" not in st.session_state:
        st.session_state.usuario = ""

    if st.session_state.logueado:
        return True

    if cargar_sesion_desde_cookie():
        return True

    st.title("🔐 Accede al sistema de registros - Space Wash")
    st.caption("Ingresa tus credenciales para continuar.")

    with st.form("login_form"):
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")

        ingresar = st.form_submit_button("Ingresar", use_container_width=True)

        if ingresar:
            usuarios = st.secrets["usuarios"]

            if usuario in usuarios and clave == usuarios[usuario]:
                st.session_state.logueado = True
                st.session_state.usuario = usuario

                controller.set(
                    "spacewash_usuario",
                    usuario,
                    max_age=60 * 60 * 24 * 7
                )

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
            controller.remove("spacewash_usuario")

            st.session_state.logueado = False
            st.session_state.usuario = ""

            st.rerun()