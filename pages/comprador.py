# pages/comprador.py

import streamlit as st
from functions import execute_query

def main():
    st.title("📋 Publicaciones hola")

    # 1) Traer todas las publicaciones
    # Asumo que tu tabla se llama `publicaciones` con columnas:
    #   id, titulo, descripcion, tipo ('venta' o 'alquiler'), precio, vendedor_id
    sql = """
        SELECT id, titulo, descripcion, tipo, precio
        FROM public.publicaciones
        ORDER BY id DESC
    """
    df = execute_query(sql, is_select=True)

    if df.empty:
        st.info("No hay publicaciones disponibles.")
        return

    # 2) Mostrar cada publicación en un expander
    for _, pub in df.iterrows():
        with st.expander(f"{pub['titulo']}  —  ${pub['precio']} ({pub['tipo']})"):
            st.write(pub["descripcion"])
            # 3) Botón según tipo
            if pub["tipo"].lower() == "alquiler":
                if st.button(f"Alquilar ID {pub['id']}", key=f"alq_{pub['id']}"):
                    # Aquí podrías llamar a una función que inserte en un table alquileres, etc.
                    st.success("✔️ Has solicitado el alquiler.")
            else:  # venta
                if st.button(f"Comprar ID {pub['id']}", key=f"comp_{pub['id']}"):
                    # Aquí podrías llamar a tu lógica de compra
                    st.success("✔️ Has comprado este artículo.")

if __name__ == "__main__":
    # Solo usuarios compradores
    if not st.session_state.get("logged_in") or st.session_state.get("role") != "Comprador":
        st.error("❌ Acceso denegado. Inicia sesión como Comprador.")
    else:
        main()

#hola