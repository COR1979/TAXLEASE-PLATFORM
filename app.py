import streamlit as st
import pandas as pd

# 1. Configuración de la página
st.set_page_config(page_title="TaxLease Platform v6.0", layout="wide")

st.title("🏛️ TaxLease Platform-Manager")

# 2. Menú lateral
menu = ["📊 Calculadora y Análisis", "🤝 Partners"]
choice = st.sidebar.selectbox("Selecciona sección:", menu)

# --- SECCIÓN 1: CALCULADORA ANALÍTICA ---
if choice == "📊 Calculadora y Análisis":
    st.header("🧮 Análisis de Inversión y Rentabilidad")
    
    # Bloque 1: Capacidad Fiscal
    with st.expander("1. Capacidad Fiscal del Cliente", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            nombre_cliente = st.text_input("Nombre del Cliente/Empresa", value="Empresa Ejemplo S.L.")
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
            st.warning(f"Diferencia: Faltan {diferencia:,.2f} € para agotar el cupo.")
        elif diferencia < 0:
            st.error(f"Exceso: Supera el límite en {abs(diferencia):,.2f} €.")
        else:
            st.info("Inversión ajustada al cupo máximo.")

    st.divider()

    # Bloque 3: Rendimiento Financiero
    st.subheader("3. Rendimiento y Rentabilidad Real")
    ahorro_neto = inv_real * 0.20
    rent_mensual = 20.0 / meses
    tae_equivalente = rent_mensual * 12

    m1, m2, m3 = st.columns(3)
    m1.metric("Beneficio Neto", f"{ahorro_neto:,.2f} €")
    m2.metric("Rentabilidad Mensual", f"{rent_mensual:.2f} %")
    m3.metric("TAE (Anualizado)", f"{tae_equivalente:.2f} %")

    # --- BOTÓN DE INFORME ---
    st.divider()
    if st.button("📄 Generar Informe Ejecutivo"):
        # Creamos el texto del informe
        texto_informe = f"""
        INFORME EJECUTIVO DE INVERSIÓN FISCAL (TAX LEASE)
        ------------------------------------------------
        CLIENTE: {nombre_cliente}
        FECHA: {pd.Timestamp.now().strftime('%d/%m/%Y')}
        
        1. ANÁLISIS DE CAPACIDAD FISCAL
        - Cuota Íntegra declarada: {cuota:,.2f} €
        - Límite legal aplicable: {limite*100:.0f}%
        - Capacidad máxima de deducción: {capacidad_max:,.2f} €
        - Inversión óptima para cupo: {inv_optima:,.2f} €
        
        2. DETALLE DE LA OPERACIÓN PROPUESTA
        - Importe de la inversión: {inv_real:,.2f} €
        - Ahorro fiscal generado (120%): {inv_real * 1.2:,.2f} €
        - Plazo estimado de recuperación: {meses} meses
        
        3. RENDIMIENTO FINANCIERO
        - Beneficio neto directo: {ahorro_neto:,.2f} € (20% sobre capital)
        - Rentabilidad mensual: {rent_mensual:.2f}%
        - Rentabilidad anualizada (TAE): {tae_equivalente:.2f}%
        
        Este análisis se basa en el Art. 39.7 de la LIS. 
        Inversión garantizada mediante Seguro de Contingencia Fiscal.
        """
        
        st.text_area("Vista previa del Informe (puedes copiarlo):", texto_informe, height=300)
        
        st.download_button(
            label="📥 Descargar Informe como .txt",
            data=texto_informe,
            file_name=f"Informe_TaxLease_{nombre_cliente.replace(' ', '_')}.txt",
            mime="text/plain"
        )

# --- SECCIÓN 2: PARTNERS ---
elif choice == "🤝 Partners":
    st.header("Consulta de Partners")
    try:
        from streamlit_gsheets import GSheetsConnection
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet="PARTNERS", ttl=0)
        st.dataframe(df, use_container_width=True)
    except Exception as e:
        st.error("⚠️ Error de conexión con el Excel.")
