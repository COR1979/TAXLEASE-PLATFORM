import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Configuración de página
st.set_page_config(page_title="TaxLease Platform v3.0", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ TaxLease Platform-Manager")

# --- NAVEGACIÓN ---
menu = ["🤝 Partners", "💰 Inversores", "🚀 Nueva Operación", "🧹 Limpieza de Datos"]
choice = st.sidebar.selectbox("Menú de Gestión", menu)

# --- 1. SECCIÓN PARTNERS ---
if choice == "🤝 Partners":
    st.header("Gestión de Partners (JV 50%)")
    with st.form("alta_partner"):
        nif = st.text_input("NIF del Partner (ID Único)")
        nombre = st.text_input("Nombre / Razón Social")
        contacto = st.text_input("Persona de Contacto")
        email = st.text_input("Email")
        domicilio = st.text_input("Domicilio Social")
        comision = st.number_input("Comisión %", value=50)
        
        if st.form_submit_button("Dar de Alta Partner"):
            df = conn.read(worksheet="PARTNERS", ttl=0)
            nueva_fila = pd.DataFrame([{
                "NIF": nif, "Nombre Partner": nombre, "Persona de Contacto": contacto,
                "Email": email, "Domicilio Social": domicilio, "Comisión %": comision,
                "Fecha Alta": datetime.now().strftime("%d/%m/%Y")
            }])
            df_final = pd.concat([df, nueva_fila], ignore_index=True)
            conn.update(worksheet="PARTNERS", data=df_final)
            st.success(f"Partner {nombre} registrado con éxito. Generando JV...")

# --- 2. SECCIÓN INVERSORES ---
elif choice == "💰 Inversores":
    st.header("Cartera de Inversores")
    with st.form("alta_inversor"):
        nif = st.text_input("NIF del Inversor (ID Único)")
        razon = st.text_input("Razón Social")
        contacto = st.text_input("Persona de Contacto")
        email = st.text_input("Email")
        facturacion = st.number_input("Facturación Anual (€)", min_value=0)
        cuota = st.number_input("Cuota Íntegra IS (€)", min_value=0)
        
        if st.form_submit_button("Registrar Inversor"):
            df = conn.read(worksheet="INVERSORES", ttl=0)
            nueva_fila = pd.DataFrame([{
                "NIF": nif, "Razón Social": razon, "Persona de Contacto": contacto,
                "Email": email, "Facturación Anual": facturacion, "Cuota IS": cuota,
                "Fecha Alta": datetime.now().strftime("%d/%m/%Y")
            }])
            df_final = pd.concat([df, nueva_fila], ignore_index=True)
            conn.update(worksheet="INVERSORES", data=df_final)
            st.success(f"Inversor {razon} registrado. Hoja de Encargo preparada.")

# --- 3. SECCIÓN CALCULADORA / OPERACIÓN ---
elif choice == "🚀 Nueva Operación":
    st.header("Calculadora de Expediente y Honorarios")
    
    # Cargar datos para selectores
    try:
        df_inv = conn.read(worksheet="INVERSORES", ttl=0)
        df_part = conn.read(worksheet="PARTNERS", ttl=0)
        
        inversor_nif = st.selectbox("Seleccionar Inversor (NIF)", df_inv["NIF"].tolist())
        partner_nif = st.selectbox("Seleccionar Partner (o DIRECTO)", ["DIRECTO"] + df_part["NIF"].tolist())
        
        # Obtener datos del inversor seleccionado para el cálculo
        datos_inv = df_inv[df_inv["NIF"] == inversor_nif].iloc[0]
        
        st.info(f"Inversor: {datos_inv['Razón Social']} | Facturación: {datos_inv['Facturación Anual']:,.2f} €")
        
        # Lógica de Límites
        limite = 0.15 if datos_inv['Facturación Anual'] > 20000000 else 0.50
        inv_optima = (datos_inv['Cuota IS'] * limite) / 1.20
        
        st.metric("Inversión Óptima Sugerida", f"{inv_optima:,.2f} €", help=f"Límite aplicado: {limite*100}%")
        
        monto_final = st.number_input("Importe Inversión Final (€)", value=inv_optima)
        ahorro = monto_final * 0.20
        
        # REGLA DE HONORARIOS (4% o mín. 300€)
        honorarios = max(300.0, monto_final * 0.04)
        st.subheader(f"Honorarios Dertogest: {honorarios:,.2f} €")
        if honorarios == 300: st.caption("(Aplicado pago mínimo de 300€)")

        if st.button("🚀 REGISTRAR EXPEDIENTE"):
            df_exp = conn.read(worksheet="EXPEDIENTES", ttl=0)
            nueva_op = pd.DataFrame([{
                "NIF Inversor": inversor_nif, "NIF Partner": partner_nif,
                "Importe Inversión": monto_final, "Ahorro Neto": ahorro,
                "Honorarios Dertogest": honorarios, "Estado": "Provisión 300€ Pendiente",
                "Fecha Operación": datetime.now().strftime("%d/%m/%Y")
            }])
            df_final = pd.concat([df_exp, nueva_op], ignore_index=True)
            conn.update(worksheet="EXPEDIENTES", data=df_final)
            st.balloons()
            st.success("✅ Operación registrada y sincronizada.")
            
    except Exception as e:
        st.error("Primero debes dar de alta al menos un Inversor.")

# --- 4. LIMPIEZA ---
elif choice == "🧹 Limpieza de Datos":
    st.warning("Zona de Pruebas: Esta acción vacía las tablas de registro.")
    if st.button("BORRAR TODO (MODO TEST)"):
        # Creamos dataframes vacíos con solo los encabezados
        # (Ajustar nombres exactos si los cambiaste en el Excel)
        st.info("Función en desarrollo para limpieza segura.")
