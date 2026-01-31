import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Plataforma TaxLease", layout="wide", page_icon="⚖️")

# Conexión principal
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Plataforma TaxLease v2.0")

with st.sidebar:
    st.header("Navegación")
    perfil = st.radio("Ir a:", ["📊 Calculadora Fiscal", "💰 Panel Inversores", "🏢 Área Asesorías"])

if perfil == "📊 Calculadora Fiscal":
    st.header("🧮 Simulación de Ahorro Fiscal (I+D+i)")
    
    with st.form("calc_form"):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Empresa Beneficiaria")
            facturacion = st.number_input("Facturación Anual (€)", min_value=0, step=1000000)
            import_inv = st.number_input("Inversión en el Proyecto (€)", min_value=0, step=1000)
        with col2:
            cuota_is = st.number_input("Cuota Íntegra IS Estimada (€)", min_value=1, step=1000)
            fecha = st.date_input("Fecha de Simulación")
        
        submit = st.form_submit_button("Calcular y Registrar en EXPEDIENTES")

    if submit:
        # LÓGICA DE SEGURIDAD (Margen 5%)
        ahorro_bruto = import_inv * 0.25
        ahorro_neto = ahorro_bruto * 0.95
        
        # MOSTRAR RESULTADOS
        st.subheader("Análisis de la Operación")
        c1, c2 = st.columns(2)
        c1.metric("Deducción Aplicada", "25%")
        c2.metric("Ahorro Neto (Oferta)", f"{ahorro_neto:,.2f} €", delta="-5% Seguridad")

        # SINCRONIZACIÓN CON PESTAÑA 'EXPEDIENTES'
        new_data = pd.DataFrame([{
            "Fecha": str(fecha),
            "Cliente": cliente,
            "Inversión": import_inv,
            "Ahorro Neto": ahorro_neto,
            "Estado": "Pendiente de Validar"
        }])
        
        try:
            # LEEMOS LA PESTAÑA CORRECTA SEGÚN TU IMAGEN
            df_actual = conn.read(worksheet="EXPEDIENTES") 
            df_final = pd.concat([df_actual, new_data], ignore_index=True)
            conn.update(worksheet="EXPEDIENTES", data=df_final)
            st.balloons()
            st.success("✅ ¡Operación registrada en la pestaña EXPEDIENTES!")
        except Exception as e:
            st.error(f"Error: No se encuentra la pestaña 'EXPEDIENTES' o falta permiso de Editor.")
