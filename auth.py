import streamlit as st


def login():
    """
    Login simple con usuarios guardados en st.secrets.
    """

    if "logueado" not in st.session_state:
        st.session_state.logueado = False

    if "usuario" not in st.session_state:
        st.session_state.usuario = ""

    if st.session_state.logueado:
        return True

    st.title("🔐 Acceso Moto Space Wash")
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
            st.rerun()