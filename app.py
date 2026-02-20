import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest Platform", layout="wide")

st.title("🏛️ Dertogest: Gestión de Incentivos Fiscales")

# 2. CONEXIÓN A GOOGLE SHEETS (Manejo de errores profesional)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("Error de configuración en los 'Secrets' de Streamlit.")

# 3. MENÚ LATERAL
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN 1: CALCULADORA FISCAL ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión (Art. 39.7 LIS / 68.2 LIRPF)")
    
    with st.expander("Datos del Inversor", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre / Empresa", "Cliente S.L.")
            cuota_is = st.number_input("Cuota Íntegra (€)", value=100000, step=1000)
        with col2:
            facturacion = st.number_input("Facturación Anual (€)", value=25000000)
            meses = st.slider("Meses para recuperación", 1, 12, 6)

    # Lógica de Límites Fiscales España
    limite_pct = 0.15 if facturacion > 20000000 else 0.50
    capacidad_deduccion = cuota_is * limite_pct
    inv_optima = capacidad_deduccion / 1.20

    st.success(f"🎯 Inversión Óptima Sugerida: **{inv_optima:,.2f} €**")

    st.divider()
    inv_real = st.number_input("Inversión Real Propuesta (€)", value=float(inv_optima))
    
    # Cálculos Financieros DERTOGEST
    ahorro_neto = inv_real * 0.20
    rent_mensual = 20.0 / meses
    tae = rent_mensual * 12
    
    # Honorarios (Base Imponible + IVA)
    setup_fee = 300.0 * 1.21
    success_fee_base = inv_real * 0.04
    success_fee_total = success_fee_base * 1.21

    c1, c2, c3 = st.columns(3)
    c1.metric("Beneficio Neto", f"{ahorro_neto:,.2f} €", "20% Fijo")
    c2.metric("Rentabilidad Mensual", f"{rent_mensual:.2f} %")
    c3.metric("TAE Anualizada", f"{tae:.2f} %")

    if st.button("📄 Generar Informe Ejecutivo"):
        informe = f"""
        INFORME DERTOGEST - {nombre}
        ------------------------------------------
        Capacidad Fiscal: {capacidad_deduccion:,.2f} €
        Inversión Propuesta: {inv_real:,.2f} €
        Ahorro Neto: {ahorro_neto:,.2f} €
        
        HONORARIOS DE GESTIÓN (IVA INCLUIDO):
        - Apertura (300€ + IVA): {setup_fee:,.2f} €
        - Éxito (4% + IVA): {success_fee_total:,.2f} €
        ------------------------------------------
        Nota: Operación garantizada bajo el Art. 39.7 LIS.
        """
        st.text_area("Vista previa", informe, height=200)

# --- SECCIÓN 2: PARTNERS ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Colaboradores")
    try:
        df_p = conn.read(worksheet="PARTNERS")
        st.dataframe(df_p)
        st.info("Reparto: 50/50 sobre Base Imponible según contrato de JV.")
    except:
        st.warning("No se pudo leer la pestaña 'PARTNERS'.")

# --- SECCIÓN 3: INVERSORES ---
elif choice == "💰 Inversores":
    st.header("Base de Datos de Inversores")
    try:
        df_i = conn.read(worksheet="INVERSORES")
        st.dataframe(df_i)
    except:
        st.warning("No se pudo leer la pestaña 'INVERSORES'.")
