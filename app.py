import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Optimización", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimizador de Inversión TaxLease")

# --- ANÁLISIS DE CAPACIDAD ---
st.header("🔍 1. Perfil Fiscal y Cálculo de Óptimos")
col1, col2 = st.columns(2)

with col1:
    facturacion = st.number_input("Facturación Anual de la Empresa (€)", min_value=0, value=5000000, step=100000)
    cuota_is = st.number_input("Cuota Íntegra IS del Cliente (€)", min_value=0, value=36000, step=1000)
    
    # Determinación de tipo de empresa por facturación
    es_gran_empresa = facturacion > 20000000
    tipo_txt = "🏢 Gran Empresa (>20M€)" if es_gran_empresa else "🏭 Pyme / Resto"
    st.info(f"Tipo de Entidad: **{tipo_txt}**")

# Lógica de límites
techo_25 = cuota_is * 0.25
techo_50 = cuota_is * 0.50

# Inversión necesaria (Inv + 20% = Techo)
inv_optima_25 = techo_25 / 1.20
inv_optima_50 = techo_50 / 1.20

with col2:
    st.subheader("Capacidad de Inversión (Rentabilidad 20%)")
    st.write(f"✅ **Límite 25%:** Inversión de **{inv_optima_25:,.2f} €**")
    st.write(f"🚀 **Límite 50%:** Inversión de **{inv_optima_50:,.2f} €**")
    st.caption("Fórmula: Inversión + 20% rentabilidad = Deducción aplicada en Cuota.")

st.divider()

# --- REGISTRO ---
st.header("📝 2. Formalización del Expediente")
with st.form("registro_exp"):
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("Nombre Inversor", value="CRISTOBAL OPROZCO")
        monto_final = st.number_input("Desembolso de Inversión Final (€)", min_value=0.0, step=500.0)
    with c2:
        nif = st.text_input("NIF Inversor")
        partner = st.text_input("NIF Partner (B61009858)")
    
    submit = st.form_submit_button("Confirmar y Guardar en Excel")

if submit:
    # Cálculo de la rentabilidad real
    deduccion_total = monto_final * 1.20
    ahorro_neto = deduccion_total - monto_final
    
    if deduccion_total > techo_50:
        st.error(f"❌ La deducción total ({deduccion_total:,.2f}€) supera el límite máximo del 50% de la cuota.")
    else:
        # Preparación de datos para EXPEDIENTES
        nueva_fila = pd.DataFrame([{
            "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%d%m%y%H%M')}",
            "Nombre Inversor": nombre,
            "NIF Inversor": nif,
            "Importe Inversión": monto_final,
            "Ahorro Neto": ahorro_neto,
            "Facturación": facturacion,
            "Cuota IS": cuota_is,
            "Estado": "Validado",
            "NIF Partner": partner
        }])
        
        try:
            df_actual = conn.read(worksheet="EXPEDIENTES")
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="EXPEDIENTES", data=df_final)
            st.balloons()
            st.success(f"¡Sincronizado! Ahorro fiscal generado: {ahorro_neto:,.2f} €")
        except Exception as e:
            st.error("Error 401. Por favor, verifica que el robot tenga permiso de EDITOR en el Excel.")
