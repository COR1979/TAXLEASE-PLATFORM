import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Plataforma TaxLease", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimizador Fiscal TaxLease v2.0")

# --- CALCULADORA PERFECTA ---
facturacion = st.number_input("Facturación Anual (€)", min_value=0, value=5000000)
cuota_is = st.number_input("Cuota Íntegra IS (€)", min_value=0, value=36000)

limite_pct = 0.15 if facturacion > 20000000 else 0.50
inv_optima = (cuota_is * limite_pct) / 1.20
st.metric("Inversión Óptima Sugerida", f"{inv_optima:,.2f} €")

# --- REGISTRO FORZADO ---
if st.button("🚀 GUARDAR EN EXCEL"):
    try:
        # Intentamos leer la primera pestaña disponible (la que moviste)
        df_actual = conn.read(ttl=0) 
        
        nueva_fila = pd.DataFrame([{
            "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%H%M%S')}",
            "Inversor": "TEST FINAL",
            "Inversión": inv_optima,
            "Ahorro": inv_optima * 0.20
        }])
        
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(data=df_final)
        
        st.balloons()
        st.success("✅ ¡CONEXIÓN ESTABLECIDA! Los datos ya están en tu primera pestaña.")
        
    except Exception as e:
        st.error(f"Error persistente: {e}")
        st.info("Si el error sigue siendo 401, por favor, borra al robot del Excel y vuelve a invitarlo como Editor.")
