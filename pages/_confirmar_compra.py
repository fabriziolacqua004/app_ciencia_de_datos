import streamlit as st
import time
from datetime import datetime, timedelta
from functions import add_confirmacion, execute_query

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

st.title("🛒 Confirmar compra")

# 1) Verificar que haya una compra en curso
if 'transaccion' not in st.session_state or st.session_state['transaccion']['tipo'].lower() != 'venta':
    st.error("No hay una compra en proceso.")
    st.stop()

pub_id = st.session_state['transaccion']['pub_id']

# 2) Bloquear la publicación en cuanto se ingresa (primera carga)
if 'bloqueado_compra' not in st.session_state:
    st.session_state['bloqueado_compra'] = True
    execute_query(
        "UPDATE publicaciones SET activoinactivo = 0 WHERE id = %s",
        params=(pub_id,), is_select=False
    )

# 3) Mostrar tiempo fijo de 5 minutos (sin autorefresh dinámico)
st.markdown("### ⏳ Tienes 5 minutos para confirmar la compra")

# 4) Botón para volver manualmente al catálogo, liberando la publicación
if st.button("🔙 Volver a publicaciones"):
    execute_query(
        "UPDATE publicaciones SET activoinactivo = 1 WHERE id = %s",
        params=(pub_id,), is_select=False
    )
    # Limpiar estado de transacción para que no queden "residuos"
    st.session_state.pop('transaccion', None)
    st.session_state.pop('bloqueado_compra', None)
    st.switch_page('pages/comprador.py')

# 5) Formulario de pago
metodo = st.selectbox("Método de pago", ["Mercado Pago", "Tarjeta de crédito", "Tarjeta de débito"])
st.subheader("💳 Datos de pago")
nombre = st.text_input("Nombre en la tarjeta")
numero = st.text_input("Número de tarjeta")
venc   = st.text_input("Fecha de vencimiento (MM/AA)")
cvv    = st.text_input("CVV")

# 6) Botón “Confirmar compra”
if st.button("Confirmar compra"):
    # Validar que se hayan completado todos los campos
    if not all([nombre, numero, venc, cvv]):
        st.warning("Completa todos los campos.")
    else:
        # a) Insertar la confirmación en la tabla
        add_confirmacion(pub_id, st.session_state['user_id'], metodo, None)
        # b) Marcar la publicación como inactiva (ya vendida)
        execute_query(
            "UPDATE publicaciones SET activoinactivo = 0 WHERE id = %s",
            params=(pub_id,), is_select=False
        )
        # c) Limpiar el estado de sesión para no mantener “transaccion”
        st.session_state.pop('transaccion', None)
        st.session_state.pop('bloqueado_compra', None)
        # d) Mostrar mensaje de éxito
        st.success("✅ Compra realizada correctamente. Redirigiendo al catálogo en 5 segundos...")
        # e) Esperar 5 segundos antes de redirigir
        time.sleep(5)
        # f) Redirigir al usuario a la página de publicaciones
        st.switch_page('pages/comprador.py')
