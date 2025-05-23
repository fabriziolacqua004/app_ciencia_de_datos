import streamlit as st
from functions import add_confirmacion, execute_query

st.title("🛒 Confirmar compra")

if 'transaccion' not in st.session_state or st.session_state['transaccion']['tipo'].lower() != 'venta':
    st.error("No hay una compra en proceso.")
    st.stop()

pub_id = st.session_state['transaccion']['pub_id']

# Selección de método de pago
metodo = st.selectbox("Método de pago", ["Mercado Pago", "Tarjeta de crédito", "Tarjeta de débito"])

st.subheader("💳 Datos de pago")
nombre = st.text_input("Nombre en la tarjeta")
numero = st.text_input("Número de tarjeta")
venc   = st.text_input("Fecha de vencimiento (MM/AA)")
cvv    = st.text_input("CVV")

if st.button("Confirmar compra"):
    if not all([nombre, numero, venc, cvv]):
        st.warning("Completa todos los campos.")
    else:
        try:
            # Guardar método elegido y vigencia NULL para venta permanente
            add_confirmacion(pub_id, st.session_state['user_id'], metodo, None)
            execute_query(
                "UPDATE publicaciones SET activoinactivo = 0 WHERE id = %s",
                params=(pub_id,), is_select=False
            )
            st.success("✅ ¡Compra confirmada con vigencia permanente!")
            st.session_state.pop('transaccion')
            # Volver automáticamente a publicaciones
            st.switch_page('pages/comprador.py')
        except Exception as e:
            st.error(f"DB error: {e}")
