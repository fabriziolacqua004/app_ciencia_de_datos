import psycopg2
import os
from dotenv import load_dotenv
import pandas as pd
import streamlit as st

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
    o DML INSERT/UPDATE/DELETE (devuelve True/False).
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
        # Muestra el error real en Streamlit para depurar
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

def add_publicacion(vendedor_id, titulo, descripcion, tipo, precio):
    sql = """
      INSERT INTO public.publicaciones
        (vendedor_id, titulo, descripcion, tipo, precio)
      VALUES (%s, %s, %s, %s, %s)
    """
    return execute_query(sql, params=(vendedor_id, titulo, descripcion, tipo, precio), is_select=False)
