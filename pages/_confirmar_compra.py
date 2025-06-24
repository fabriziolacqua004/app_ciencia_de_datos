import streamlit as st
import time
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from functions import add_confirmacion, execute_query

st.markdown("""
    <style>
      #MainMenu {visibility: hidden !important;}
      nav[aria-label="Page navigation"] {display: none !important;}
      [data-testid="stSidebarNav"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

st.title("🛒 Confirmar compra")

# 1) Verificar transacción activa
if 'transaccion' not in st.session_state or st.session_state['transaccion']['tipo'].lower() != 'venta':
    st.error("No hay una compra en proceso.")
    st.stop()

pub_id = st.session_state['transaccion']['pub_id']

# 2) Bloquear publicación y guardar hora de inicio
if 'bloqueado_compra' not in st.session_state:
    st.session_state['bloqueado_compra'] = True
    st.session_state['inicio_timer_compra'] = datetime.now()
    execute_query(
        "UPDATE publicaciones SET activoinactivo = 0 WHERE id = %s",
        params=(pub_id,), is_select=False
    )

# 3) Temporizador de 5 minutos
tiempo_total = timedelta(minutes=1)
tiempo_restante = (st.session_state['inicio_timer_compra'] + tiempo_total) - datetime.now()

# Refresca la página cada 10 segundos
st_autorefresh(interval=60 * 1000, key="auto_refresh_compra")

# Si se terminó el tiempo, liberar y redirigir
if tiempo_restante.total_seconds() <= 0:
    execute_query(
        "UPDATE publicaciones SET activoinactivo = 1 WHERE id = %s",
        params=(pub_id,), is_select=False
    )
    st.session_state.pop('transaccion', None)
    st.session_state.pop('bloqueado_compra', None)
    st.session_state.pop('inicio_timer_compra', None)
    st.switch_page('pages/comprador.py')
else:
    minutos, segundos = divmod(int(tiempo_restante.total_seconds()), 60)
    st.markdown(f"### ⏳ Tienes {minutos} min {segundos} seg para confirmar la compra")

# 4) Botón para volver manualmente al catálogo
if st.button("🔙 Volver a publicaciones", key="volver_publicaciones"):
    execute_query(
        "UPDATE publicaciones SET activoinactivo = 1 WHERE id = %s",
        params=(pub_id,), is_select=False
    )
    st.session_state.pop('transaccion', None)
    st.session_state.pop('bloqueado_compra', None)
    st.session_state.pop('inicio_timer_compra', None)
    st.switch_page('pages/comprador.py')

# 5) Formulario de pago
metodo = st.selectbox("Método de pago", ["Mercado Pago", "Tarjeta de crédito", "Tarjeta de débito"])
st.subheader("💳 Datos de pago")
nombre = st.text_input("Nombre en la tarjeta")
numero = st.text_input("Número de tarjeta")
venc   = st.text_input("Fecha de vencimiento (MM/AA)")
cvv    = st.text_input("CVV")

# 6) Confirmar compra
if st.button("Confirmar compra", key="confirmar_compra"):
    if not all([nombre, numero, venc, cvv]):
        st.warning("Completa todos los campos.")
    else:
        # 1) Registrar confirmación y reactivar publicación
        add_confirmacion(pub_id, st.session_state['user_id'], metodo, None)
        execute_query(
            "UPDATE publicaciones SET activoinactivo = 0 WHERE id = %s",
            params=(pub_id,), is_select=False
        )
        # 2) Limpiar estado de la transacción
        st.session_state.pop('transaccion', None)
        st.session_state.pop('bloqueado_compra', None)
        st.session_state.pop('inicio_timer_compra', None)
        # 3) Obtener datos del dueño
        result = execute_query(
            "SELECT id_vendedor FROM publicaciones WHERE id = %s",
            params=(pub_id,), is_select=True
        )
        id_dueno = int(result.iloc[0]['id_vendedor'])
        info = execute_query(
            "SELECT nombre_y_apellido, numero_de_telefono FROM vendedores WHERE id = %s",
            params=(id_dueno,), is_select=True
        )
        nombre_dueno   = info.at[0, 'nombre_y_apellido']
        telefono_dueno = info.at[0, 'numero_de_telefono']
        # 4) Mostrar mensaje de contacto
        st.info(f"📞 Comunicate con **{nombre_dueno}** al **{telefono_dueno}** para coordinar la entrega.")
        # 5) Mensaje final y redirección
        st.success("✅ Compra realizada correctamente. Redirigiendo al catálogo...")
        time.sleep(15)
        st.switch_page('pages/comprador.py')

