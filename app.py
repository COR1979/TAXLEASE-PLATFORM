import streamlit as st
from streamlit_gsheets import GSheetsConnection

st.set_page_config(page_title="Plataforma TaxLease", layout="wide", page_icon="🚀")

# Título principal
st.title("🏛️ Plataforma TaxLease v2.0")
st.markdown("---")

# Menú lateral para navegar entre perfiles
menu = st.sidebar.radio("Seleccione su perfil:", ["📊 Calculadora Fiscal", "💰 Panel Inversores", "🏢 Área Asesorías"])

if menu == "📊 Calculadora Fiscal":
    st.header("Calculadora de Rentabilidad")
    st.info("Aquí realizaremos los cálculos de Tax Lease para sus clientes.")
    # Tu lógica de cálculo irá aquí

elif menu == "💰 Panel Inversores":
    st.header("Oportunidades para Inversores")
    st.write("Listado de operaciones disponibles para participar.")

elif menu == "🏢 Área Asesorías":
    st.header("Gestión de Clientes")
    st.write("Panel exclusivo para despachos y asesorías fiscalistas.")
