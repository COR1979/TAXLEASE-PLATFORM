import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Master", layout="wide")

# Inicializamos la conexión
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Plataforma TaxLease v2.0")

# --- BLOQUE DE SEGURIDAD PARA EL ERROR 401 ---
try:
    # Intentamos una lectura limpia sin caché para forzar la validación
    df_test = conn.read(ttl=0) 
    st.sidebar.success("✅ Conexión con Google Sheets establecida.")
except Exception as e:
    st.sidebar.error(f"❌ Error 401 Persistente")
    st.sidebar.write("1. Ve a Streamlit Cloud > Settings > Secrets.")
    st.sidebar.write("2. Asegúrate de que el JSON no tenga saltos de línea extra.")
    st.stop() # Detenemos la app si no hay conexión para no dar cálculos falsos

# --- CÁLCULOS PERFECTOS (Los que ya validamos) ---
facturacion = st.number_input("Facturación Anual (€)", min_value=0, value=5000000)
cuota_is = st.number_input("Cuota Íntegra IS (€)", min_value=0, value=36000)

es_gran_empresa = facturacion > 20000000
limite_pct = 0.15 if es_gran_empresa else 0.50
techo_deduccion = cuota_is * limite_pct
inv_optima = techo_deduccion / 1.20

st.metric("Inversión Óptima Sugerida", f"{inv_optima:,.2f} €")

# --- REGISTRO EN LA TERCERA PESTAÑA ---
st.subheader("📝 Registro en EXPEDIENTES")
if st.button("🚀 GUARDAR OPERACIÓN"):
    nueva_fila = pd.DataFrame([{
        "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%H%M%S')}",
        "Nombre Inversor": "OPERACIÓN VALIDADA",
        "Importe Inversión": inv_optima,
        "Estado": "Validado"
    }])
    
    try:
        # Usamos el nombre exacto de tu tercera pestaña
        df_actual = conn.read(worksheet="EXPEDIENTES", ttl=0)
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="EXPEDIENTES", data=df_final)
        st.balloons()
        st.success("🎉 ¡Guardado en la pestaña EXPEDIENTES!")
    except Exception as e:
        st.error(f"Error al escribir: {e}")
        st.info("Nota: Si dice que no encuentra la pestaña, cámbiale el nombre en el Excel a 'EXP' (más corto) y prueba de nuevo.")
