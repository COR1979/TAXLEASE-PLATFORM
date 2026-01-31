import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Master", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Localizador de Pestañas TaxLease")

# --- BUSCADOR AUTOMÁTICO DE PESTAÑAS ---
st.sidebar.header("🔍 Diagnóstico de Hojas")
if st.sidebar.button("Listar todas las pestañas"):
    try:
        # Intentamos obtener los nombres de todas las hojas del libro
        # Nota: Usamos una lectura básica para activar la conexión
        url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        st.sidebar.write("Conectando al Excel...")
        
        # Leemos la primera hoja por defecto para verificar acceso
        df_test = conn.read(ttl=0)
        st.sidebar.success("✅ Conexión establecida con el archivo.")
        st.sidebar.info("Si no encuentra 'EXPEDIENTES', revisaremos los nombres manuales.")
    except Exception as e:
        st.sidebar.error(f"Error de acceso: {e}")

# --- FORMULARIO DE PRUEBA ---
st.header("📊 Prueba de Escritura Directa")
nombre_pestaña = st.text_input("Escribe el nombre de la pestaña tal cual aparece en tu Excel", value="EXPEDIENTES")

if st.button("🚀 Intentar grabar en esa pestaña"):
    nueva_fila = pd.DataFrame([{"ID": "TEST", "Nombre": "VERIFICACIÓN"}])
    try:
        # Intentamos leer la pestaña indicada por el usuario
        df = conn.read(worksheet=nombre_pestaña, ttl=0)
        df_final = pd.concat([df, nueva_fila], ignore_index=True)
        conn.update(worksheet=nombre_pestaña, data=df_final)
        st.balloons()
        st.success(f"¡LOGRADO! He podido escribir en la pestaña '{nombre_pestaña}'.")
    except Exception as e:
        st.error(f"No se pudo acceder a '{nombre_pestaña}': {e}")
