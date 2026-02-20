import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Dertogest Platform v1.2", layout="wide")
st.title("🏛️ Dertogest: Gestión de Incentivos Fiscales")

# 2. CONEXIÓN
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
        st.success(f"Inversión Óptima Sugerida: {inv_opt:,.2f} €")
    
    inv_real = st.number_input("Inversión Real Propuesta (€)", value=float(inv_opt))
    st.info(f"Ahorro Neto Directo (20%): {inv_real * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS (Contrato JV Completo con Protección de Cartera) ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners")
    try:
        df = conn.read(worksheet="PARTNERS")
        st.dataframe(df)
        
        st.subheader("📝 Generar Contrato de Colaboración (JV)")
        nif_sel = st.selectbox("Selecciona Partner por NIF", df["NIF (ID único)"].tolist())
        d = df[df["NIF (ID único)"] == nif_sel].iloc[0]

        if st.button("Generar Texto Legal Completo"):
            # TEXTO ÍNTEGRO DEL DOCUMENTO DE COLABORACIÓN
            contrato_full = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 y domicilio en Carrer de Borriana, 1-13, Esc. C, 2º 1ª; 08030 BARCELONA, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).
De otra parte, {d['Nombre Partner (Razón Social)']}, con NIF {d['NIF (ID único)']} y domicilio en {d['Domicilio Social']} (SOCIO COMERCIAL).

EXPONEN:
I. Que el SOCIO TÉCNICO gestiona activos de inversión fiscal (Art. 39.7 LIS).
II. Que el SOCIO COMERCIAL cuenta con una cartera de clientes para optimizar su carga tributaria.

CLÁUSULAS:
PRIMERA. OBJETO. Colaboración para la captación de inversores y formalización de contratos.
SEGUNDA. DIVISIÓN DE FUNCIONES. DERTOGEST asume la parte técnica y financiera; el SOCIO COMERCIAL la identificación y gestión del cliente.
TERCERA. MODELO ECONÓMICO. Reparto al 50% de rendimientos brutos sobre Base Imponible (+ IVA).
CUARTA. TRANSPARENCIA Y LIQUIDACIÓN. Pago en un máximo de 10 días tras el cobro efectivo por DERTOGEST.
QUINTA. GARANTÍAS TÉCNICAS. Certificación oficial y Póliza de Seguro de Contingencia Fiscal.

SEXTA. CONFIDENCIALIDAD, PROPIEDAD Y NO CIRCUNVENCIÓN.
1. PROPIEDAD DE CARTERA: DERTOGEST reconoce la propiedad exclusiva de los clientes por parte del SOCIO COMERCIAL y se compromete formalmente a NO ofrecerles servicios de asesoría general ni cualquier gestión ajena al presente contrato de Tax Lease.
2. NO CIRCUNVENCIÓN: El SOCIO COMERCIAL no contactará plataformas directamente durante 2 años.

SÉPTIMA. RGPD. Cumplimiento del Reglamento (UE) 2016/679.
OCTAVA. DURACIÓN. Un año prorrogable automáticamente.
NOVENA. FIRMA DIGITAL. Validez mediante firma digital avanzada.
"""
            st.text_area("Contrato listo para copiar:", contrato_full, height=600)
            st.download_button("📥 Descargar Contrato .txt", contrato_full, file_name=f"Contrato_JV_{d['NIF (ID único)']}.txt")

    except Exception as e:
        st.error(f"Error al leer la hoja de Partners: {e}")

# --- SECCIÓN 3: INVERSORES (Contrato de Encargo Completo) ---
elif choice == "💰 Inversores":
    st.header("Gestión de Inversores")
    try:
        df_i = conn.read(worksheet="INVERSORES")
        st.dataframe(df_i)
        
        st.subheader("📝 Generar Contrato de Encargo")
        nif_inv = st.selectbox("Selecciona Inversor por NIF", df_i.iloc[:, 0].tolist())
        di = df_i[df_i.iloc[:, 0] == nif_inv].iloc[0]

        if st.button("Generar Texto de Encargo"):
            encargo_full = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS: DERTOGEST, S.L. (GESTOR) y {di[1]} con NIF {di[0]} (CLIENTE).

CLÁUSULAS:
PRIMERA. OBJETO. Localización de activos con rentabilidad neta garantizada del 20%.
SEGUNDA. HONORARIOS. 300 € (Apertura) + 4% Success Fee (Netos + IVA). Los 300€ se descuentan del pago final.
TERCERA. PAGO. En periodo de liquidación de impuestos (Junio/Julio).
CUARTA. GARANTÍA. Devolución de los 300 € si no se presenta propuesta viable en plazo.
QUINTA. RGPD. Tratamiento exclusivo de datos para la inversión fiscal.
SEXTA. FIRMA. Formalización digital avanzada.
"""
            st.text_area("Contrato de Encargo:", encargo_full, height=500)
    except Exception as e:
        st.error(f"Error: {e}")
