import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Master", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Plataforma TaxLease: Optimización y Registro")

# --- 1. ENTRADA DE DATOS FISCALES ---
st.header("📊 Análisis de la Operación")
col_in1, col_in2 = st.columns(2)

with col_in1:
    facturacion = st.number_input("Facturación Anual de la Empresa (€)", min_value=0, value=25000000, step=100000)
    cuota_is_inicial = st.number_input("Cuota Íntegra IS Inicial (€)", min_value=0, value=100000, step=1000)

# --- 2. LÓGICA DE LÍMITES (GRAN EMPRESA VS PYME) ---
es_gran_empresa = facturacion > 20000000

if es_gran_empresa:
    limite_pct = 0.15
    tipo_entidad = "🏢 Gran Empresa (>20M€)"
    color_msg = "warning"
else:
    # Para Pymes, si la inversión es alta se suele llegar al 50%, 
    # pero aquí fijamos el máximo legal aplicable según tu criterio.
    limite_pct = 0.50 
    tipo_entidad = "🏭 Pyme / Resto"
    color_msg = "info"

st.toast(f"Detectado: {tipo_entidad}")

# Deducción Máxima permitida sobre la cuota
max_deduccion_posible = cuota_is_inicial * limite_pct

# Inversión Óptima para agotar ese límite (Inversión * 1.20 = Deducción)
inv_optima = max_deduccion_posible / 1.20
rentabilidad_esperada = inv_optima * 0.20

with col_in2:
    st.subheader("Capacidad Máxima de Absorción")
    st.write(f"**Límite Legal Aplicable:** {limite_pct*100:.0f}% de la Cuota")
    st.write(f"💰 **Deducción Máxima:** {max_deduccion_posible:,.2f} €")
    st.success(f"🎯 **Inversión Óptima:** {inv_optima:,.2f} €")

st.divider()

# --- 3. IMPACTO EN LA CUOTA (EL ANTES Y EL DESPUÉS) ---
st.header("📉 Impacto Fiscal")
monto_final = st.slider("Ajustar Inversión Final (€)", 0.0, inv_optima * 1.2, inv_optima)

deduccion_generada = monto_final * 1.20
rentabilidad_cliente = monto_final * 0.20
cuota_final_pagar = cuota_is_inicial - deduccion_generada

c1, c2, c3 = st.columns(3)
c1.metric("Inversión Realizada", f"{monto_final:,.2f} €")
c2.metric("Rentabilidad (20%)", f"{rentabilidad_cliente:,.2f} €", delta="Beneficio Directo")
c3.metric("Cuota Final IS", f"{cuota_final_pagar:,.2f} €", delta=f"-{deduccion_generada:,.2f} €", delta_color="normal")

st.divider()

# --- 4. REGISTRO EN EXPEDIENTES ---
st.header("📝 Registro del Expediente")
with st.form("registro_final"):
    f1, f2 = st.columns(2)
    with f1:
        nombre = st.text_input("Nombre Inversor", value="CRISTOBAL OPROZCO")
        nif = st.text_input("NIF Inversor")
    with f2:
        partner = st.text_input("NIF Partner", value="B61009858")
        submit = st.form_submit_button("Confirmar y Enviar a EXPEDIENTES")

if submit:
    nueva_fila = pd.DataFrame([{
        "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%d%m%y%H%M')}",
        "Nombre Inversor": nombre,
        "Importe Inversión": monto_final,
        "Ahorro Neto": rentabilidad_cliente,
        "Cuota IS Final": cuota_final_pagar,
        "Estado": "Validado",
        "NIF Partner": partner
    }])
    
    try:
        df_actual = conn.read(worksheet="EXPEDIENTES")
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="EXPEDIENTES", data=df_final)
        st.balloons()
        st.success("✅ ¡Expediente registrado con éxito!")
    except Exception as e:
        st.error("Error 401: Revisa que el robot sea EDITOR en el Excel.")
