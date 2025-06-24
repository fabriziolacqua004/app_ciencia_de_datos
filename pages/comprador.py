# pages/comprador.py
import streamlit as st
from functions import execute_query, clean_expired_rentals
from datetime import datetime
import webbrowser
from html import escape

# ——————————————————————————————————————————————————————————
# Estilos CSS para tarjetas azules (con !important)
# ——————————————————————————————————————————————————————————
st.markdown("""
    <style>
      /* Oculta elementos innecesarios */
      #MainMenu {visibility: hidden !important;}
      nav[aria-label="Page navigation"] {display: none !important;}
      [data-testid="stSidebarNav"] {display: none !important;}
      /* Estilos de tarjeta */
      .card {
        background-color: #e6f2ff !important;
        padding: 20px !important;
        border-radius: 10px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
      }
      .card img {
        max-width: 100% !important;
        border-radius: 8px !important;
        display: block !important;
        margin-bottom: 10px !important;
      }
      .card-title {
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        color: #004080 !important;
        margin-bottom: 0.5rem !important;
      }
      .card-body p {
        margin: 0.25rem 0 !important;
      }
    </style>
""", unsafe_allow_html=True)

# Sidebar – Cerrar sesión
with st.sidebar:
    if st.button("🚪 Cerrar sesión", key="cerrar_sesion_comprador"):
        st.session_state.clear()
        st.switch_page("Inicio.py")

# Validar sesión y rol
if not st.session_state.get("logged_in"):
    st.error("❌ Debes iniciar sesión primero.")
    st.stop()
if st.session_state.get("role") != "Comprador":
    st.error("❌ Acceso solo para Compradores.")
    st.stop()

# Limpiar alquileres expirados
clean_expired_rentals()

st.title("📋 Publicaciones")

# Filtros y ordenamientos
categorias = execute_query("SELECT id, descripcion FROM categoria", is_select=True)
categoria_dict = dict(zip(categorias["descripcion"], categorias["id"]))

categoria_seleccionada = st.selectbox("Filtrar por categoría", ["Todas"] + list(categoria_dict.keys()))
estado_seleccionado    = st.selectbox("Filtrar por estado", ["Todos", "Nuevo", "Usado"])
tipo_seleccionado      = st.selectbox(
    "Filtrar por tipo",
    ["Todos", "Venta", "Alquiler", "Donación"]
)
precio_orden           = st.selectbox("Ordenar por precio", ["Ninguno", "Menor a Mayor", "Mayor a Menor"], index=0)
alfabetico             = st.checkbox("Ordenar alfabéticamente?", value=False)

# Construir y ejecutar consulta
sql = [
    "SELECT p.id, p.titulo, p.descripcion, p.precio, p.estado, c.descripcion AS categoria,",
    "p.venta_alquiler, p.id_vendedor, p.link_acceso, p.imagen_url",
    "FROM publicaciones p",
    "JOIN productos pr ON p.id_producto = pr.id",
    "JOIN categoria c  ON pr.id_categoria = c.id",
    "WHERE p.activoinactivo = 1"
]
if categoria_seleccionada != "Todas":
    sql.append(f"AND c.id = {categoria_dict[categoria_seleccionada]}")
if estado_seleccionado != "Todos":
    sql.append(f"AND LOWER(p.estado) = LOWER('{estado_seleccionado}')")
if tipo_seleccionado != "Todos":
    sql.append(f"AND LOWER(p.venta_alquiler) = LOWER('{tipo_seleccionado}')")

if alfabetico:
    sql.append("ORDER BY p.titulo ASC")
elif precio_orden == "Menor a Mayor":
    sql.append("ORDER BY p.precio ASC")
elif precio_orden == "Mayor a Menor":
    sql.append("ORDER BY p.precio DESC")
else:
    sql.append("ORDER BY p.id DESC")

query = " ".join(sql)
df = execute_query(query, is_select=True)

if df.empty:
    st.info("No hay publicaciones disponibles.")
    st.stop()

# Renderizar tarjetas con HTML
for _, pub in df.iterrows():
    parts = ["<div class='card'>"]
    if pub.get("imagen_url"):
        img_url = escape(pub["imagen_url"])
        parts.append(f"<img src='{img_url}' alt='Imagen publicación' />")
    title = escape(pub['titulo'])
    price_disp = f"${pub['precio']}" if pub['venta_alquiler'].lower() != "donación" else "Gratis"
    parts.append(f"<div class='card-title'>{title} — {price_disp} ({pub['venta_alquiler']})</div>")
    parts.append("<div class='card-body'>")
    parts.append(f"<p><strong>Descripción:</strong> {escape(pub['descripcion'])}</p>")
    parts.append(f"<p><strong>Categoría:</strong> {escape(pub['categoria'])}</p>")
    parts.append(f"<p><strong>Estado:</strong> {escape(pub['estado'])}</p>")
    parts.append("</div></div>")
    html = "".join(parts)
    st.markdown(html, unsafe_allow_html=True)

    # Botones de acción
    if pub["id_vendedor"] in [1, 2, 3]:
        if st.button("🔗 Visitar link", key=f"link_{pub['id']}"):
            webbrowser.open_new_tab(pub["link_acceso"])
    else:
        venta_tipo = pub["venta_alquiler"].lower()
        if venta_tipo == "venta":
            label = "Comprar"
            page = "_confirmar_compra.py"
        elif venta_tipo == "alquiler":
            label = "Alquilar"
            page = "_confirmar_alquiler.py"
        else:
            label = "Aceptar donación"
            page = "_aceptar_donacion.py"

        if st.button(label, key=f"btn_{venta_tipo}_{pub['id']}"):
            st.session_state["transaccion"] = {
                "pub_id": pub["id"],
                "tipo": pub["venta_alquiler"]
            }
            st.switch_page(f"pages/{page}")

