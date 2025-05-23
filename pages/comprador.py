import streamlit as st
from functions import execute_query, clean_expired_rentals
from datetime import datetime

with st.sidebar:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.switch_page('Inicio.py')  

if not st.session_state.get('logged_in'):
    st.error("❌ Debes iniciar sesión primero.")
    st.stop()

if st.session_state['role'] != 'Comprador':  # en vendedor.py
    st.error("❌ Acceso solo para Compradores.")
    st.stop()
# Limpiar alquileres expirados al cargar la página
clean_expired_rentals()

st.title("📋 Publicaciones")

# Filtros
categorias = execute_query("SELECT id, descripcion FROM categoria", is_select=True)
categoria_dict = dict(zip(categorias["descripcion"], categorias["id"]))
categoria_seleccionada = st.selectbox("Filtrar por categoría", ["Todas"] + list(categoria_dict.keys()))

estado_seleccionado = st.selectbox("Filtrar por estado", ["Todos", "Nuevo", "Usado"])
tipo_seleccionado = st.selectbox("Filtrar por tipo", ["Todos", "Venta", "Alquiler"])

# Traer datos
sql = """
    SELECT p.id, p.titulo, p.descripcion, p.tipo, p.precio, p.estado,
           c.descripcion AS categoria, p.venta_alquiler
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
    sql += f" AND LOWER(p.venta_alquiler) = LOWER('{tipo_seleccionado}')"
sql += " ORDER BY p.id DESC"

df = execute_query(sql, is_select=True)

if df.empty:
    st.info("No hay publicaciones disponibles.")
    st.stop()

for _, pub in df.iterrows():
    action = "Comprar" if pub["venta_alquiler"].lower() == "venta" else "Alquilar"
    with st.expander(f"{pub['titulo']}  —  ${pub['precio']} ({pub['venta_alquiler']})"):
        st.write(f"**Descripción:** {pub['descripcion']}")
        st.write(f"**Categoría:** {pub['categoria']}")
        st.write(f"**Estado:** {pub['estado']}")
        if st.button(f"{action} ID {pub['id']}", key=f"btn_{pub['id']}"):
            st.session_state['transaccion'] = {'pub_id': pub['id'], 'tipo': pub['venta_alquiler']}
            if pub['venta_alquiler'].lower() == 'venta':
                st.switch_page('pages/_confirmar_compra.py')
            else:
                st.switch_page('pages/_confirmar_alquiler.py')