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
        # Dividimos en columnas para que el formulario no sea tan largo
        col1, col2 = st.columns(2)
        
        with col1:
            nif = st.text_input("NIF del Partner (ID Único)")
            nombre = st.text_input("Nombre / Razón Social")
            contacto = st.text_input("Persona de Contacto")
        
        with col2:
            email = st.text_input("Email")
            telefono = st.text_input("Teléfono")
            domicilio = st.text_input("Domicilio Social")
        
        comision = st.number_input("Comisión %", value=50)
        
        if st.form_submit_button("Dar de Alta Partner"):
            if not nif or not nombre:
                st.warning("⚠️ El NIF y el Nombre son obligatorios.")
            else:
                try:
                    # 1. LEER DATOS EXISTENTES (TTL=0 para que siempre sea real)
                    df_existente = conn.read(worksheet="PARTNERS", ttl=0)
                    
                    # 2. CREAR LA NUEVA FILA (Orden exacto de tu Excel)
                    # Nota: He añadido "" para la columna G que tienes vacía
                    nueva_fila = pd.DataFrame([{
                        "NIF": nif,
                        "Nombre Partner": nombre,
                        "Persona de Contacto": contacto,
                        "Email": email,
                        "Teléfono": telefono,
                        "Domicilio Social": domicilio,
                        " ": "",  # Esta es tu columna G vacía
                        "Comisión %": comision,
                        "Fecha Alta": datetime.now().strftime("%d/%m/%Y"),
                        "Enlace JV": "" # Columna J
                    }])
                    
                    # 3. UNIR Y ACTUALIZAR
                    # Usamos concat para poner la nueva fila al final sin borrar las anteriores
                    df_final = pd.concat([df_existente, nueva_fila], ignore_index=True)
                    
                    conn.update(worksheet="PARTNERS", data=df_final)
                    
                    st.balloons()
                    st.success(f"✅ Partner '{nombre}' guardado. Los datos anteriores se han mantenido.")
                    
                except Exception as e:
                    st.error(f"❌ Error al conectar con el Excel: {e}")
