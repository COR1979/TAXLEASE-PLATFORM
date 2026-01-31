import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Optimización", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimizador de Inversión TaxLease")

# --- ANÁLISIS DE CAPACIDAD ---
st.header("🔍 1. Cálculo de Inversión Óptima (Rentabilidad 20%)")
cuota_is = st.number_input("Cuota Íntegra IS del Cliente (€)", min_value=0, value=36000, step=1000)

# 1. Definimos los techos legales (Lo máximo que puede deducir)
techo_25 = cuota_is * 0.25
techo_50 = cuota_is * 0.50

# 2. Calculamos la inversión necesaria para alcanzar esos techos con un 20% de margen
# Formula: Inv * 1.20 = Techo  =>  Inv = Techo / 1.20
inv_optima_25 = techo_25 / 1.20
inv_optima_50 = techo_50 / 1.20

col1, col2 = st.columns(2)
with col1:
    st.subheader("Escenario Estándar (25%)")
    st.write(f"Deducción Máxima: **{techo_25:,.2f} €**")
    st.success(f"Inversión a realizar: **{inv_optima_25:,.2f} €**")
    st.caption(f"Detalle: {inv_optima_25:,.2f} + 20% rentabilidad = {techo_25:,.2f}")

with col2:
    st.subheader("Escenario Intensivo (50%)")
    st.write(f"Deducción Máxima: **{techo_50:,.2f} €**")
    st.success(f"Inversión a realizar: **{inv_optima_50:,.2f} €**")
    st.caption(f"Detalle: {inv_optima_50:,.2f} + 20% rentabilidad = {techo_50:,.2f}")

st.divider()

# --- REGISTRO ---
st.header("📝 2. Registro del Expediente")
with st.form("registro"):
    c1, c2 = st.columns(2)
    with c1:
        nombre = st.text_input("Nombre Inversor", value="CRISTOBAL OPROZCO")
        monto_inv = st.number_input("Inversión Final Acordada (€)", min_value=0.0, step=500.0)
    with c2:
        nif = st.text_input("NIF")
        partner = st.text_input("NIF Partner", value="B61009858")
    
    btn = st.form_submit_button("Guardar en EXPEDIENTES")

if btn:
    # El beneficio para el inversor es el 20% de su inversión
    beneficio = monto_inv * 0.20
    deduccion_total = monto_inv + beneficio
    
    # Verificación de seguridad
    if deduccion_total > techo_50:
        st.error(f"⚠️ Error: La deducción total ({deduccion_total:,.2f}€) supera el límite legal del 50% de la cuota.")
    else:
        nueva_fila = pd.DataFrame([{
            "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%d%m%y%H%M')}",
            "Nombre Inversor": nombre,
            "Importe Inversión": monto_inv,
            "Ahorro Neto": beneficio,
            "Estado": "Validado",
            "NIF Partner": partner
        }])
        
        try:
            df_actual = conn.read(worksheet="EXPEDIENTES")
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="EXPEDIENTES", data=df_final)
            st.balloons()
            st.success("Operación registrada correctamente.")
        except Exception as e:
            st.error(f"Error 401: Revisa los permisos de 'Editor' del robot en el Excel.")
