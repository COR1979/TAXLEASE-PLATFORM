import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Dertogest Platform", layout="wide")
st.title("🏛️ Dertogest: Gestión de Incentivos Fiscales")

# 2. CONEXIÓN
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de configuración: {e}")

# 3. MENÚ
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores"]
choice = st.sidebar.selectbox("Selecciona sección", menu)

# --- CALCULADORA ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión Tax Lease")
    col1, col2 = st.columns(2)
    with col1:
        factu = st.number_input("Facturación Anual (€)", value=11200000)
        cuota = st.number_input("Cuota Íntegra IS Inicial (€)", value=102000)
        meses = st.slider("Meses recuperación", 1, 12, 6)
    
    limite = 0.15 if factu > 20000000 else 0.50
    inv_opt = (cuota * limite) / 1.20
    st.metric("Inversión Óptima Sugerida", f"{inv_opt:,.2f} €")

# --- PARTNERS (JV) ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners")
    try:
        df = conn.read(worksheet="PARTNERS")
        
        # --- LÍNEA DE DIAGNÓSTICO (Solo si hay dudas) ---
        # st.write("Columnas detectadas:", list(df.columns)) 
        
        st.dataframe(df)
        
        st.subheader("📝 Generar Contrato JV")
        
        # Nombres exactos de las columnas (AHORA CON EL PARÉNTESIS CERRADO)
        col_id = "NIF (ID único)"
        col_nombre = "Nombre Partner (Razón Social)" 
        col_domicilio = "Domicilio Social"
        
        nif_sel = st.selectbox("Selecciona Partner por NIF", df[col_id].tolist())
        datos = df[df[col_id] == nif_sel].iloc[0]

        if st.button("Generar Texto Contrato"):
            texto = f"""CONTRATO JV - DERTOGEST
--------------------------------------------------
PARTNER: {datos[col_nombre]}
NIF: {datos[col_id]}
DOMICILIO: {datos[col_domicilio]}

REPARTO: 50% sobre Base Imponible (+ IVA).
--------------------------------------------------"""
            st.text_area("Copia el contrato:", texto, height=250)
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Si el error es 'KeyError', comprueba que los nombres de las columnas en el Excel no tengan espacios extra al final.")

# --- INVERSORES ---
elif choice == "💰 Inversores":
    st.header("Gestión de Inversores")
    try:
        df_i = conn.read(worksheet="INVERSORES")
        st.dataframe(df_i)
        nif_i = st.selectbox("Selecciona Inversor (NIF)", df_i.iloc[:, 0].tolist())
        if st.button("Generar Texto Encargo"):
            st.success(f"Contrato listo para el NIF: {nif_i}")
    except Exception as e:
        st.error(f"Error: {e}")
