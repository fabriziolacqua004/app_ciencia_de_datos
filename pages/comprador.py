# pages/comprador.py
import streamlit as st
from functions import execute_query

def main():
    st.title("📋 Publicaciones")

    # 🔹 Filtros dinámicos desde la base de datos
    categorias_sql = "SELECT id, descripcion FROM public.categoria ORDER BY descripcion"
    categorias_df = execute_query(categorias_sql, is_select=True)
    categorias = {row["descripcion"]: row["id"] for _, row in categorias_df.iterrows()}
    categoria_seleccionada = st.selectbox("Filtrar por categoría:", ["Todas"] + list(categorias.keys()))

    estado_seleccionado = st.selectbox("Filtrar por estado:", ["Todos", "Nuevo", "Usado"])
    tipo_seleccionado = st.selectbox("Filtrar por tipo:", ["Todos", "Venta", "Alquiler"])

    # 🔹 Query base con joins para poder filtrar
    sql = """
        SELECT pub.id, pub.titulo, pub.descripcion, pub.tipo, pub.estado, pub.precio,
               cat.descripcion AS categoria
        FROM public.publicaciones AS pub
        JOIN public.productos AS prod ON pub.id_producto = prod.id
        JOIN public.categoria AS cat ON prod.id_categoria = cat.id
        WHERE pub.activo = 1
    """

    filtros = []
    if categoria_seleccionada != "Todas":
        filtros.append(f"cat.id = {categorias[categoria_seleccionada]}")
    if estado_seleccionado != "Todos":
        filtros.append(f"LOWER(pub.estado) = LOWER('{estado_seleccionado}')")
    if tipo_seleccionado != "Todos":
        filtros.append(f"LOWER(pub.tipo) = LOWER('{tipo_seleccionado}')")

    if filtros:
        sql += " AND " + " AND ".join(filtros)

    sql += " ORDER BY pub.id DESC"

    df = execute_query(sql, is_select=True)

    if df.empty:
        st.info("No hay publicaciones disponibles con los filtros seleccionados.")
        return

    # 🔹 Mostrar cada publicación
    for _, pub in df.iterrows():
        with st.expander(f"{pub['titulo']} — ${pub['precio']} ({pub['tipo']})"):
            st.write(f"**Descripción:** {pub['descripcion']}")
            st.write(f"**Categoría:** {pub['categoria']}")
            st.write(f"**Estado:** {pub['estado']}")
            
            # Botón según tipo
            if pub["tipo"].lower() == "alquiler":
                if st.button(f"Alquilar ID {pub['id']}", key=f"alq_{pub['id']}"):
                    st.success("✔️ Has solicitado el alquiler.")
            else:
                if st.button(f"Comprar ID {pub['id']}", key=f"comp_{pub['id']}"):
                    st.success("✔️ Has comprado este artículo.")

if __name__ == "__main__":
    # Solo compradores
    if not st.session_state.get("logged_in") or st.session_state.get("role") != "Comprador":
        st.error("❌ Acceso denegado. Inicia sesión como Comprador.")
    else:
        main()
