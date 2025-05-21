import streamlit as st
from functions import execute_query
from datetime import datetime

def main():
    st.title("📋 Publicaciones")

    # Filtros
    categorias = execute_query("SELECT id, descripcion FROM categoria", is_select=True)
    categoria_dict = dict(zip(categorias["descripcion"], categorias["id"]))
    categoria_seleccionada = st.selectbox("Filtrar por categoría", ["Todas"] + list(categoria_dict.keys()))

    estado_seleccionado = st.selectbox("Filtrar por estado", ["Todos", "Nuevo", "Usado"])
    tipo_seleccionado = st.selectbox("Filtrar por tipo", ["Todos", "Venta", "Alquiler"])

    sql = """
        SELECT p.id, p.titulo, p.descripcion, p.tipo, p.precio, p.estado, c.descripcion as categoria
        FROM publicaciones p
        JOIN productos pr ON p.id_producto = pr.id
        JOIN categoria c ON pr.id_categoria = c.id
        WHERE p.activoinactivo = 1
    """

    if categoria_seleccionada != "Todas":
        sql += f" AND c.id = {categoria_dict[categoria_seleccionada]}"
    if estado_seleccionado != "Todos":
        sql += f" AND LOWER(p.estado) = LOWER('{estado_seleccionado}')"
    if tipo_seleccionado != "Todos":
        sql += f" AND LOWER(p.tipo) = LOWER('{tipo_seleccionado}')"

    sql += " ORDER BY p.id DESC"

    df = execute_query(sql, is_select=True)

    if df.empty:
        st.info("No hay publicaciones disponibles.")
        return

    for _, pub in df.iterrows():
        with st.expander(f"{pub['titulo']}  —  ${pub['precio']} ({pub['tipo']})"):
            st.write(f"**Descripción:** {pub['descripcion']}")
            st.write(f"**Categoría:** {pub['categoria']}")
            st.write(f"**Estado:** {pub['estado']}")
            
            if pub["tipo"].lower() == "alquiler":
                if st.button(f"Alquilar ID {pub['id']}", key=f"alq_{pub['id']}"):
                    st.success("✔️ Has solicitado el alquiler.")
            else:
                if st.button(f"Comprar ID {pub['id']}", key=f"comp_{pub['id']}"):
                    update_sql = f"UPDATE publicaciones SET activoinactivo = 0 WHERE id = {pub['id']}"
                    execute_query(update_sql, is_select=False)

                    st.session_state["compra_iniciada"] = True
                    st.session_state["compra_pub_id"] = pub["id"]
                    st.session_state["compra_tiempo_inicio"] = datetime.now()

                    st.switch_page("pages/confirmar_compra.py")

if __name__ == "__main__":
    if not st.session_state.get("logged_in") or st.session_state.get("role") != "Comprador":
        st.error("❌ Acceso denegado. Inicia sesión como Comprador.")
    else:
        main()
