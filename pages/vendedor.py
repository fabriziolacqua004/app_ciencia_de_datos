import streamlit as st
from datetime import date

from functions import (
    execute_query,
    get_productos,
    add_publicacion,
    init_supabase_client,
    update_publicacion_activo,
    delete_publicacion
)

# ——————————————————————————————————————————————————————————
# Estilos: ocultar menú lateral, navegación, etc.
# ——————————————————————————————————————————————————————————
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

# ——————————————————————————————————————————————————————————
# Sidebar – Cerrar sesión
# ——————————————————————————————————————————————————————————
with st.sidebar:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.switch_page("Inicio.py")

# ——————————————————————————————————————————————————————————
# Verificar sesión y rol
# ——————————————————————————————————————————————————————————
if not st.session_state.get("logged_in"):
    st.error("❌ Debes iniciar sesión primero.")
    st.stop()
if st.session_state.get("role") != "Vendedor":
    st.error("❌ Acceso solo para vendedores.")
    st.stop()

st.title("Panel del Vendedor")

# ——————————————————————————————————————————————————————————
# 1. Crear Publicación (con imagen)
# ——————————————————————————————————————————————————————————
st.header("🌐 Publicar nuevo producto")

productos = get_productos()
opciones = {p["nombre"]: p["id"] for p in productos}

with st.form("publicar_form"):
    titulo          = st.text_input("Título de la publicación")
    descripcion     = st.text_area("Descripción")
    tipo            = st.text_input("Tipo de producto (opcional)")
    estado          = st.selectbox("Estado del producto", ["Nuevo", "Usado"])
    precio          = st.number_input("Precio", min_value=0.0, step=0.01)
    link            = st.text_input("Link de acceso (opcional)")
    venta_alquiler  = st.selectbox("¿Es para venta o alquiler?", ["Venta", "Alquiler"])
    producto_nombre = st.selectbox("Seleccionar producto", list(opciones.keys()))

    uploaded_file = st.file_uploader(
        "📷 Subí una foto (JPEG/PNG)", type=["jpg", "jpeg", "png"]
    )

    if st.form_submit_button("Publicar"):
        if not titulo or not descripcion:
            st.error("❌ Completa título y descripción.")
        elif uploaded_file is None:
            st.error("❌ Debes subir una imagen (JPEG/PNG).")
        else:
            file_bytes = uploaded_file.read()

            supabase = init_supabase_client()
            if not supabase:
                st.error("❌ No se pudo inicializar Supabase. Revisa .env")
            else:
                import time as _time
                extension = uploaded_file.name.split(".")[-1]
                timestamp = int(_time.time())
                file_name = f"publicacion_{st.session_state['user_id']}_{timestamp}.{extension}"

                try:
                    bucket = supabase.storage.from_("bucketimagenespublicaciones")
                except Exception as e:
                    st.error(f"❌ No se pudo acceder al bucket: {e}")
                    st.stop()

                try:
                    bucket.upload(
                        file_name,
                        file_bytes,
                        {"cacheControl": "3600", "upsert": False}
                    )
                except Exception as e:
                    st.error(f"❌ Error al subir la imagen: {e}")
                    st.stop()

                try:
                    imagen_url = bucket.get_public_url(file_name)
                except Exception as e:
                    st.error(f"❌ No se pudo obtener la URL pública de la imagen: {e}")
                    imagen_url = None

                if not imagen_url:
                    st.error("❌ No se obtuvo ninguna URL de la imagen, abortando creación.")
                else:
                    id_producto    = opciones[producto_nombre]
                    id_vendedor    = st.session_state["user_id"]
                    fecha_creacion = date.today()

                    success = add_publicacion(
                        id_producto, id_vendedor, titulo, descripcion,
                        tipo, estado, precio, fecha_creacion,
                        link, venta_alquiler, imagen_url
                    )

                    if success:
                        st.success("✅ Publicación creada correctamente con imagen.")
                    else:
                        st.error("❌ Hubo un error al insertar la publicación en la base de datos.")

# ——————————————————————————————————————————————————————————
# 2. Ver “Mis publicaciones” con botones para borrar y activar/desactivar
# ——————————————————————————————————————————————————————————
st.header("📄 Mis publicaciones")
id_vendedor = st.session_state["user_id"]

