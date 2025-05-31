import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
from supabase import create_client, Client
from typing import Tuple
# Carga variables de entorno desde .env
load_dotenv()


def connect_to_supabase():
    host     = os.getenv("SUPABASE_DB_HOST")
    port     = os.getenv("SUPABASE_DB_PORT")
    dbname   = os.getenv("SUPABASE_DB_NAME")
    user     = os.getenv("SUPABASE_DB_USER")
    password = os.getenv("SUPABASE_DB_PASSWORD")

    if not all([host, port, dbname, user, password]):
        st.error("❌ Faltan variables de entorno de Supabase en .env")
        return None

    try:
        conn = psycopg2.connect(
            host=host, port=port, dbname=dbname,
            user=user, password=password
        )
        return conn
    except psycopg2.Error as e:
        st.error(f"❌ Error de conexión a la base de datos: {e}")
        return None


def execute_query(query, params=None, conn=None, is_select=True):
    """
    Ejecuta una consulta SELECT (devuelve DataFrame)
    o una consulta DML INSERT/UPDATE/DELETE (devuelve True/False).
    """
    close_conn = False
    try:
        if conn is None:
            conn = connect_to_supabase()
            close_conn = True
        if conn is None:
            return pd.DataFrame() if is_select else False

        cursor = conn.cursor()
        cursor.execute(query, params)

        if is_select:
            rows = cursor.fetchall()
            cols = [d[0] for d in cursor.description]
            df = pd.DataFrame(rows, columns=cols)
            result = df
        else:
            conn.commit()
            result = True

        cursor.close()
        if close_conn:
            conn.close()

        return result

    except Exception as e:
        st.error(f"DB error: {e}")
        if conn and not is_select:
            conn.rollback()
        return pd.DataFrame() if is_select else False


def add_vendedor(nombre_y_apellido, ubicacion, telefono, mail, usuario, contraseña):
    sql = """
        INSERT INTO public.vendedores
        (
          "nombre_y_apellido",
          "ubicacion",
          "numero_de_telefono",
          "mail",
          "nombre_de_usuario",
          "contraseña"
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (nombre_y_apellido, ubicacion, telefono, mail, usuario, contraseña)
    return execute_query(sql, params=params, is_select=False)


def add_comprador(nombre_y_apellido, ubicacion, telefono, mail, usuario, contraseña):
    sql = """
        INSERT INTO public.compradores
        (
          "nombre_y_apellido",
          "ubicacion",
          "numero_de_telefono",
          "mail",
          "nombre_de_usuario",
          "contraseña"
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (nombre_y_apellido, ubicacion, telefono, mail, usuario, contraseña)
    return execute_query(sql, params=params, is_select=False)


def add_publicacion(
    id_producto,
    id_vendedor,
    titulo,
    descripcion,
    tipo,
    estado,
    precio,
    fecha_de_creacion,
    link_acceso,
    venta_alquiler,
    imagen_url,
    activoinactivo=1
):
    """
    Inserta una nueva publicación, ahora con imagen_url.
    - imagen_url: string con la URL pública de la foto en Supabase Storage
    """
    sql = """
        INSERT INTO public.publicaciones (
            id_producto, id_vendedor, titulo, descripcion, tipo, estado,
            precio, fecha_de_creacion, link_acceso, venta_alquiler,
            imagen_url, activoinactivo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (
        id_producto,
        id_vendedor,
        titulo,
        descripcion,
        tipo,
        estado,
        precio,
        fecha_de_creacion,
        link_acceso,
        venta_alquiler,
        imagen_url,
        activoinactivo
    )
    return execute_query(sql, params=params, is_select=False)


def get_productos():
    sql = "SELECT id, nombre FROM public.productos"
    df = execute_query(sql, is_select=True)
    return df.to_dict("records")


def update_publicacion_activo(id_publicacion: int, activo: int) -> bool:
    sql = """
       UPDATE public.publicaciones
       SET activoinactivo = %s
       WHERE id = %s
    """
    return execute_query(sql, params=(activo, id_publicacion), is_select=False)



def delete_publicacion(id_publicacion: int) -> Tuple[bool, str]:
    # 1) Verificar confirmaciones
    sql_check = """
        SELECT COUNT(*) AS cnt
        FROM public.confirmaciones
        WHERE id_publicacion = %s
    """
    df_check = execute_query(sql_check, params=(id_publicacion,), is_select=True)
    if int(df_check.loc[0, "cnt"]) > 0:
        return False, "❌ No se puede borrar: hay confirmaciones relacionadas."
    # 2) Borrar si no hay
    sql_delete = "DELETE FROM public.publicaciones WHERE id = %s"
    if execute_query(sql_delete, params=(id_publicacion,), is_select=False):
        return True, "✅ Publicación borrada correctamente."
    return False, "❌ Error al ejecutar el borrado."


def clean_expired_rentals():
    """
    Borra confirmaciones expiradas (fecha_confirmacion + vigencia días < NOW)
    y reactiva las publicaciones correspondientes.
    """
    # 1) Seleccionar publicaciones expiradas
    sql_select = """
        SELECT id_publicacion
        FROM public.confirmaciones
        WHERE fecha_confirmacion + (vigencia * INTERVAL '1 day') < NOW()
    """
    df = execute_query(sql_select, is_select=True)
    if df.empty:
        return True

    ids = tuple(df['id_publicacion'].tolist())
    # 2) Borrar confirmaciones expiradas
    sql_delete = "DELETE FROM public.confirmaciones WHERE id_publicacion IN %s"
    execute_query(sql_delete, params=(ids,), is_select=False)
    # 3) Reactivar publicaciones
    sql_update = "UPDATE public.publicaciones SET activoinactivo = 1 WHERE id IN %s"
    execute_query(sql_update, params=(ids,), is_select=False)
    return True


def add_confirmacion(
    id_publicacion: int,
    id_comprador: int,
    metodo_pago: str,
    vigencia: int | None
) -> bool:
    """
    Inserta una confirmación con:
      - vigencia: número de días para alquiler, o None para venta permanente.
    """
    sql = """
       INSERT INTO public.confirmaciones
         (id_publicacion, id_comprador, metodo_de_pago, vigencia)
       VALUES (%s, %s, %s, %s)
    """
    return execute_query(
        sql,
        params=(id_publicacion, id_comprador, metodo_pago, vigencia),
        is_select=False
    )


# ----------------------------------------------------
# Configuración e inicialización del cliente Supabase
# (solo se usa para upload/obtener URL de imagen)
# ----------------------------------------------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

supabase: Client = None


def init_supabase_client():
    """
    Inicializa la variable global 'supabase' llamando a create_client().
    Si falta la URL o la KEY en .env, muestra error y devuelve None.
    """
    global supabase
    if supabase is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            st.error("❌ Falta configurar SUPABASE_URL o SUPABASE_ANON_KEY en .env")
            return None
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase
