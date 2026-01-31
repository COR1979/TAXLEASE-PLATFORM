import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Configuración de página
st.set_page_config(page_title="Plataforma TaxLease", layout="wide", page_icon="⚖️")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Plataforma TaxLease v2.0")

# Menú lateral
with st.sidebar:
    st.header("Navegación")
    perfil = st.radio("Ir a:", ["📊 Calculadora Fiscal", "💰 Panel Inversores", "🏢 Área Asesorías"])

if perfil == "📊 Calculadora Fiscal":
    st.header("🧮 Calculadora de Rentabilidad")
    
    with st.form("calc_form"):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Nombre del Cliente/Empresa")
            import_inv = st.number_input("Importe a Invertir (€)", min_value=0, step=1000)
        with col2:
            porcentaje_deduc = st.slider("Porcentaje de Deducción (%)", 10, 30, 20)
            fecha = st.date_input("Fecha de Operación")
        
        submit = st.form_submit_button("Calcular y Registrar")

    if submit:
        # Lógica matemática simple
        ganancia = import_inv * (porcentaje_deduc / 100)
        total_fiscal = import_inv + ganancia
        
        st.success(f"✅ Cálculo realizado: La ganancia fiscal estimada es de {ganancia:,.2f} €")
        
        # Guardar en Google Sheets
        new_data = pd.DataFrame([{
            "Fecha": str(fecha),
            "Cliente": cliente,
            "Inversión": import_inv,
            "Deducción %": porcentaje_deduc,
            "Ganancia": ganancia,
            "Total": total_fiscal,
            "Estado": "Pendiente"
        }])
        
        try:
            existing_data = conn.read(worksheet="Sheet1")
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_df)
            st.balloons()
            st.info("Datos sincronizados con éxito en el panel de control.")
        except Exception as e:
            st.error(f"Error de conexión: {e}")

elif perfil == "💰 Panel Inversores":
    st.header("💰 Oportunidades para Inversores")
    st.write("Cargando operaciones disponibles...")
    # Aquí leeremos las operaciones con 'Estado': 'Validada'

elif perfil == "🏢 Área Asesorías":
    st.header("🏢 Gestión para Asesorías")
    st.write("Listado histórico de expedientes.")
