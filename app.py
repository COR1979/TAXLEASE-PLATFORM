import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Optimización", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimización de Inversión TaxLease")

# --- PANEL DE CÁLCULO ÓPTIMO ---
st.header("🔍 Buscador de Inversión Óptima")
col1, col2 = st.columns(2)

with col1:
    cuota_is = st.number_input("Cuota Íntegra IS del Cliente (€)", min_value=0, step=1000, value=36000)
    facturacion = st.number_input("Facturación Empresa (€)", min_value=0, step=100000)

# Lógica de optimización automática
limite_base = 0.25
# Si la inversión supera el 10% de la cuota, el límite de aplicación sube al 50%
inv_optima_50 = (cuota_is * 0.50) / 0.25 
inv_optima_25 = (cuota_is * 0.25) / 0.25

with col2:
    st.subheader("Capacidad de Absorción")
    st.write(f"🔹 **Escenario Estándar (25%):** Hasta {inv_optima_25:,.2f} € de inversión.")
    st.write(f"🚀 **Escenario Intensivo (50%):** Hasta {inv_optima_50:,.2f} € de inversión.")
    st.caption("El escenario 50% se activa si la inversión supera el 10% de la cuota íntegra.")

st.divider()

# --- FORMULARIO DE REGISTRO (Solo cuando ya sabes cuánto invertir) ---
st.header("📝 Registro del Expediente Final")
with st.form("registro_final"):
    c1, c2 = st.columns(2)
    with c1:
        nombre_inv = st.text_input("Nombre del Inversor", value="CRISTOBAL OPROZCO")
        monto_final = st.number_input("Inversión Acordada (€)", min_value=0, step=500)
    with c2:
        nif_inv = st.text_input("NIF Inversor")
        nif_partner = st.text_input("NIF Partner", value="B61009858")
    
    submit = st.form_submit_button("Confirmar y Enviar a EXPEDIENTES")

if submit:
    # Cálculo final con el 5% de seguridad
    ahorro_real = (monto_final * 0.25) * 0.95
    
    nueva_fila = pd.DataFrame([{
        "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%d%m%y%H%M')}",
        "Nombre Inversor": nombre_inv,
        "Importe Inversión": monto_final,
        "Ahorro Neto": ahorro_real,
        "Estado": "Validado",
        "NIF Partner": nif_partner
    }])

    try:
        df_actual = conn.read(worksheet="EXPEDIENTES")
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="EXPEDIENTES", data=df_final)
        st.balloons()
        st.success(f"Operación registrada. Ahorro generado: {ahorro_real:,.2f} €")
    except Exception as e:
        st.error(f"Error de conexión (401): Revisa los Secrets en Streamlit Cloud.")
