import streamlit as st

# 1. Configuración de la página
st.set_page_config(page_title="TaxLease Platform v5.0", layout="wide")

st.title("🏛️ TaxLease Platform-Manager")

# 2. Menú lateral
menu = ["📊 Calculadora y Análisis", "🤝 Partners"]
choice = st.sidebar.selectbox("Selecciona sección:", menu)

# --- SECCIÓN 1: CALCULADORA ANALÍTICA ---
if choice == "📊 Calculadora y Análisis":
    st.header("🧮 Análisis de Inversión y Rentabilidad")
    
    # Bloque 1: Capacidad Fiscal (El Techo)
    with st.expander("1. Capacidad Fiscal del Cliente (Límites Legales)", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            cuota = st.number_input("Cuota Íntegra IS Inicial (€)", value=100000, step=5000)
            facturacion = st.number_input("Facturación Anual (€)", value=25000000, step=1000000)
        
        limite = 0.15 if facturacion > 20000000 else 0.50
        capacidad_max = cuota * limite
        inv_optima = capacidad_max / 1.20
        
        with c2:
            st.metric("Límite Fiscal Aplicable", f"{limite*100:.0f}%")
            st.success(f"Inversión Óptima Sugerida: {inv_optima:,.2f} €")

    st.divider()

    # Bloque 2: La Operación Real
    st.subheader("2. Contraste de la Operación Real")
    col_real1, col_real2 = st.columns(2)
    
    with col_real1:
        inv_real = st.number_input("Inversión Real Realizada (€)", value=float(inv_optima))
        meses = st.slider("Plazo de recuperación (Meses)", 1, 12, 6)
    
    with col_real2:
        diferencia = inv_optima - inv_real
        if diferencia > 0:
            st.warning(f"Diferencia: Faltan {diferencia:,.2f} € para agotar el cupo fiscal.")
        elif diferencia < 0:
            st.error(f"Exceso: Supera el límite legal en {abs(diferencia):,.2f} €.")
        else:
            st.info("La inversión coincide exactamente con el cupo máximo.")

    st.divider()

    # Bloque 3: Rendimiento Financiero
    st.subheader("3. Rendimiento y Rentabilidad Real")
    
    # Cálculos financieros
    ahorro_neto = inv_real * 0.20
    rent_mensual = 20.0 / meses
    tae_equivalente = rent_mensual * 12

    m1, m2, m3 = st.columns(3)
    m1.metric("Beneficio Neto", f"{ahorro_neto:,.2f} €", "20% fijo")
    m2.metric("Rentabilidad Mensual", f"{rent_mensual:.2f} %")
    m3.metric("TAE (Anualizado)", f"{tae_equivalente:.2f} %", delta="Rendimiento Financiero")

    st.caption(f"Análisis: El capital de {inv_real:,.2f} € genera un retorno total de {inv_real + ahorro_neto:,.2f} € en solo {meses} meses.")

# --- SECCIÓN 2: PARTNERS (Conexión protegida) ---
elif choice == "🤝 Partners":
    st.header("Consulta de Partners")
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="PARTNERS", ttl=0)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("⚠️ No se pudo conectar con el Excel. La calculadora sigue operativa.")
