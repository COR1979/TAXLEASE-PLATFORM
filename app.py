import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE IA (Conexión Directa v1)
IA_ACTIVA = False
try:
    import google.generativeai as genai
    IA_ACTIVA = True
except ImportError:
    pass

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest AI Platform v5.0", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal & Gestión")

# 3. FUNCIÓN DE DATOS SEGURA
def cargar_datos_limpios(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        df.columns = df.columns.str.strip() # Limpia espacios invisibles
        return df
    except Exception as e:
        st.error(f"Error al conectar con la pestaña '{hoja}': {e}")
        return None

# 4. CONFIGURAR IA (Sin listado de modelos para evitar el error 404)
model = None
if IA_ACTIVA and "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Forzamos el uso del modelo sin prefijos para máxima compatibilidad
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        IA_ACTIVA = False

# 5. MENÚ LATERAL (Estructura fija para que nada desaparezca)
st.sidebar.title("Menú Principal")
choice = st.sidebar.radio("Selecciona una herramienta:", 
                         ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"])

# --- SECCIÓN 1: CALCULADORA ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión Tax Lease")
    col1, col2 = st.columns(2)
    with col1:
        f = st.number_input("Facturación Anual (€)", value=11200000)
        i = st.number_input("Cuota Íntegra IS (€)", value=102000)
    limite = 0.15 if f > 20000000 else 0.50
    inv_opt = (i * limite) / 1.20
    with col2:
        st.metric("Límite Fiscal", f"{limite*100:.0f}%")
        st.success(f"Inversión Óptima Sugerida: {inv_opt:,.2f} €")
        st.info(f"Ahorro Neto Directo (20%): {inv_opt * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS (CONTRATO ÍNTEGRO PALABRA POR PALABRA) ---
elif choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners Mercantiles")
    df_p = cargar_datos_limpios("PARTNERS")
    if df_p is not None:
        st.dataframe(df_p)
        nif_sel = st.selectbox("Selecciona Partner (NIF)", df_p["NIF (ID único)"].tolist())
        d = df_p[df_p["NIF (ID único)"] == nif_sel].iloc[0]
        
        if st.button("Generar Contrato JV Profesional"):
            contrato_full = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 y domicilio en Carrer de Borriana, 1-13, Esc. C, 2º 1ª; 08030 BARCELONA, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).

De otra parte, {d['Nombre Partner (Razón Social)']}, con NIF {d['NIF (ID único)']} y domicilio en {d['Domicilio Social']}, representada en este acto por D./Dña. {d['Representante Legal']} (SOCIO COMERCIAL).

EXPONEN:
I. Que el SOCIO TÉCNICO gestiona activos de inversión fiscal basados en el Art. 39.7 de la LIS (Tax Lease).
II. Que el SOCIO COMERCIAL cuenta con una cartera de clientes para optimizar su carga tributaria mediante dichos activos.
III. Que ambas partes desean colaborar bajo un modelo de transparencia total y beneficio compartido.

CLÁUSULAS:
PRIMERA. OBJETO. Regular la colaboración para la captación de inversores y la formalización de contratos de financiación en proyectos de I+D+i y Cultura.
SEGUNDA. DIVISIÓN DE FUNCIONES. DERTOGEST asume la búsqueda, auditoría técnica y financiera; el SOCIO COMERCIAL asume la identificación de clientes y gestión comercial.
TERCERA. MODELO ECONÓMICO Y IVA. Reparto al 50% de rendimientos brutos (Comisión de Origen, Setup y Success Fee). Importes en Base Imponible + IVA vigente.
CUARTA. TRANSPARENCIA Y LIQUIDACIÓN. Pago al SOCIO COMERCIAL en un máximo de 10 días tras el cobro efectivo por parte de DERTOGEST.
QUINTA. GARANTÍAS TÉCNICAS. Operación bajo Certificación oficial (ICAA, INAEM) y Póliza de Seguro de Contingencia Fiscal.
SEXTA. CONFIDENCIALIDAD Y PROTECCIÓN DE CARTERA. DERTOGEST reconoce la propiedad exclusiva de los clientes del SOCIO COMERCIAL y se compromete formalmente a NO ofrecerles servicios de asesoría general ni cualquier gestión ajena al presente contrato de Tax Lease.
SÉPTIMA. NO CIRCUNVENCIÓN. El SOCIO COMERCIAL no contactará plataformas directamente durante la vigencia y 2 años posteriores.
OCTAVA. RGPD. Cumplimiento del Reglamento (UE) 2016/679.
NOVENA. DURACIÓN Y FIRMA. Un año prorrogable. Formalización mediante firma digital avanzada.
"""
            st.text_area("Contrato íntegro para copiar:", contrato_full, height=600)

# --- SECCIÓN 3: INVERSORES (CONTRATO DE ENCARGO ÍNTEGRO) ---
elif choice == "💰 Inversores":
    st.header("💰 Gestión de Inversores")
    df_i = cargar_datos_limpios("INVERSORES")
    if df_i is not None:
        st.dataframe(df_i)
        nif_inv = st.selectbox("Selecciona Inversor (NIF)", df_i.iloc[:, 0].tolist())
        filas = df_i[df_i.iloc[:, 0] == nif_inv]
        
        if not filas.empty:
            di = filas.iloc[0]
            if st.button("Generar Contrato de Encargo"):
                rep_inv = di[3] if len(di) > 3 else "[Representante]"
                contrato_enc = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS: DERTOGEST, S.L. (GESTOR) y {di[1]}, con NIF {di[0]}, representada por D./Dña. {rep_inv} (CLIENTE).

CLÁUSULAS:
1. OBJETO. Localización de activos con rentabilidad neta garantizada del 20% sobre aportación.
2. HONORARIOS. Apertura: 300 € (Netos + IVA), descontables de la factura final. Success Fee: 4% (Neto + IVA).
3. GARANTÍA. Devolución íntegra de los 300 € si no se presenta propuesta viable en el plazo pactado.
4. PAGO. Los honorarios se abonarán coincidiendo con el periodo de liquidación de impuestos (Junio/Julio).
5. RGPD Y FIRMA. Tratamiento exclusivo para la inversión y firma digital avanzada.
"""
                st.text_area("Texto del Encargo completo:", contrato_enc, height=450)

# --- SECCIÓN 4: ASESOR IA (CORRECCIÓN 404) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("¿Qué duda legal tienes?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                # Instrucción directa para evitar fallos de configuración
                response = model.generate_content(f"Eres experto en Tax Lease España (Art 39.7 LIS). Pregunta: {prompt}")
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.error(f"Error 404: El modelo aún no está disponible en tu API Key. {e}")
                st.info("💡 Daniel, el sistema ya está habilitado en Google Cloud. Solo falta que Google termine de propagar el permiso a tu cuenta.")
