import streamlit as st
from functions import add_confirmacion, execute_query

st.title("💸 Confirmar alquiler")

if 'transaccion' not in st.session_state or st.session_state['transaccion']['tipo'].lower() != 'alquiler':
    st.error("No hay un alquiler en proceso.")
    st.stop()

pub_id = st.session_state['transaccion']['pub_id']

dias = st.number_input("Cantidad de días a alquilar", min_value=1, step=1)

# Selección de método de pago
metodo = st.selectbox("Método de pago", ["Mercado Pago", "Tarjeta de crédito", "Tarjeta de débito"])

st.subheader("💳 Datos de pago")
nombre = st.text_input("Nombre en la tarjeta")
numero = st.text_input("Número de tarjeta")
venc   = st.text_input("Fecha de vencimiento (MM/AA)")
cvv    = st.text_input("CVV")

if st.button("Confirmar alquiler"):
    if not all([dias, nombre, numero, venc, cvv]):
        st.warning("Completa todos los campos.")
    else:
        try:
            # Guardar método elegido y días de vigencia
            add_confirmacion(pub_id, st.session_state['user_id'], metodo, int(dias))
            execute_query(
                "UPDATE publicaciones SET activoinactivo = 0 WHERE id = %s",
                params=(pub_id,), is_select=False
            )
            st.success(f"✅ ¡Alquilado por {dias} días con éxito!")
            st.session_state.pop('transaccion')
            # Volver automáticamente a publicaciones
            st.switch_page('pages/comprador.py')
        except Exception as e:
            st.error(f"DB error: {e}")
