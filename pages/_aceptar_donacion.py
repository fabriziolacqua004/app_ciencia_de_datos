import streamlit as st
import time
from functions import execute_query, add_confirmacion
from html import escape

# ——————————————————————————————————————————————————————————
# Ocultar menús de Streamlit
# ——————————————————————————————————————————————————————————
st.markdown("""
    <style>
      #MainMenu {visibility: hidden !important;}
      nav[aria-label="Page navigation"] {display: none !important;}
      [data-testid="stSidebarNav"] {display: none !important;}
    </style>
""", unsafe_allow_html=True)

st.title("🤝 Aceptar donación")

# 1) Verificar transacción activa y que sea donación
if 'transaccion' not in st.session_state or st.session_state['transaccion']['tipo'].lower() != 'donación':
    st.error("No hay ninguna donación en proceso.")
    st.stop()

pub_id = st.session_state['transaccion']['pub_id']

# 2) Botón para confirmar la aceptación
if st.button("Aceptar donación", key="aceptar_donacion"):
    # 2.1) Registrar la confirmación
    add_confirmacion(pub_id, st.session_state['user_id'], 'Donación', None)

    # 2.2) Desactivar la publicación para que no aparezca más
    execute_query(
        "UPDATE publicaciones SET activoinactivo = 0 WHERE id = %s",
        params=(pub_id,), is_select=False
    )

    # 2.3) Obtener datos del dueño (vendedor) para contacto
    result = execute_query(
        "SELECT id_vendedor FROM publicaciones WHERE id = %s",
        params=(pub_id,), is_select=True
    )
    if result.empty:
        st.error("❌ No pudimos encontrar al dueño de esta publicación.")
    else:
        id_dueno = int(result.iloc[0]['id_vendedor'])
        info = execute_query(
            "SELECT nombre_y_apellido, numero_de_telefono FROM vendedores WHERE id = %s",
            params=(id_dueno,), is_select=True
        )
        if info.empty:
            st.warning("✅ Donación aceptada. Pero no encontramos datos de contacto del dueño.")
        else:
            nombre_dueno   = info.iloc[0]['nombre_y_apellido']
            telefono_dueno = info.iloc[0]['numero_de_telefono']
            st.info(f"📞 Comunicate con **{ escape(nombre_dueno) }** al **{ escape(telefono_dueno) }** para coordinar la entrega.")

    # 2.4) Mensaje final y redirección
    st.success("✅ Donación aceptada correctamente. Te redirigimos al catálogo...")
    # Limpieza de estado
    for k in ('transaccion',):
        st.session_state.pop(k, None)
    time.sleep(10)
    st.switch_page('pages/comprador.py')

# 3) Botón de cancelar y volver
if st.button("🔙 Volver sin aceptar"):
    st.session_state.pop('transaccion', None)
    st.success("Has cancelado la donación. Redirigiendo al catálogo...")
    time.sleep(1)
    st.switch_page('pages/comprador.py')
