import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. IA: PERSONALIDAD BLINDADA (Art. 39.7 LIS + Matiz Estimación Directa)
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
                "CRITERIO TÉCNICO: La inversión es apta para sociedades (IS) y personas físicas (IRPF). "
                "REQUISITO SINE QUA NON: En IRPF, el inversor DEBE tributar en ESTIMACIÓN DIRECTA "
                "(ya sea Normal o Simplificada). Los contribuyentes en ESTIMACIÓN OBJETIVA (Módulos) "
                "quedan excluidos. No hables de barcos ni de AIEs antiguas. Centrado en el 20% de beneficio."
            )
            model = genai.GenerativeModel(model_name=available_models[0], system_instruction=instrucciones)
            IA_ACTIVA = True
except Exception:
    IA_ACTIVA = False

# 2. CONFIGURACIÓN
st.set_page_config(page_title="Dertogest Platform v10.0", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal")

def cargar_datos(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except: return None

# 3. MENÚ LATERAL
choice = st.sidebar.selectbox("Herramientas", ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"])

# --- SECCIÓN 1: CALCULADORA (RESTAURADA) ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión")
    col1, col2 = st.columns(2)
    with col1:
        f = st.number_input("Facturación Anual (€)", value=11200000)
        i = st.number_input("Cuota IS / IRPF (€)", value=120000)
    
    limite = 0.15 if f > 20000000 else 0.50
    inv_opt = (i * limite) / 1.20
    
    with col2:
        st.metric("Límite Fiscal Aplicable", f"{limite*100:.0f}%")
        st.success(f"Inversión Óptima: {inv_opt:,.2f} €")
        st.info(f"Ahorro Neto (20%): {inv_opt * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS (CONTRATO ÍNTEGRO DE 9 CLÁUSULAS) ---
elif choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners Mercantiles")
    df = cargar_datos("PARTNERS")
    if df is not None:
        st.dataframe(df)
        nif = st.selectbox("Partner (NIF)", df["NIF (ID único)"].tolist())
        d = df[df["NIF (ID único)"] == nif].iloc[0]
        
        if st.button("Generar Contrato"):
            texto_jv = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).
De otra parte, {d['Nombre Partner (Razón Social)']}, con NIF {d['NIF (ID único)']} y domicilio en {d['Domicilio Social']}, representada por D./Dña. {d['Representante Legal']} (SOCIO COMERCIAL).

CLÁUSULAS:
PRIMERA. OBJETO. Gestión de activos de inversión fiscal (Art. 39.7 LIS).
SEGUNDA. FUNCIONES. DERTOGEST asume la parte técnica; el Socio Comercial la captación.
TERCERA. REPARTO. 50% de rendimientos brutos sobre Base Imponible (+ IVA).
CUARTA. LIQUIDACIÓN. Pago al Socio Comercial en máximo 10 días tras el cobro.
QUINTA. PROTECCIÓN DE CARTERA. DERTOGEST se compromete a NO ofrecer servicios de asesoría general ni gestiones ajenas al Tax Lease a los clientes del Socio Comercial.
SEXTA. NO CIRCUNVENCIÓN. Prohibición de contacto directo con plataformas por 2 años.
SÉPTIMA. RGPD. Cumplimiento del Reglamento (UE) 2016/679.
OCTAVA. DURACIÓN. Un año prorrogable.
NOVENA. FIRMA DIGITAL. Validez mediante firma digital avanzada.
"""
            st.text_area("Contrato Completo:", texto_jv, height=600)

# --- SECCIÓN 3: INVERSORES ---
elif choice == "💰 Inversores":
    st.header("💰 Gestión de Inversores")
    df_inv = cargar_datos("INVERSORES")
    if df_inv is None or df_inv.empty:
        st.warning("No hay inversores registrados actualmente.")
    else:
        st.dataframe(df_inv)
        nif_i = st.selectbox("Inversor (NIF)", df_inv.iloc[:, 0].tolist())
        datos_i = df_inv[df_inv.iloc[:, 0] == nif_i]
        if not datos_i.empty:
            di = datos_i.iloc[0]
            if st.button("Generar Encargo"):
                rep = di[3] if len(di) > 3 else "[Representante]"
                st.text_area("Encargo Completo:", f"CONTRATO ENCARGO: DERTOGEST y {di[1]} (NIF {di[0]}). Rentabilidad: 20%. Honorarios: 300€ + 4% Éxito.", height=400)

# --- SECCIÓN 4: IA (CON LA VERDAD TÉCNICA) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Senior Dertogest")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("¿Qué duda técnica tienes sobre el Art. 39.7 LIS?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                res = model.generate_content(prompt)
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.error(f"Error: {e}")
