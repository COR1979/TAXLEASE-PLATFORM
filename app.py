import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Master", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimizador Fiscal TaxLease")

# --- TEST DE CONEXIÓN DINÁMICO ---
if st.sidebar.button("🔍 Forzar Reconocimiento de Pestañas"):
    try:
        # Intentamos leer la pestaña directamente por su nombre
        df_test = conn.read(worksheet="EXPEDIENTES", ttl=0)
        st.sidebar.success("✅ ¡Localizada! He encontrado 'EXPEDIENTES' en la posición 3.")
    except Exception as e:
        st.sidebar.error("❌ No la encuentro por nombre.")
        st.sidebar.info("Consejo: Asegúrate de que no haya un espacio después de la S: 'EXPEDIENTES '")

# --- LÓGICA DE CÁLCULO (La que ya definimos como perfecta) ---
facturacion = st.number_input("Facturación Anual (€)", min_value=0, value=5000000)
cuota_is = st.number_input("Cuota Íntegra IS (€)", min_value=0, value=36000)

es_gran_empresa = facturacion > 20000000
# Tu regla: 15% para Grandes Empresas, 50% para Pymes (Escenario máximo)
limite_pct = 0.15 if es_gran_empresa else 0.50 

techo_deduccion = cuota_is * limite_pct
inv_optima = techo_deduccion / 1.20

st.metric("Inversión Óptima Sugerida", f"{inv_optima:,.2f} €")

# --- REGISTRO ---
if st.button("🚀 GRABAR EN EXPEDIENTES"):
    nueva_fila = pd.DataFrame([{
        "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%H%M%S')}",
        "Nombre Inversor": "PRUEBA POSICION 3",
        "Importe Inversión": inv_optima,
        "Estado": "Validado",
        "NIF Partner": "B61009858"
    }])
    
    try:
        # TTL=0 obliga a la App a no usar memoria vieja y mirar el Excel real
        df_actual = conn.read(worksheet="EXPEDIENTES", ttl=0)
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="EXPEDIENTES", data=df_final)
        st.balloons()
        st.success("🎉 ¡LOGRADO! Datos grabados en la tercera pestaña.")
    except Exception as e:
        st.error(f"Fallo crítico: {e}")
