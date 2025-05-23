import streamlit as st
from functions import get_productos, add_publicacion
import datetime

with st.sidebar:
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.switch_page('Inicio.py')  # o el nombre de tu script principal sin carpeta ni ".py"

if not st.session_state.get('logged_in'):
    st.error("❌ Debes iniciar sesión primero.")
    st.stop()

if st.session_state['role'] != 'Vendedor':  # en vendedor.py
    st.error("❌ Acceso solo para vendedores.")
    st.stop()

st.title("Publicar nuevo producto")

if "user_id" not in st.session_state or st.session_state.get("role") != "Vendedor":
    st.warning("Debes iniciar sesión como vendedor.")
    st.stop()

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