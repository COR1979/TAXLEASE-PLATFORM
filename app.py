import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Dertogest Platform v1.1", layout="wide")
st.title("🏛️ Dertogest: Gestión de Incentivos Fiscales")

# 2. CONEXIÓN (Importe corregido para evitar ModuleNotFoundError)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de configuración: {e}")

# 3. MENÚ
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN 1: CALCULADORA (Lógica fiscal española) ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión")
    col1, col2 = st.columns(2)
    with col1:
        factu = st.number_input("Facturación Anual (€)", value=11200000)
        cuota = st.number_input("Cuota Íntegra IS (€)", value=102000)
    
    limite = 0.15 if factu > 20000000 else 0.50
    inv_opt = (cuota * limite) / 1.20

    with col2:
        st.metric("Límite Fiscal", f"{limite*100:.0f}%")
        st.success(f"Inversión Óptima: {inv_opt:,.2f} €")
    
    # Honorarios según contrato
    inv_real = st.number_input("Inversión Real (€)", value=float(inv_opt))
    st.info(f"Ahorro Neto (20%): {inv_real * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS (Contrato JV Completo) ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners")
    try:
        df = conn.read(worksheet="PARTNERS")
        st.dataframe(df)
        
        st.subheader("📝 Generar Contrato JV Profesional")
        nif_sel = st.selectbox("Selecciona Partner por NIF", df["NIF (ID único)"].tolist())
        d = df[df["NIF (ID único)"] == nif_sel].iloc[0]

        if st.button("Generar Texto Legal Completo"):
            # TEXTO ÍNTEGRO DEL DOCUMENTO DE COLABORACIÓN
            contrato_full = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE) [cite: 1]

REUNIDOS: [cite: 2]
De una parte, DERTOGEST, S.L., con NIF B61009858 y domicilio en Carrer de Borriana, 1-13, Esc. C, 2º 1ª; 08030 BARCELONA, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO). [cite: 3, 4]
De otra parte, {d['Nombre Partner (Razón Social)']}, con NIF {d['NIF (ID único)']} y domicilio en {d['Domicilio Social']}, representada por D. {d['Nombre Partner (Razón Social)']} (SOCIO COMERCIAL). [cite: 5]

EXPONEN: [cite: 6]
I. Que el SOCIO TÉCNICO gestiona activos de inversión fiscal basados en el Art. 39.7 de la LIS (Tax Lease). [cite: 7, 8]
II. Que el SOCIO COMERCIAL cuenta con una cartera de clientes para optimizar su carga tributaria. [cite: 9]

CLÁUSULAS: [cite: 11]
PRIMERA. OBJETO. Regular la colaboración para captación de inversores y formalización de contratos. [cite: 12]
SEGUNDA. DIVISIÓN DE FUNCIONES. [cite: 13]
- SOCIO TÉCNICO (DERTOGEST): Búsqueda, auditoría técnica/financiera, interlocución con plataformas y documentación legal. [cite: 14]
- SOCIO COMERCIAL: Identificación de clientes, cálculo de cuota íntegra, presentación comercial y gestión de firmas. [cite: 15]
TERCERA. MODELO ECONÓMICO Y IVA. Reparto al 50% de rendimientos brutos (Comisión Origen, Setup y Success Fee). [cite: 16, 17] Importes en Base Imponible + IVA vigente. [cite: 18]
CUARTA. TRANSPARENCIA Y LIQUIDACIÓN. Pago al SOCIO COMERCIAL en máximo 10 días tras el cobro de DERTOGEST. [cite: 20, 22]
QUINTA. GARANTÍAS TÉCNICAS. Certificación oficial (ICAA, INAEM) y Póliza de Seguro de Contingencia Fiscal. [cite: 23, 24]
SEXTA. NO CIRCUNVENCIÓN. El SOCIO COMERCIAL no contactará plataformas directamente por 2 años tras la vigencia. [cite: 25, 27]
SÉPTIMA. RGPD. Cumplimiento del Reglamento (UE) 2016/679. [cite: 28, 29]
OCTAVA. DURACIÓN. Un año prorrogable automáticamente, salvo preaviso de 30 días. [cite: 30, 31]
NOVENA. FIRMA DIGITAL. Formalización mediante firma digital avanzada. [cite: 32, 33]
"""
            st.text_area("Contrato listo para copiar:", contrato_full, height=600)
            st.download_button("📥 Descargar .txt", contrato_full, file_name=f"JV_{d['NIF (ID único)']}.txt")

    except Exception as e:
        st.error(f"Error al leer la hoja de Partners: {e}")

# --- SECCIÓN 3: INVERSORES (Contrato de Encargo Completo) ---
elif choice == "💰 Inversores":
    st.header("Gestión de Inversores")
    try:
        df_i = conn.read(worksheet="INVERSORES")
        st.dataframe(df_i)
        
        st.subheader("📝 Generar Contrato de Encargo")
        nif_inv = st.selectbox("Inversor (NIF)", df_i.iloc[:, 0].tolist())
        di = df_i[df_i.iloc[:, 0] == nif_inv].iloc[0]

        if st.button("Generar Texto de Encargo"):
            # TEXTO ÍNTEGRO DEL CONTRATO DE ENCARGO
            encargo_full = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL [cite: 34]

REUNIDOS: [cite: 35]
De una parte, DERTOGEST, S.L. (GESTOR). [cite: 36]
De otra parte, {di[1]}, con NIF {di[0]} (CLIENTE). [cite: 37]

EXPONEN: El CLIENTE encomienda al GESTOR la localización de activos fiscales (Art. 39.7 LIS / 68.2 LIRPF). [cite: 38, 39]

CLÁUSULAS: [cite: 40]
PRIMERA. OBJETO. Localización de proyectos con rentabilidad neta del 20%. 
SEGUNDA. HONORARIOS. Apertura: 300 € (Netos + IVA), descontables de la factura final. [cite: 42, 43] Success Fee: 4% (Neto + IVA). 
TERCERA. PAGO. Coincidiendo con liquidación de impuestos (30 junio o 25 julio). [cite: 45]
CUARTA. GARANTÍA. Devolución de los 300 € si no se presenta propuesta viable. 
QUINTA. RGPD. Tratamiento de datos fiscales para formalizar la inversión. [cite: 47, 48]
SEXTA. FIRMA. Firma digital avanzada con plena validez. [cite: 49]
"""
            st.text_area("Contrato de Encargo:", encargo_full, height=500)
    except Exception as e:
        st.error(f"Error: {e}")
