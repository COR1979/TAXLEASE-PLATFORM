import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. IA: PERSONALIDAD TÉCNICA (Sincronizada con Art. 39.7 LIS y Art. 68.2 LIRPF)
IA_ACTIVA = False
model = None
try:
    import google.generativeai as genai
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available_models:
            instrucciones = (
                "Eres el Asesor Senior de DERTOGEST. Tu base legal es el ARTÍCULO 39.7 LIS. "
                "CRITERIO TÉCNICO SOBRE PERSONAS FÍSICAS (IRPF): "
                "1. REQUISITO SINE QUA NON: El inversor DEBE estar en ESTIMACIÓN DIRECTA. "
                "2. PROHIBICIÓN: Los contribuyentes en ESTIMACIÓN OBJETIVA (Módulos) NO pueden ser inversores. "
                "3. BENEFICIO: El ahorro fiscal es un 20% neto garantizado sobre la aportación. "
                "Sé directo, profesional y utiliza un lenguaje jurídico-mercantil preciso."
            )
            model = genai.GenerativeModel(model_name=available_models[0], system_instruction=instrucciones)
            IA_ACTIVA = True
except Exception:
    IA_ACTIVA = False

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest Platform v13.0", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal & Gestión")

def cargar_datos(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except: return None

# 3. MENÚ LATERAL
choice = st.sidebar.selectbox("Herramientas", ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"])

# --- SECCIÓN 1: CALCULADORA ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión Tax Lease")
    col1, col2 = st.columns(2)
    with col1:
        f = st.number_input("Facturación Anual (€)", value=11200000)
        i = st.number_input("Cuota IS / IRPF (€)", value=120000)
    
    limite = 0.15 if f > 20000000 else 0.50
    inv_opt = (i * limite) / 1.20
    
    with col2:
        st.metric("Límite de Deducción", f"{limite*100:.0f}%")
        st.success(f"Inversión Óptima Sugerida: {inv_opt:,.2f} €")
        st.info(f"Ahorro Neto (20%): {inv_opt * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS (CONTRATO JV ÍNTEGRO) ---
elif choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners Mercantiles")
    df_p = cargar_datos("PARTNERS")
    if df_p is not None:
        st.dataframe(df_p)
        nif = st.selectbox("Selecciona Partner (NIF)", df_p["NIF (ID único)"].tolist())
        d = df_p[df_p["NIF (ID único)"] == nif].iloc[0]
        
        if st.button("Generar Contrato JV Profesional"):
            texto_jv = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 y domicilio en Carrer de Borriana, 1-13, Esc. C, 2º 1ª; 08030 BARCELONA, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).

De otra parte, {d['Nombre Partner (Razón Social)']}, con NIF {d['NIF (ID único)']} y domicilio en {d['Domicilio Social']}, representada por D./Dña. {d['Representante Legal']} (SOCIO COMERCIAL).

EXPONEN:
I. Que el SOCIO TÉCNICO cuenta con el conocimiento e infraestructura para gestionar activos de inversión fiscal basados en el Art. 39.7 de la LIS (Tax Lease).
II. Que el SOCIO COMERCIAL cuenta con una cartera de clientes susceptibles de optimizar su carga tributaria mediante dichos activos.
III. Que ambas partes desean colaborar bajo un modelo de transparencia total y beneficio compartido.

CLÁUSULAS:
PRIMERA. OBJETO. Regular la colaboración para la captación de inversores y la formalización de contratos de financiación en proyectos de I+D+i y Cultura.
SEGUNDA. DIVISIÓN DE FUNCIONES.
- SOCIO TÉCNICO (DERTOGEST): Búsqueda, auditoría técnica y financiera de proyectos, interlocución con plataformas y preparación de documentación legal.
- SOCIO COMERCIAL: Identificación de clientes aptos, cálculo de cuota íntegra, presentación comercial y gestión de la firma del inversor.
TERCERA. MODELO ECONÓMICO Y IVA. Las partes acuerdan repartir al 50% los rendimientos brutos (Comisión de Origen, Setup Fee y Success Fee). Importes en Base Imponible + IVA vigente.
CUARTA. TRANSPARENCIA Y LIQUIDACIÓN. Pago al SOCIO COMERCIAL en un plazo máximo de 10 días tras el cobro efectivo por parte de DERTOGEST.
QUINTA. GARANTÍAS TÉCNICAS. Cada operación contará con Certificación administrativa oficial (ICAA, INAEM o Informe Motivado) y Póliza de Seguro de Contingencia Fiscal.
SEXTA. CONFIDENCIALIDAD, PROPIEDAD Y NO CIRCUNVENCIÓN.
- Propiedad de Cartera: DERTOGEST reconoce la propiedad exclusiva de los clientes del SOCIO COMERCIAL.
- No Circunvención: El SOCIO COMERCIAL no contactará directamente con las plataformas por 2 años.
SÉPTIMA. RGPD. Cumplimiento del Reglamento (UE) 2016/679.
OCTAVA. DURACIÓN. Un año, prorrogable automáticamente.
NOVENA. FIRMA DIGITAL. Formalización mediante firma digital avanzada.
"""
            st.text_area("Contrato listo para copiar:", texto_jv, height=600)

# --- SECCIÓN 3: INVERSORES (CONTRATO DE ENCARGO ÍNTEGRO) ---
elif choice == "💰 Inversores":
    st.header("💰 Gestión de Clientes Inversores")
    df_i = cargar_datos("INVERSORES")
    if df_i is None or df_i.empty or df_i.iloc[:, 0].isnull().all():
        st.warning("No hay inversores registrados actualmente.")
    else:
        st.dataframe(df_i)
        nif_inv = st.selectbox("Inversor (NIF)", df_i.iloc[:, 0].tolist())
        filas = df_i[df_i.iloc[:, 0] == nif_inv]
        if not filas.empty:
            di = filas.iloc[0]
            if st.button("Generar Contrato de Encargo Profesional"):
                rep_inv = di[3] if len(di) > 3 else "[Representante]"
                # TEXTO ÍNTEGRO DEL ARCHIVO FACILITADO
                texto_encargo = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 (en adelante, el GESTOR).
De otra parte, {di[1]}, con NIF {di[0]} (en adelante, el CLIENTE), representada por D./Dña. {rep_inv}.

EXPONEN:
Que el CLIENTE encomienda al GESTOR la localización y auditoría de activos fiscales (Art. 39.7 LIS / 68.2 LIRPF) que permitan una optimización de su cuota íntegra de impuestos.

CLÁUSULAS:
PRIMERA. OBJETO. Localización y reserva de cupo en proyectos que garanticen una rentabilidad neta del 20% sobre la aportación realizada.
SEGUNDA. HONORARIOS.
1. Apertura de Expediente: 300 € (Netos + IVA). Este importe se descontará de la factura final.
2. Success Fee: 4% (Neto + IVA) sobre el volumen total de la inversión formalizada.
TERCERA. PAGO. El pago de los honorarios de éxito se realizará coincidiendo con el periodo de liquidación de impuestos: 30 de junio (IRPF) o 25 de julio (IS) del ejercicio siguiente a la inversión.
CUARTA. GARANTÍAS. Si el GESTOR no presenta una propuesta viable, se devolverán los 300 € íntegros (sin intereses de demora).
QUINTA. PROTECCIÓN DE DATOS. DERTOGEST procesará los datos fiscales del CLIENTE con la única finalidad de formalizar la inversión bajo el cumplimiento del RGPD.
SEXTA. FIRMA. Se formaliza mediante firma digital avanzada, teniendo plena validez jurídica.
"""
                st.text_area("Encargo completo para copiar:", texto_encargo, height=600)

# --- SECCIÓN 4: IA ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Senior Dertogest")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("Consulta técnica..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                res = model.generate_content(prompt)
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.error(f"Error: {e}")
