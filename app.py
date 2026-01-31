import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Optimización", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimizador Fiscal TaxLease")

# --- SECCIÓN 1: CÁLCULO DE CAPACIDAD ---
st.header("🔍 1. Análisis de Capacidad de Absorción")
col1, col2 = st.columns(2)

with col1:
    cuota_is = st.number_input("Cuota Íntegra IS del Cliente (€)", min_value=0, value=36000, step=1000)
    st.info("La ley permite deducir el 25% de la cuota, o el 50% si la inversión supera el 10% de la misma.")

# Cálculo de límites sobre cuota
limite_25_cuota = cuota_is * 0.25
limite_50_cuota = cuota_is * 0.50

# Inversión necesaria para agotar esos límites (Deducción es el 25% de la inversión)
inv_necesaria_25 = limite_25_cuota / 0.25
inv_necesaria_50 = limite_50_cuota / 0.25

with col2:
    st.subheader("Resultados de Capacidad")
    st.write(f"✅ **Límite Estándar (25%):** Puede absorber hasta **{limite_25_cuota:,.2f} €** de deducción.")
    st.write(f"👉 Inversión ideal: **{inv_necesaria_25:,.2f} €**")
    st.divider()
    st.write(f"🚀 **Límite Incrementado (50%):** Puede absorber hasta **{limite_50_cuota:,.2f} €** de deducción.")
    st.write(f"👉 Inversión ideal: **{inv_necesaria_50:,.2f} €**")

st.divider()

# --- SECCIÓN 2: REGISTRO DEL EXPEDIENTE ---
st.header("📝 2. Registro de la Operación")
with st.form("registro_expediente"):
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("Nombre del Inversor", value="CRISTOBAL OPROZCO")
        monto_acordado = st.number_input("Inversión Final Acordada (€)", min_value=0, step=1000)
    with c2:
        nif = st.text_input("NIF Inversor")
        partner = st.text_input("NIF Partner", value="B61009858")
    
    btn = st.form_submit_button("Sincronizar con Excel")

if btn:
    # Ahorro neto para el inversor (Aplicando el 5% de margen de seguridad)
    ahorro_neto = (monto_acordado * 0.25) * 0.95
    
    fila = pd.DataFrame([{
        "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%d%m%y%H%M')}",
        "Nombre Inversor": nombre,
        "NIF Inversor": nif,
        "Importe Inversión": monto_acordado,
        "Ahorro Neto": ahorro_neto,
        "Estado": "Simulación",
        "NIF Partner": partner
    }])

    try:
        df_actual = conn.read(worksheet="EXPEDIENTES")
        df_final = pd.concat([df_actual, fila], ignore_index=True)
        conn.update(worksheet="EXPEDIENTES", data=df_final)
        st.balloons()
        st.success(f"Operación guardada. Ahorro para el cliente: {ahorro_neto:,.2f} €")
    except Exception as e:
        st.error(f"Error 401: No hay permiso de escritura. Revisa los Secrets y que el robot sea 'Editor' en el Excel.")
