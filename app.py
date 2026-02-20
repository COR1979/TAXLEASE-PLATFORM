import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai

# 1. CONEXIÓN Y LIMPIEZA QUIRÚRGICA
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    def cargar_datos(hoja):
        df = conn.read(worksheet=hoja, ttl=0)
        # ESTO LIMPIA LOS ESPACIOS Y EVITA EL ERROR 'Representante Legal'
        df.columns = df.columns.str.strip() 
        return df
except Exception as e:
    st.error(f"Error de conexión: {e}")

# 2. ACTIVAR IA (Solo si la clave tiene comillas en Secrets)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash', 
        system_instruction="Eres el Asesor Senior de DERTOGEST. Experto en Art. 39.7 LIS.")

# 3. SECCIÓN PARTNERS (Datos de tu imagen d20bcf)
# ... resto del código que genera el contrato ...
