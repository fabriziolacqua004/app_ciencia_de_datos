import streamlit as st
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
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

# Autorefresh cada segundo mientras no se cancele
st.session_state.setdefault("compra_cancelado", False)
if not st.session_state["compra_cancelado"]:
    st_autorefresh(interval=1000, limit=None, key="refresh_compra")

st.title("🛒 Confirmar compra")

# Verificar que haya una compra en curso
if 'transaccion' not in st.session_state or st.session_state['transaccion']['tipo'].lower() != 'venta':
    st.error("No hay una compra en proceso.")
    st.stop()

pub_id = st.session_state['transaccion']['pub_id']

# Inicializar timer y bloquear la publicación al primer acceso
if 'tiempo_inicio' not in st.session_state:
    st.session_state['tiempo_inicio'] = datetime.now()
    execute_query(
        "UPDATE publicaciones SET activoinactivo = 0 WHERE id = %s",
        params=(pub_id,), is_select=False
    )

# Calcular tiempo restante
restante = timedelta(minutes=5) - (datetime.now() - st.session_state['tiempo_inicio'])
if restante.total_seconds() <= 0:
    # Expiró: reactivar y volver
    execute_query(
        "UPDATE publicaciones SET activoinactivo = 1 WHERE id = %s",
        params=(pub_id,), is_select=False
    )
    st.session_state.pop('transaccion', None)
    st.session_state.pop('tiempo_inicio', None)
    st.warning("⏰ Se agotó el tiempo. Volviendo al catálogo...")
    st.experimental_rerun()

# Mostrar countdown en vivo
mins, secs = divmod(int(restante.total_seconds()), 60)
st.markdown(f"### Tiempo restante: ⏳ {mins:02d}:{secs:02d}")

# Botón siempre visible para volver al catálogo
if st.button("🔙 Volver a publicaciones"):
    st.session_state["compra_cancelado"] = True
    execute_query(
        "UPDATE publicaciones SET activoinactivo = 1 WHERE id = %s",
        params=(pub_id,), is_select=False
    )
    st.session_state.pop('transaccion', None)
    st.session_state.pop('tiempo_inicio', None)
    st.switch_page('pages/comprador.py')

# Formulario de pago
metodo = st.selectbox("Método de pago", ["Mercado Pago", "Tarjeta de crédito", "Tarjeta de débito"])
st.subheader("💳 Datos de pago")
nombre = st.text_input("Nombre en la tarjeta")
numero = st.text_input("Número de tarjeta")
venc   = st.text_input("Fecha de vencimiento (MM/AA)")
cvv    = st.text_input("CVV")

if st.button("Confirmar compra"):
    st.session_state["compra_cancelado"] = True
    if not all([nombre, numero, venc, cvv]):
        st.warning("Completa todos los campos.")
    else:
        add_confirmacion(pub_id, st.session_state['user_id'], metodo, None)
        st.success("✅ Compra confirmada y publicación inactiva.")
        # limpiar y volver
        st.session_state.pop('transaccion', None)
        st.session_state.pop('tiempo_inicio', None)
        st.experimental_rerun()