sql_pub = f"""
    SELECT 
      p.id,
      p.titulo,
      p.descripcion,
      p.precio,
      p.estado,
      p.venta_alquiler,
      p.activoinactivo,
      p.imagen_url
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
            if row.get("imagen_url"):
                st.image(row["imagen_url"], width=300)
                st.write("")  # Espacio debajo de la imagen

            st.write(f"**Descripción:** {row['descripcion']}")
            st.write(f"**Estado:** {row['estado']}")
            st.write(f"**Publicación:** {estado_pub}")

            col1, col2 = st.columns([1, 1])

            # —————————— Botón para Activar/Desactivar ——————————
            with col1:
                btn_label = "Desactivar" if row["activoinactivo"] == 1 else "Activar"
                key_act = f"btn_estado_{row['id']}"
                if st.button(f"{btn_label} publicación ID {row['id']}", key=key_act):
                    nuevo_estado = 0 if row["activoinactivo"] == 1 else 1
                    updated = update_publicacion_activo(row["id"], nuevo_estado)
                    if updated:
                        st.success(
                            f"✅ Publicación {'desactivada' if nuevo_estado == 0 else 'activada'} correctamente."
                        )
                    else:
                        st.error("❌ Error al actualizar el estado.")
                    # Al pulsar este botón, Streamlit vuelve a ejecutar todo el script,
                    # así que df_pub se refresca automáticamente con el nuevo valor.

            # —————————— Botón para Borrar ——————————
            with col2:
                key_del = f"btn_borrar_{row['id']}"
                if st.button(f"🗑️ Borrar publicación ID {row['id']}", key=key_del):
                    borrado, mensaje = delete_publicacion(row["id"])
                    if borrado:
                        st.success(mensaje)
                    else:
                        st.error(mensaje)
                    # Al pulsar este botón, Streamlit vuelve a ejecutar todo el script,
                    # así que df_pub se refresca automáticamente, eliminando (o no) la fila.

# ——————————————————————————————————————————————————————————
# 3. Ver Todas las Publicaciones Disponibles (sin botones de compra/alquiler)
# ——————————————————————————————————————————————————————————
st.header("📅 Ver publicaciones disponibles")

categorias     = execute_query("SELECT id, descripcion FROM categoria", is_select=True)
categoria_dict = dict(zip(categorias["descripcion"], categorias["id"]))
categoria_sel  = st.selectbox("Filtrar por categoría", ["Todas"] + list(categoria_dict.keys()))
estado_sel     = st.selectbox("Filtrar por estado", ["Todos", "Nuevo", "Usado"])
tipo_sel       = st.selectbox("Filtrar por tipo", ["Todos", "Venta", "Alquiler"])
precio_orden   = st.selectbox("Filtrar por precio", ["Ninguno", "Menor a Mayor", "Mayor a Menor"], index=0)
alfabetico     = st.checkbox("Ordenar alfabéticamente?", value=False)

sql_all = """
    SELECT 
      p.id,
      p.titulo,
      p.descripcion,
      p.tipo,
      p.precio,
      p.estado,
      c.descripcion AS categoria,
      p.venta_alquiler,
      p.imagen_url
    FROM publicaciones p
    JOIN productos pr ON p.id_producto = pr.id
    JOIN categoria c  ON pr.id_categoria = c.id
    WHERE p.activoinactivo = 1
"""
if categoria_sel != "Todas":
    sql_all += f" AND c.id = {categoria_dict[categoria_sel]}"
if estado_sel != "Todos":
    sql_all += f" AND LOWER(p.estado) = LOWER('{estado_sel}')"
if tipo_sel != "Todos":
    sql_all += f" AND LOWER(p.venta_alquiler) = LOWER('{tipo_sel}')"

if alfabetico:
    sql_all += " ORDER BY p.titulo ASC"
elif precio_orden == "Menor a Mayor":
    sql_all += " ORDER BY p.precio ASC"
elif precio_orden == "Mayor a Menor":
    sql_all += " ORDER BY p.precio DESC"
else:
    sql_all += " ORDER BY p.id DESC"

df_all = execute_query(sql_all, is_select=True)

if df_all.empty:
    st.info("No hay publicaciones disponibles.")
else:
    for _, pub in df_all.iterrows():
        with st.expander(f"{pub['titulo']} — ${pub['precio']} ({pub['venta_alquiler']})"):
            if pub.get("imagen_url"):
                st.image(pub["imagen_url"], width=300)
                st.write("")

            st.write(f"**Descripción:** {pub['descripcion']}")
            st.write(f"**Estado:** {pub['estado']}")
            st.write(f"**Categoría:** {pub['categoria']}")
# ——————————————————————————————————————————————————————————
# 4. Ver confirmaciones de mis publicaciones
# ——————————————————————————————————————————————————————————
# ——————————————————————————————————————————————————————————
# 4. Ver confirmaciones de mis publicaciones (vigencia “Permanente” si es NULL)
# ——————————————————————————————————————————————————————————
st.header("🔔 Confirmaciones recibidas")

sql_conf = f"""
    SELECT 
      conf.metodo_de_pago,
      conf.fecha_confirmacion,
      CASE 
        WHEN conf.vigencia IS NULL THEN 'Permanente'
        ELSE conf.vigencia::TEXT
      END AS vigencia,
      cmp."nombre_y_apellido" AS comprador,
      p.titulo AS publicacion
    FROM public.confirmaciones conf
    JOIN public.publicaciones p 
      ON conf.id_publicacion = p.id
    JOIN public.compradores cmp 
      ON conf.id_comprador = cmp.id
    WHERE p.id_vendedor = {id_vendedor}
    ORDER BY conf.fecha_confirmacion DESC
"""
df_conf = execute_query(sql_conf, is_select=True)

if df_conf.empty:
    st.info("No hay confirmaciones para tus publicaciones.")
else:
    st.table(df_conf[["metodo_de_pago", "fecha_confirmacion", "vigencia", "comprador", "publicacion"]])

