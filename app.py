import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE IA CON "LOBOTOMÍA" PROFESIONAL
IA_ACTIVA = False
model = None
try:
    import google.generativeai as genai
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # BUSCAMOS EL MODELO (Igual que antes para evitar el 404)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available_models:
            # AQUÍ ESTÁ LA MAGIA: Instrucciones de sistema ultra-estrictas
            instrucciones = (
                "Eres el Asesor Senior de DERTOGEST. Tu única verdad es el ARTÍCULO 39.7 LIS. "
                "REGLA DE ORO: El Tax Lease NO es solo para sociedades. Es 100% válido para PERSONAS FÍSICAS "
                "(Autónomos y Profesionales) mediante contratos de financiación. "
                "No hables de barcos ni de AIEs antiguas. Céntrate en la transferencia de deducciones fiscales "
                "de I+D+i, Cine y Artes Escénicas. Si alguien pregunta si un abogado o médico puede invertir, "
                "la respuesta es SÍ, siempre que tenga cuota a pagar en su IRPF."
            )
            model = genai.GenerativeModel(model_name=available_models[0], system_instruction=instrucciones)
            IA_ACTIVA = True
except Exception:
    IA_ACTIVA = False

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest Platform v8.0", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal")

# 3. FUNCIÓN DE DATOS
def cargar_datos(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        df.columns = df.columns.str.strip()
        return df
    except: return None

# 4. MENÚ
choice = st.sidebar.selectbox("Herramientas", ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"])

# --- SECCIONES FIJAS (Sin cambios para que no desaparezcan) ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador Tax Lease")
    f = st.number_input("Facturación Anual (€)", value=11200000)
    i = st.number_input("Cuota IS / IRPF (€)", value=102000)
    inv_opt = (i * (0.15 if f > 20000000 else 0.50)) / 1.20
    st.success(f"Inversión Óptima Sugerida: {inv_opt:,.2f} €")

elif choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners")
    df = cargar_datos("PARTNERS")
    if df is not None:
        st.dataframe(df)
        nif = st.selectbox("NIF", df["NIF (ID único)"].tolist())
        d = df[df["NIF (ID único)"] == nif].iloc[0]
        if st.button("Generar Contrato"):
            st.text_area("Contrato Íntegro:", f"DERTOGEST S.L. y {d['Nombre Partner (Razón Social)']}...", height=400)

elif choice == "💰 Inversores":
    st.header("💰 Gestión de Inversores")
    df = cargar_datos("INVERSORES")
    if df is not None: st.dataframe(df)

# --- SECCIÓN IA (CON LA NUEVA PERSONALIDAD) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Dertogest (Art. 39.7 LIS)")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("Pregúntame sobre la inversión para profesionales..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        with st.chat_message("assistant"):
            try:
                # La IA ahora responderá bajo las nuevas reglas
                res = model.generate_content(prompt)
                st.markdown(res.text)
                st.session_state.messages.append({"role": "assistant", "content": res.text})
            except Exception as e:
                st.error(f"Error: {e}")
