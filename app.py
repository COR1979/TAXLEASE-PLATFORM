import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Master", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimizador Fiscal TaxLease v2.0")

# --- ENTRADA DE DATOS ---
facturacion = st.number_input("Facturación Anual (€)", min_value=0, value=5000000)
cuota_is_inicial = st.number_input("Cuota Íntegra IS Inicial (€)", min_value=0, value=36000)

es_gran_empresa = facturacion > 20000000
limite_pct = 0.15 if es_gran_empresa else 0.50 

techo_deduccion = cuota_is_inicial * limite_pct
inv_optima = techo_deduccion / 1.20

st.metric("Inversión Óptima Sugerida", f"{inv_optima:,.2f} €")

if st.button("🚀 GUARDAR EN EXCEL"):
    nueva_fila = pd.DataFrame([{
        "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%H%M%S')}",
        "Nombre Inversor": "OPERACIÓN VALIDADA",
        "Importe Inversión": inv_optima,
        "Estado": "Validado"
    }])
    
    try:
        df_actual = conn.read(worksheet="EXPEDIENTES", ttl=0)
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="EXPEDIENTES", data=df_final)
        st.balloons()
        st.success("🎉 ¡CONECTADO! Los datos están en tu Excel.")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
