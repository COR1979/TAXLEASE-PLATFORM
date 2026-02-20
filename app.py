import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN E INTERFAZ
st.set_page_config(page_title="Dertogest Platform v1.0", layout="wide")
st.title("🏛️ Dertogest: Gestión de Incentivos Fiscales")

# 2. CONEXIÓN A GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Error de conexión. Revisa los 'Secrets' en Streamlit Cloud.")

# 3. MENÚ
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores"]
choice = st.sidebar.selectbox("Selecciona una sección", menu)

# --- SECCIÓN 1: CALCULADORA FISCAL ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión Tax Lease")
    
    col_input, col_diag = st.columns(2)
    with col_input:
        st.subheader("Datos del Cliente")
        facturacion = st.number_input("Facturación Anual de la Empresa (€)", value=11200000, step=100000)
        cuota_is = st.number_input("Cuota Íntegra IS Inicial (€)", value=102000, step=1000)
        meses = st.slider("Plazo de recuperación (Meses)", 1, 12, 6)

    # Lógica fiscal según perfil
    es_gran_empresa = facturacion > 20000000
    limite_pct = 0.15 if es_gran_empresa else 0.50
    perfil = "Gran Empresa (>20M€)" if es_gran_empresa else "Pyme/Empresa Estándar (<20M€)"
    
    deduccion_max = cuota_is * limite_pct
    inv_optima = deduccion_max / 1.20

    with col_diag:
        st.subheader("Diagnóstico de Capacidad")
        st.write(f"**Perfil:** {perfil}")
        st.write(f"**Límite Legal:** {limite_pct*100:.0f}% de la cuota íntegra.")
        st.metric("Deducción Máxima", f"{deduccion_max:,.2f} €")
        st.success(f"🎯 Inversión Óptima Sugerida: {inv_optima:,.2f} €")

    st.divider()
    st.subheader("📉 Simulador de Impacto Final")
    inv_real = st.number_input("Ajustar Inversión Real (€)", value=float(inv_optima))
    
    # Métricas de rentabilidad
    deduccion_gen = inv_real * 1.20
    ahorro_neto = inv_real * 0.20
    rent_mensual = 20.0 / meses
    tae = rent_mensual * 12

    c1, c2, c3 = st.columns(3)
    c1.metric("Deducción Generada", f"{deduccion_gen:,.2f} €")
    c2.metric("Ahorro Neto (Beneficio)", f"{ahorro_neto:,.2f} €", "↑ 20% neto")
    c3.metric("Nueva Cuota a Pagar", f"{max(0.0, cuota_is - deduccion_gen):,.2f} €", f"-{deduccion_gen:,.2f} €", delta_color="normal")

    st.info(f"Análisis Financiero: Rentabilidad Mensual del {rent_mensual:.2f}% | TAE Anualizada: {tae:.2f}%")

# --- SECCIÓN 2: PARTNERS (JV) ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Colaboradores Mercantiles")
    try:
        # Cargamos datos según tus columnas (A: NIF, B: Nombre, C: Domicilio...)
        df = conn.read(worksheet="PARTNERS")
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        st.subheader("📝 Redactar Contrato JV")
        nif_sel = st.selectbox("Selecciona Partner por NIF (ID)", df["NIF (ID único)"].tolist())
        datos = df[df["NIF (ID único)"] == nif_sel].iloc[0]

        if st.button("Generar Texto Legal JV"):
            texto = f"""CONTRATO DE COLABORACIÓN MERCANTIL (JOINT VENTURE)
--------------------------------------------------
REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858[cite: 3].
De otra parte, {datos['Nombre Partner (Razón Social']}, con NIF {datos['NIF (ID único)']} y domicilio en {datos['Domicilio Social']}.

ACUERDOS:
1. REPARTO: 50% de rendimientos brutos sobre Base Imponible (+ IVA).
2. LIQUIDACIÓN: Pago en un máximo de 10 días tras el cobro[cite: 22].
3. NO CIRCUNVENCIÓN: Compromiso de no contactar plataformas directamente por 2 años[cite: 27].
4. GARANTÍAS: Certificación administrativa oficial y Póliza de Seguro[cite: 24].
--------------------------------------------------"""
            st.text_area("Copia el contrato aquí:", texto, height=300)
    except Exception as e:
        st.error(f"Error al leer la hoja de Partners: {e}")

# --- SECCIÓN 3: INVERSORES ---
elif choice == "💰 Inversores":
    st.header("Gestión de Clientes Inversores")
    try:
        df_i = conn.read(worksheet="INVERSORES")
        st.dataframe(df_i)
        
        st.divider()
        st.subheader("📝 Redactar Contrato de Encargo")
        nif_inv = st.selectbox("Selecciona Inversor por NIF", df_i.iloc[:, 0].tolist())
        d_inv = df_i[df_i.iloc[:, 0] == nif_inv].iloc[0]

        if st.button("Generar Texto Legal Inversor"):
            texto_inv = f"""CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL
--------------------------------------------------
GESTOR: DERTOGEST, S.L. [cite: 36]
CLIENTE: {d_inv[1]} con NIF {d_inv[0]} [cite: 37]

ACUERDOS:
1. RENTABILIDAD: Garantizada rentabilidad neta del 20%[cite: 41].
2. HONORARIOS: 300 € (Apertura) + 4% Success Fee (Netos + IVA).
3. GARANTÍA: Devolución íntegra de 300 € si no hay propuesta viable[cite: 46].
--------------------------------------------------"""
            st.text_area("Copia el contrato aquí:", texto_inv, height=300)
    except Exception:
        st.warning("Pestaña 'INVERSORES' no encontrada o vacía.")
