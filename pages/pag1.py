import streamlit as st
# conexion con base de datos
# Import the function from functions.py
try:
    from functions import connect_to_supabase
    print('Successfully imported connect_to_supabase from functions.py')
except ImportError as e:
    print(f'Error importing function: {e}')
    print('Make sure functions.py is in the same directory or in the Python path.')
from dotenv import load_dotenv
load_dotenv()

query = "SELECT * FROM categoria"
execute_query(query)
