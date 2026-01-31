import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Master v2.0", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimizador Fiscal TaxLease v2.0")

# --- 1. ENTRADA DE DATOS ---
st.header("📊 Perfil del Cliente")
col_in1, col_in2 = st.columns(2)

with col_in1:
    facturacion = st.number_input("Facturación Anual (€)", min_value=0, value=5000000, step=100000)
    cuota_is_inicial = st.number_input("Cuota Íntegra IS Inicial (€)", min_value=0, value=36000, step=1000)

# Lógica de límites (Gran Empresa vs Pyme)
es_gran_empresa = facturacion > 20000000

if es_gran_empresa:
    escenarios = [{"nombre": "Límite Gran Empresa", "pct": 0.15}]
    st.warning("🏢 Gran Empresa detectada: Límite de deducción al 15%.")
else:
    escenarios = [
        {"nombre": "Escenario Estándar", "pct": 0.25},
        {"nombre": "Escenario Intensivo", "pct": 0.50}
    ]
    st.info("🏭 Pyme detectada: Mostrando escenarios al 25% y 50%.")

st.divider()

# --- 2. CÁLCULO DE OPTIMIZACIÓN ---
st.header("🔍 Inversión Óptima y Rentabilidad (20%)")
cols = st.columns(len(escenarios))

for i, esc in enumerate(escenarios):
    with cols[i]:
        techo_deduccion = cuota_is_inicial * esc["pct"]
        # Fórmula validada: Inv = Techo / 1.20
        inv_optima = techo_deduccion / 1.20
        beneficio = inv_optima * 0.20
        
        st.subheader(f"{esc['nombre']} ({esc['pct']*100:.0f}%)")
        st.write(f"Deducción Máxima: **{techo_deduccion:,.2f} €**")
        st.success(f"Inversión a realizar: **{inv_optima:,.2f} €**")
        st.metric("Beneficio Cliente (20%)", f"{beneficio:,.2f} €")

st.divider()

# --- 3. IMPACTO FINAL Y REGISTRO ---
st.header("📉 Simulación Final e Impacto en Cuota")
monto_final = st.number_input("Confirmar Inversión Final (€)", min_value=0.0, value=inv_optima, step=500.0)

deduccion_total = monto_final * 1.20
cuota_final = cuota_is_inicial - deduccion_total
ahorro_neto = deduccion_total - monto_final

c1, c2, c3 = st.columns(3)
c1.metric("Ahorro Neto Real", f"{ahorro_neto:,.2f} €")
c2.metric("Cuota IS Final", f"{cuota_final:,.2f} €", delta=f"-{deduccion_total:,.2f} €")
c3.metric("Rentabilidad s/ Inversión", "20.0%")

if st.button("🚀 GUARDAR EN EXPEDIENTES"):
    nueva_fila = pd.DataFrame([{
        "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%d%m%y%H%M')}",
        "Nombre Inversor": "OPERACIÓN VALIDADA",
        "Importe Inversión": monto_final,
        "Ahorro Neto": ahorro_neto,
        "Estado": "Pendiente",
        "Facturación": facturacion
    }])
    
    try:
        # Intentamos escribir en la pestaña EXPEDIENTES
        df_actual = conn.read(worksheet="EXPEDIENTES", ttl=0)
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="EXPEDIENTES", data=df_final)
        st.balloons()
        st.success("🎉 ¡Sincronizado con éxito en tu Excel!")
    except Exception as e:
        st.error(f"Error de conexión: {e}")
