import streamlit as st
from functions import execute_query, get_productos, add_publicacion
import datetime

# Sidebar - Cerrar sesión
with st.sidebar:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.switch_page('Inicio.py')

# Verificar sesión y rol
if not st.session_state.get('logged_in'):
    st.error("❌ Debes iniciar sesión primero.")
    st.stop()

if st.session_state['role'] != 'Vendedor':
    st.error("❌ Acceso solo para vendedores.")
    st.stop()

st.title("Panel del Vendedor")

# ===================
# 1. Crear Publicación
# ===================
st.header("🌐 Publicar nuevo producto")
productos = get_productos()
opciones = {p["nombre"]: p["id"] for p in productos}

with st.form("publicar_form"):
    titulo     = st.text_input("Título de la publicación")
    descripcion= st.text_area("Descripción")
    tipo       = st.text_input("Tipo de producto (opcional)")
    estado     = st.selectbox("Estado del producto", ["Nuevo", "Usado"])
    precio     = st.number_input("Precio", min_value=0.0, step=0.01)
    link       = st.text_input("Link de acceso (opcional)")
    venta_alquiler = st.selectbox("¿Es para venta o alquiler?", ["Venta", "Alquiler"])
    producto_nombre = st.selectbox("Seleccionar tipo de producto", list(opciones.keys()))

    if st.form_submit_button("Publicar"):
        if not titulo or not descripcion:
            st.error("Completa todos los campos obligatorios.")
        else:
            id_producto = opciones[producto_nombre]
            id_vendedor = st.session_state["user_id"]
            fecha_creacion = datetime.date.today()

            success = add_publicacion(
                id_producto, id_vendedor, titulo, descripcion,
                tipo, estado, precio, fecha_creacion,
                link, venta_alquiler
            )
            if success:
                st.success("Publicación creada correctamente.")
            else:
                st.error("Error al crear la publicación.")

# ==============================
# 2. Ver Publicaciones Propias
# ==============================
st.header("📄 Mis publicaciones")
id_vendedor = st.session_state["user_id"]
sql_pub = f"""
    SELECT p.titulo, p.descripcion, p.precio, p.estado, p.venta_alquiler, p.activoinactivo
    FROM publicaciones p
    WHERE p.id_vendedor = {id_vendedor}
    ORDER BY p.id DESC
"""
df_pub = execute_query(sql_pub, is_select=True)

if df_pub.empty:
    st.info("Aún no tienes publicaciones.")
else:
    for _, row in df_pub.iterrows():
        estado_pub = "Activa" if row["activoinactivo"] == 1 else "Inactiva"
        with st.expander(f"{row['titulo']} — ${row['precio']} ({row['venta_alquiler']})"):
            st.write(f"**Descripción:** {row['descripcion']}")
            st.write(f"**Estado:** {row['estado']}")
            st.write(f"**Publicación:** {estado_pub}")

# ===============================
# 3. Ver Confirmaciones Recibidas
# ===============================
st.header("🛎️ Confirmaciones de compra/alquiler")
sql_conf = f"""
    SELECT p.titulo, c.fecha_confirmacion, c.metodo_de_pago, c.vigencia, co.nombre_y_apellido AS comprador
    FROM confirmaciones c
    JOIN publicaciones p ON p.id = c.id_publicacion
    JOIN compradores co ON co.id = c.id_comprador
    WHERE p.id_vendedor = {id_vendedor}
    ORDER BY c.fecha_confirmacion DESC
"""
df_conf = execute_query(sql_conf, is_select=True)

if df_conf.empty:
    st.info("Todavía no tienes confirmaciones.")
else:
    for _, row in df_conf.iterrows():
        with st.expander(f"{row['titulo']} ({row['fecha_confirmacion']})"):
            st.write(f"**Comprador:** {row['comprador']}")
            st.write(f"**Método de pago:** {row['metodo_de_pago']}")
            vigencia = row["vigencia"]
            if vigencia is None:
                vigencia_str = "permanente"
            else:
                vigencia_str = f"{vigencia} días"
            st.write(f"**Vigencia:** {vigencia_str}")

# ========================================
# 4. Ver Todas las Publicaciones (sin botones)
# ========================================
st.header("📅 Ver publicaciones disponibles")
categorias = execute_query("SELECT id, descripcion FROM categoria", is_select=True)
categoria_dict = dict(zip(categorias["descripcion"], categorias["id"]))
categoria_sel = st.selectbox("Filtrar por categoría", ["Todas"] + list(categoria_dict.keys()))
estado_sel    = st.selectbox("Filtrar por estado", ["Todos", "Nuevo", "Usado"])
tipo_sel      = st.selectbox("Filtrar por tipo", ["Todos", "Venta", "Alquiler"])

sql_all = """
    SELECT p.id, p.titulo, p.descripcion, p.tipo, p.precio, p.estado,
           c.descripcion AS categoria, p.venta_alquiler
    FROM publicaciones p
    JOIN productos pr ON p.id_producto = pr.id
    JOIN categoria c ON pr.id_categoria = c.id
    WHERE p.activoinactivo = 1
"""
if categoria_sel != "Todas":
    sql_all += f" AND c.id = {categoria_dict[categoria_sel]}"
if estado_sel != "Todos":
    sql_all += f" AND LOWER(p.estado) = LOWER('{estado_sel}')"
if tipo_sel != "Todos":
    sql_all += f" AND LOWER(p.venta_alquiler) = LOWER('{tipo_sel}')"
sql_all += " ORDER BY p.id DESC"

df_all = execute_query(sql_all, is_select=True)

if df_all.empty:
    st.info("No hay publicaciones disponibles.")
else:
    for _, pub in df_all.iterrows():
        with st.expander(f"{pub['titulo']} — ${pub['precio']} ({pub['venta_alquiler']})"):
            st.write(f"**Descripción:** {pub['descripcion']}")
            st.write(f"**Categoría:** {pub['categoria']}")
            st.write(f"**Estado:** {pub['estado']}")

