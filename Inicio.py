import streamlit as st
import base64
from functions import execute_query, add_vendedor, add_comprador

# Ocultar menú lateral y selector de páginas
st.markdown("""
    <style>
      /* Oculta el menú de hamburguesa */
      #MainMenu {visibility: hidden !important;}
      /* Oculta la navegación de páginas en la cabecera */
      nav[aria-label="Page navigation"] {display: none !important;}
      /* Oculta la lista de páginas en la sidebar */
      [data-testid="stSidebarNav"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

<<<<<<< HEAD
=======
# Función para fondo de pantalla
>>>>>>> 33b94a5cf1fe663e953670562a2407a9d7e7a9f7
def set_background():
    css = """
    <style>
        /* Fondo general claro (como en vendedor.py) */
        .stApp {
            background-color: #F4F4F4 !important;
        }

        /* Zona del formulario con fondo #51A3A3 */
        div.stForm {
            background-color: #51A3A3 !important;
            padding: 2em !important;
            border-radius: 12px !important;
            box-shadow: 0 0 15px rgba(0, 0, 0, 0.3) !important;
        }

        /* Texto oscuro en toda la app */
        h1, h2, h3, h4, h5, h6,
        label, .stRadio > div,
        .stApp, .stApp * {
            color: #11151C !important;
        }

        /* Texto dentro del formulario (también oscuro para coherencia) */
        div.stForm, div.stForm * {
            color: #11151C !important;
        }

        /* Inputs dentro del formulario */
        div.stForm input,
        div.stForm textarea {
            background-color: white !important;
            color: #11151C !important;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

<<<<<<< HEAD
# Aplicar fondo al inicio
=======
# Aplicar fondo
>>>>>>> 33b94a5cf1fe663e953670562a2407a9d7e7a9f7
set_background()

# Ahora el contenido de la app
st.title("ORTOPEDIX")
st.subheader("Bienvenido a la plataforma de compra y venta de productos ortopédicos.")

action = st.radio("¿Qué deseas hacer?", ["Crear cuenta", "Iniciar sesión"])

if action == "Crear cuenta":
    role = st.radio("¿Eres vendedor o comprador?", ["Vendedor", "Comprador"])
    with st.form("signup_form"):
        st.markdown("### 📝 Formulario de Registro")
        nombre     = st.text_input("👤 Nombre y Apellido")
        ubicacion  = st.text_input("📍 Ubicación")
        telefono   = st.text_input("📞 Teléfono")
        mail       = st.text_input("📧 Mail")
        usuario    = st.text_input("🆔 Nombre de Usuario")
        contraseña = st.text_input("🔒 Contraseña", type="password")

        if st.form_submit_button("✅ Registrarme"):
            if all([nombre, ubicacion, telefono, mail, usuario, contraseña]):
                if role == "Vendedor":
                    success = add_vendedor(nombre, ubicacion, telefono, mail, usuario, contraseña)
                else:
                    success = add_comprador(nombre, ubicacion, telefono, mail, usuario, contraseña)

                if success:
                    st.success("🎉 Cuenta creada con éxito. Ahora puedes iniciar sesión.")
                else:
                    st.error("❌ Error al crear la cuenta.")
            else:
                st.error("⚠️ Por favor, completa todos los campos.")

else:
    role = st.radio("¿Inicias como vendedor o comprador?", ["Vendedor", "Comprador"])
    with st.form("login_form"):
        st.markdown("### 🔐 Iniciar Sesión")
        usuario    = st.text_input("🆔 Usuario")
        contraseña = st.text_input("🔒 Contraseña", type="password")

        if st.form_submit_button("🔓 Ingresar"):
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
                    st.success(f"🙌 Bienvenido, {usuario} ({role})")
                    # Redirigir tras login exitoso
                    st.switch_page('pages/vendedor.py' if role == 'Vendedor' else 'pages/comprador.py')
                else:
                    st.error("❌ Usuario o contraseña incorrectos.")
            else:
                st.error("⚠️ Por favor, completa ambos campos.")
