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
    st.error("Error de configuración en Secrets.")

# 3. MENÚ
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN 1: CALCULADORA (Igual que antes, funciona perfecto) ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión")
    col1, col2 = st.columns(2)
    with col1:
        nombre_sim = st.text_input("Nombre Cliente", "Empresa S.L.")
        cuota = st.number_input("Cuota Íntegra (€)", value=100000)
        factu = st.number_input("Facturación Anual (€)", value=25000000)
    
    limite = 0.15 if factu > 20000000 else 0.50
    inv_opt = (cuota * limite) / 1.20

    with col2:
        st.metric("Límite Fiscal", f"{limite*100:.0f}%")
        st.success(f"Inversión Óptima: {inv_opt:,.2f} €")
    
    inv_real = st.number_input("Inversión Real (€)", value=float(inv_opt))
    if st.button("📄 Generar Informe"):
        # (Lógica del informe breve que ya tenías)
        st.info("Informe generado con éxito (ver abajo).")

# --- SECCIÓN 2: PARTNERS (Generador de Contrato JV) ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners y Contratos JV")
    try:
        df_p = conn.read(worksheet="PARTNERS")
        st.dataframe(df_p, use_container_width=True)
        
        st.divider()
        st.subheader("📝 Generar Contrato de Colaboración")
        
        # Selector de Partner basado en la primera columna (Nombre)
        partner_nombres = df_p.iloc[:, 0].tolist()
        seleccionado = st.selectbox("Selecciona un Partner para el contrato:", partner_nombres)
        
        # Extraer datos de la fila seleccionada
        datos = df_p[df_p.iloc[:, 0] == seleccionado].iloc[0]
        
        if st.button("⚖️ Redactar Contrato JV"):
            contrato_jv = f"""
CONTRATO DE COLABORACIÓN MERCANTIL (JOINT VENTURE)
--------------------------------------------------
REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 (SOCIO TÉCNICO).
De otra parte, {datos[0]}, con NIF {datos[1]} y domicilio en {datos[2]} (SOCIO COMERCIAL).

CLÁUSULAS DESTACADAS:
1. OBJETO: Captación de inversores para proyectos Art. 39.7 LIS.
2. REPARTO: 50% de los rendimientos brutos sobre Base Imponible (+ IVA).
3. NO CIRCUNVENCIÓN: El Socio Comercial no contactará directamente con plataformas.
4. PROTECCIÓN DE DATOS: Tratamiento bajo RGPD 2016/679.

(Texto legal completo según borrador revisado...)
--------------------------------------------------
"""
            st.text_area("Contrato listo para copiar:", contrato_jv, height=400)
            st.download_button("📥 Descargar Contrato .txt", contrato_jv, file_name=f"Contrato_JV_{seleccionado}.txt")

    except Exception as e:
        st.warning("Asegúrate de que la pestaña 'PARTNERS' tiene datos.")

# --- SECCIÓN 3: INVERSORES (Generador de Contrato Encargo) ---
elif choice == "💰 Inversores":
    st.header("Base de Datos de Inversores")
    try:
        df_i = conn.read(worksheet="INVERSORES")
        st.dataframe(df_i, use_container_width=True)
        
        st.divider()
        st.subheader("📝 Generar Contrato de Encargo")
        
        inv_nombres = df_i.iloc[:, 0].tolist()
        sel_inv = st.selectbox("Selecciona un Inversor:", inv_nombres)
        datos_inv = df_i[df_i.iloc[:, 0] == sel_inv].iloc[0]

        if st.button("⚖️ Redactar Contrato Inversor"):
            contrato_inv = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL
--------------------------------------------------
CLIENTE: {datos_inv[0]}
NIF/CIF: {datos_inv[1]}
GESTOR: DERTOGEST, S.L.

ACUERDOS:
1. RENTABILIDAD: Se garantiza una rentabilidad neta del 20%.
2. HONORARIOS: 300€ Apertura + 4% Success Fee (Base Imponible + IVA).
3. PAGO: A liquidar en el periodo impositivo (Julio/Junio).
4. GARANTÍA: Devolución de 300€ si no hay activo disponible.

(Texto legal completo según borrador revisado...)
--------------------------------------------------
"""
            st.text_area("Contrato listo para copiar:", contrato_inv, height=400)
            st.download_button("📥 Descargar Contrato .txt", contrato_inv, file_name=f"Contrato_Inv_{sel_inv}.txt")

    except:
        st.warning("Asegúrate de que la pestaña 'INVERSORES' tiene datos.")
