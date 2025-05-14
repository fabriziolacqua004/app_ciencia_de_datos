

# 1) Elegir acción
action = st.radio("¿Qué deseas hacer?", ["Crear cuenta", "Iniciar sesión"])

if action == "Crear cuenta":
    role = st.radio("¿Eres vendedor o comprador?", ["Vendedor", "Comprador"])
    with st.form("signup_form"):
        nombre       = st.text_input("Nombre y Apellido")
        ubicacion    = st.text_input("Ubicación")
        telefono     = st.text_input("Teléfono")
        mail         = st.text_input("Mail")
        usuario      = st.text_input("Nombre de Usuario")
        contraseña   = st.text_input("Contraseña", type="password")

        if st.form_submit_button("Registrarme"):
            if all([nombre, ubicacion, telefono, mail, usuario, contraseña]):
                if role == "Vendedor":
                    success = add_vendedor(nombre, ubicacion, telefono, mail, usuario, contraseña)
                else:
                    success = add_comprador(nombre, ubicacion, telefono, mail, usuario, contraseña)

                if success:
                    st.success("✅ Cuenta creada. Ahora inicia sesión.")
                else:
                    st.error("❌ Error al crear la cuenta. Revisa los mensajes de la DB.")
            else:
                st.error("⚠️ Completa todos los campos.")

else:  # Iniciar sesión
    role = st.radio("¿Inicias como vendedor o comprador?", ["Vendedor", "Comprador"])
    with st.form("login_form"):
        usuario    = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")

        if st.form_submit_button("Login"):
            if usuario and contraseña:
                table = "vendedores" if role == "Vendedor" else "compradores"
                sql = f"""
                    SELECT id
                    FROM public.{table}
                    WHERE "nombre_de_usuario" = %s
                      AND "contraseña"        = %s
                """
                df = execute_query(sql, params=(usuario, contraseña), is_select=True)
                if not df.empty:
                    st.session_state["logged_in"] = True
                    st.session_state["role"]      = role
                    st.session_state["user_id"]   = int(df.loc[0, "id"])
                    st.success(f"Bienvenido, {usuario} ({role})")
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
            else:
                st.error("⚠️ Ingresa usuario y contraseña.")

# 3) Si está logueado, muestro la app principal
if st.session_state.get("logged_in", False):
    st.sidebar.title("Menú")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state.clear()
        st.experimental_rerun()

    st.info(f"Sesión iniciada como {st.session_state['role']} (ID={st.session_state['user_id']})")
    # Aquí agregas tus secciones de gestión: publicaciones, confirmaciones, etc.

#hola
#hola
