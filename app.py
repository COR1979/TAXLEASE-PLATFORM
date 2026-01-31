import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Optimización", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimizador Fiscal TaxLease")

# --- ANÁLISIS DE CAPACIDAD ---
st.header("🔍 1. Análisis de Capacidad (Límites LIS)")
cuota_is = st.number_input("Cuota Íntegra IS del Cliente (€)", min_value=0, value=36000, step=1000)

# El AHORRO (Deducción) máximo permitido por ley
max_ahorro_25 = cuota_is * 0.25
max_ahorro_50 = cuota_is * 0.50

# La INVERSIÓN necesaria para generar ese ahorro (asumiendo que el ahorro es el 25% de la inversión)
# Nota: En Tax Lease, el cliente pone X y recibe X + margen. 
inv_necesaria_25 = max_ahorro_25 / 0.25
inv_necesaria_50 = max_ahorro_50 / 0.25

col1, col2 = st.columns(2)
with col1:
    st.subheader("Escenario Estándar (25%)")
    st.write(f"Deducción máxima: **{max_ahorro_25:,.2f} €**")
    st.info(f"Inversión para agotar límite: **{inv_necesaria_25:,.2f} €**")

with col2:
    st.subheader("Escenario Intensivo (50%)")
    st.write(f"Deducción máxima: **{max_ahorro_50:,.2f} €**")
    st.info(f"Inversión para agotar límite: **{inv_necesaria_50:,.2f} €**")

st.warning("⚠️ Nota: La inversión puede ser superior a la cuota porque lo que se limita es la DEDUCCIÓN aplicada, no el desembolso. No obstante, financieramente el cliente solo invertirá si el ahorro neto es atractivo.")

# --- REGISTRO ---
st.divider()
st.header("📝 2. Registro del Expediente")
with st.form("registro"):
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("Nombre Inversor")
        monto_inv = st.number_input("Inversión Final Acordada (€)", min_value=0)
    with c2:
        nif = st.text_input("NIF")
        partner = st.text_input("NIF Partner")
    
    btn = st.form_submit_button("Guardar en EXPEDIENTES")

if btn:
    # Ahorro para el cliente (25% de lo invertido con margen de seguridad)
    ahorro_generado = (monto_inv * 0.25) * 0.95
    
    if ahorro_generado > max_ahorro_50:
        st.error(f"¡Atención! El ahorro generado ({ahorro_generado:,.2f}€) supera el límite máximo legal del 50% de la cuota.")
    else:
        # Lógica de guardado...
        st.success("Operación validada dentro de los límites.")
