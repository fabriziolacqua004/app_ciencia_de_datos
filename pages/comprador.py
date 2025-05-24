import streamlit as st
from functions import execute_query, clean_expired_rentals
from datetime import datetime
import webbrowser

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

# Sidebar – Cerrar sesión
with st.sidebar:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.switch_page('Inicio.py')

# Verificar sesión y rol
if not st.session_state.get('logged_in'):
    st.error("❌ Debes iniciar sesión primero.")
    st.stop()
if st.session_state['role'] != 'Comprador':
    st.error("❌ Acceso solo para Compradores.")
    st.stop()

# Limpiar alquileres expirados
clean_expired_rentals()

st.title("📋 Publicaciones")

# Filtros
categorias = execute_query("SELECT id, descripcion FROM categoria", is_select=True)
categoria_dict = dict(zip(categorias["descripcion"], categorias["id"]))
categoria_seleccionada = st.selectbox(
    "Filtrar por categoría",
    ["Todas"] + list(categoria_dict.keys())
)
estado_seleccionado = st.selectbox("Filtrar por estado", ["Todos", "Nuevo", "Usado"])
tipo_seleccionado   = st.selectbox("Filtrar por tipo", ["Todos", "Venta", "Alquiler"])

# Ordenamientos
precio_orden = st.selectbox("Filtrar por precio", ["Ninguno", "Menor a Mayor", "Mayor a Menor"], index=0)
alfabetico   = st.checkbox("Ordenar alfabéticamente?", value=False)

# Construir consulta
sql = """
    SELECT p.id, p.titulo, p.descripcion, p.tipo, p.precio, p.estado,
           c.descripcion AS categoria, p.venta_alquiler, p.id_vendedor, p.link_acceso
    FROM publicaciones p
    JOIN productos pr ON p.id_producto = pr.id
    JOIN categoria c  ON pr.id_categoria = c.id
    WHERE p.activoinactivo = 1
"""
# Aplicar filtros
if categoria_seleccionada != "Todas":
    sql += f" AND c.id = {categoria_dict[categoria_seleccionada]}"
if estado_seleccionado != "Todos":
    sql += f" AND LOWER(p.estado) = LOWER('{estado_seleccionado}')"
if tipo_seleccionado != "Todos":
    sql += f" AND LOWER(p.venta_alquiler) = LOWER('{tipo_seleccionado}')"
# Aplicar ordenamientos
if alfabetico:
    sql += " ORDER BY p.titulo ASC"
elif precio_orden == "Menor a Mayor":
    sql += " ORDER BY p.precio ASC"
elif precio_orden == "Mayor a Menor":
    sql += " ORDER BY p.precio DESC"
else:
    sql += " ORDER BY p.id DESC"

df = execute_query(sql, is_select=True)

if df.empty:
    st.info("No hay publicaciones disponibles.")
    st.stop()

for _, pub in df.iterrows():
    with st.expander(f"{pub['titulo']} — ${pub['precio']} ({pub['venta_alquiler']})"):
        st.write(f"**Descripción:** {pub['descripcion']}")
        st.write(f"**Categoría:** {pub['categoria']}")
        st.write(f"**Estado:** {pub['estado']}")

        if pub["id_vendedor"] in [1, 2, 3]:
            if st.button(f"🔗 Visitar link (ID {pub['id']})", key=f"link_{pub['id']}"):
                webbrowser.open_new_tab(pub["link_acceso"])
        else:
            accion = "Comprar" if pub["venta_alquiler"].lower() == "venta" else "Alquilar"
            if st.button(f"{accion} ID {pub['id']}", key=f"btn_{pub['id']}"):
                st.session_state['transaccion'] = {
                    'pub_id': pub['id'],
                    'tipo':   pub['venta_alquiler']
                }
                if pub['venta_alquiler'].lower() == 'venta':
                    st.switch_page('pages/_confirmar_compra.py')
                else:
                    st.switch_page('pages/_confirmar_alquiler.py')
