import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="TaxLease Platform v3.0", layout="wide")

# Intentar conexión con diagnóstico
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("⚠️ Error en la configuración de Secrets. Revisa el JSON.")
    st.stop()

st.title("🏛️ TaxLease Platform-Manager")

menu = ["🤝 Partners", "💰 Inversores", "🚀 Nueva Operación"]
choice = st.sidebar.selectbox("Menú de Gestión", menu)

if choice == "🤝 Partners":
    st.header("Gestión de Partners (JV 50%)")
    
    with st.form("alta_partner"):
        nif = st.text_input("NIF del Partner (ID Único)")
        nombre = st.text_input("Nombre / Razón Social")
        contacto = st.text_input("Persona de Contacto")
        email = st.text_input("Email")
        domicilio = st.text_input("Domicilio Social")
        
        if st.form_submit_button("Dar de Alta Partner"):
            if not nif or not nombre:
                st.warning("El NIF y el Nombre son obligatorios.")
            else:
                try:
                    # LEER DATOS EXISTENTES
                    df = conn.read(worksheet="PARTNERS", ttl=0)
                    
                    nueva_fila = pd.DataFrame([{
                        "NIF": nif, "Nombre Partner": nombre, "Persona de Contacto": contacto,
                        "Email": email, "Domicilio Social": domicilio, "Comisión %": 50,
                        "Fecha Alta": datetime.now().strftime("%d/%m/%Y")
                    }])
                    
                    df_final = pd.concat([df, nueva_fila], ignore_index=True)
                    conn.update(worksheet="PARTNERS", data=df_final)
                    st.balloons()
                    st.success(f"✅ Partner {nombre} registrado correctamente en el Excel.")
                except Exception as e:
                    st.error(f"❌ Error al escribir en el Excel: {e}")
                    st.info("Asegúrate de que la pestaña se llame PARTNERS (en mayúsculas).")
