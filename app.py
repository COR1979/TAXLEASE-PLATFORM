import streamlit as st

# 1. Configuración básica
st.set_page_config(page_title="TaxLease Platform", layout="wide")

st.title("🏛️ TaxLease Platform-Manager")

# 2. Menú lateral
menu = ["📊 Calculadora Fiscal", "🤝 Partners"]
choice = st.sidebar.selectbox("Ir a:", menu)

# --- SECCIÓN 1: CALCULADORA (Funciona siempre, no depende del Excel) ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Calculadora de Impacto Fiscal")
    
    col1, col2 = st.columns(2)
    with col1:
        cuota = st.number_input("Cuota Íntegra IS Inicial (€)", value=100000, step=5000)
        facturacion = st.number_input("Facturación Anual (€)", value=25000000, step=1000000)
    
    # Lógica de límites fiscales
    limite = 0.15 if facturacion > 20000000 else 0.50
    capacidad = cuota * limite
    inv_optima = capacidad / 1.20

    with col2:
        st.metric("Límite Fiscal", f"{limite*100:.0f}%")
        st.success(f"Inversión Óptima Sugerida: {inv_optima:,.2f} €")

    st.divider()
    
    st.subheader("Simulador de Propuesta Real")
    propuesta = st.number_input("Importe de la Inversión Real (€)", value=float(inv_optima))
    
    # Cálculos basados en la propuesta
    deduccion = propuesta * 1.20
    ahorro = propuesta * 0.20
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Deducción (120%)", f"{deduccion:,.2f} €")
    c2.metric("Ahorro Neto (20%)", f"{ahorro:,.2f} €")
    c3.metric("Cuota Final IS", f"{cuota - deduccion:,.2f} €", delta=f"-{deduccion:,.2f} €")

# --- SECCIÓN 2: PARTNERS (Conexión con Google Sheets) ---
elif choice == "🤝 Partners":
    st.header("Base de Datos de Partners")
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="PARTNERS", ttl=0)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error(f"⚠️ Error al conectar con el Excel: {e}")
        st.info("Revisa si tus 'Secrets' en Streamlit Cloud siguen configurados correctamente.")
