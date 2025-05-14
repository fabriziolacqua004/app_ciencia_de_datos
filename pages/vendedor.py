# pages/vendedor.py

import streamlit as st
from functions import execute_query, add_publicacion

def main():
    st.title("🖋️ Crear nueva publicación")

    with st.form("pub_form"):
        titulo      = st.text_input("Título")
        descripcion = st.text_area("Descripción")
        tipo        = st.selectbox("Tipo", ["venta", "alquiler"])
        precio      = st.number_input("Precio", min_value=0.0, format="%f")
        if st.form_submit_button("Publicar"):
            if all([titulo, descripcion, tipo, precio is not None]):
                ok = add_publicacion(
                    st.session_state["user_id"],  # vendedor_id
                    titulo, descripcion, tipo, precio
                )
                if ok:
                    st.success("✅ Publicación creada.")
                else:
                    st.error("❌ Error al crear la publicación.")
            else:
                st.error("Completa todos los campos.")

if __name__ == "__main__":
    if not st.session_state.get("logged_in") or st.session_state.get("role") != "Vendedor":
        st.error("❌ Acceso denegado. Inicia sesión como Vendedor.")
    else:
        main()
