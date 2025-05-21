import streamlit as st
from functions import execute_query
from datetime import datetime, timedelta

def main():
    st.title("🕒 Confirmar compra")

    if "compra_iniciada" not in st.session_state or not st.session_state["compra_iniciada"]:
        st.error("No hay una compra en proceso.")
        return

    pub_id = st.session_state["compra_pub_id"]
    tiempo_inicio = st.session_state["compra_tiempo_inicio"]
    tiempo_restante = max(timedelta(minutes=10) - (datetime.now() - tiempo_inicio), timedelta(seconds=0))

    minutos, segundos = divmod(tiempo_restante.seconds, 60)
    st.markdown(f"### Tiempo restante: ⏳ {minutos:02}:{segundos:02}")

    if tiempo_restante.total_seconds() == 0:
        reactivar_sql = f"UPDATE publicaciones SET activoinactivo = 1 WHERE id = {pub_id}"
        execute_query(reactivar_sql, is_select=False)
        st.session_state["compra_iniciada"] = False
        st.warning("⏱ Tiempo expirado. La publicación ha sido reactivada.")
        return

    st.subheader("💳 Ingresá los datos de tu tarjeta")
    nombre = st.text_input("Nombre en la tarjeta")
    numero = st.text_input("Número de tarjeta")
    vencimiento = st.text_input("Fecha de vencimiento (MM/AA)")
    cvv = st.text_input("CVV")

    if st.button("Confirmar compra"):
        if not all([nombre, numero, vencimiento, cvv]):
            st.warning("Por favor, completá todos los campos.")
        else:
            confirmar_sql = f"""
                INSERT INTO confirmaciones (id_publicacion, id_comprador, vigencia, metodo_de_pago)
                VALUES ({pub_id}, {st.session_state['user_id']}, 'Permanente', 'Tarjeta')
            """
            desactivar_sql = f"UPDATE publicaciones SET activoinactivo = 0 WHERE id = {pub_id}"

            try:
                execute_query(confirmar_sql, is_select=False)
                execute_query(desactivar_sql, is_select=False)

                st.success("✅ ¡Compra confirmada exitosamente!")
                st.session_state["compra_iniciada"] = False
            except Exception as e:
                st.error(f"DB error: {e}")

if __name__ == "__main__":
    if not st.session_state.get("logged_in") or st.session_state.get("role") != "Comprador":
        st.error("❌ Acceso denegado. Inicia sesión como Comprador.")
    else:
        main()
