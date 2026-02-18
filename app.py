import streamlit as st
import pandas as pd

# Configuración inicial
st.set_page_config(page_title="TaxLease Platform", layout="wide")

st.title("🏛️ TaxLease Platform-Manager")

# Menú lateral
choice = st.sidebar.selectbox("Ir a:", ["📊 Calculadora Fiscal", "🤝 Partners"])

if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Calculadora de Impacto Fiscal")
    col1, col2 = st.columns(2)
    with col1:
        cuota = st.number_input("Cuota Íntegra IS (€)", value=100000)
        factu = st.number_input("Facturación Anual (€)", value=25000000)
    
    limite = 0.15 if factu > 20000000 else 0.50
    inv_optima = (cuota * limite) / 1.20

    with col2:
        st.metric("Límite Fiscal", f"{limite*100:.0f}%")
        st.success(f"Inversión Óptima Sugerida: {inv_optima:,.2f} €")
    
    st.divider()
    monto = st.number_input("Inversión Real Propuesta (€)", value=float(inv_optima))
    st.info(f"Ahorro Neto (20%): {monto * 0.20:,.2f} € | Deducción: {monto * 1.20:,.2f} €")

elif choice == "🤝 Partners":
    st.header("Consulta de Partners")
    try:
        # Intentamos la conexión
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="PARTNERS", ttl=0)
        st.dataframe(df)
    except Exception as e:
        st.error("No se pudo cargar el Excel, pero la calculadora sigue disponible.")
        st.warning("Verifica que en 'Secrets' de Streamlit Cloud tengas configurada la conexión.")
