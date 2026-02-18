import streamlit as st
import pandas as pd
from datetime import datetime

# Intentamos importar las librerías de Google, si fallan, la App avisará
try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    GOOGLE_LIBS_READY = True
except ImportError:
    GOOGLE_LIBS_READY = False

st.set_page_config(page_title="TaxLease Platform v4.0", layout="wide")

st.title("🏛️ TaxLease Platform-Manager")

# --- MENÚ LATERAL ---
menu = ["📊 Calculadora Fiscal", "🤝 Partners", "💰 Inversores"]
choice = st.sidebar.selectbox("Menú de Gestión", menu)

# ==========================================
# SECCIÓN: CALCULADORA FISCAL
# ==========================================
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Calculadora de Impacto Fiscal")
    
    col1, col2 = st.columns(2)
    with col1:
        cuota_is = st.number_input("Cuota Íntegra IS Inicial (€)", value=100000)
        facturacion = st.number_input("Facturación Anual (€)", value=25000000)
    
    # Lógica de límites
    limite_pct = 0.15 if facturacion > 20000000 else 0.50
    capacidad_deduccion = cuota_is * limite_pct
    inv_optima = capacidad_deduccion / 1.20

    with col2:
        st.metric("Límite de Deducción", f"{limite_pct*100:.0f}%")
        st.success(f"🎯 Inversión Óptima Sugerida: {inv_optima:,.2f} €")

    st.divider()
    
    st.subheader("Simulador de Propuesta")
    inv_propuesta = st.number_input("Importe de la Inversión Real (€)", value=float(inv_optima))
    
    ahorro_neto = inv_propuesta * 0.20
    deduccion_total = inv_propuesta * 1.20
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Deducción Generada", f"{deduccion_total:,.2f} €")
    c2.metric("Ahorro Neto (20%)", f"{ahorro_neto:,.2f} €")
    c3.metric("Cuota Final IS", f"{cuota_is - deduccion_total:,.2f} €")

# ==========================================
# SECCIÓN: PARTNERS (SOLO LECTURA)
# ==========================================
elif choice == "🤝 Partners":
    st.header("Lista de Partners (desde Excel)")
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="PARTNERS", ttl=0)
        st.dataframe(df)
    except Exception as e:
        st.error(f"Error al conectar con Excel: {e}")

if not GOOGLE_LIBS_READY:
    st.warning("⚠️ Nota: Las librerías para generar contratos no están instaladas en requirements.txt.")
