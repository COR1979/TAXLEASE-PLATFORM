import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE LIBRERÍAS DE IA
IA_ACTIVA = False
try:
    import google.generativeai as genai
    IA_ACTIVA = True
except ImportError:
    st.error("Librería 'google-generativeai' no encontrada. Revisa requirements.txt")

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest AI Hub", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal")

# 3. FUNCIÓN DE DATOS (Solución definitiva para image_d20fc9)
def obtener_datos(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        # Limpiamos nombres de columnas de espacios traicioneros
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error de conexión con Excel: {e}")
        return None

# 4. CONFIGURAR IA (Con prevención de error NotFound)
model = None
if IA_ACTIVA and "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos el nombre de modelo más estándar y compatible
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error al configurar IA: {e}")

# 5. MENÚ
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "🤖 Asesor IA Fiscal"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN PARTNERS (Sincronizada con image_d20bcf) ---
if choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners")
    df_p = obtener_datos("PARTNERS")
    if df_p is not None:
        st.dataframe(df_p)
        nif = st.selectbox("Selecciona NIF", df_p["NIF (ID único)"].tolist())
        d = df_p[df_p["NIF (ID único)"] == nif].iloc[0]
        
        if st.button("Generar Borrador Contrato"):
            st.text_area("Borrador para Google Docs:", 
                f"PARTNER: {d['Nombre Partner (Razón Social)']}\nREPRESENTANTE: {d['Representante Legal']}\nNIF: {d['NIF (ID único)']}", 
                height=250)

# --- SECCIÓN ASESOR IA (Con gestión de errores google.api_core) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    
    if "GOOGLE_API_KEY" not in st.secrets:
        st.warning("Verifica que la API Key esté en la primera línea de los Secrets con comillas.")
    elif model is None:
        st.error("El modelo de IA no pudo inicializarse.")
    else:
        # Chat interactivo
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if pregunta := st.chat_input("¿En qué puedo ayudarte hoy?"):
            st.session_state.chat_history.append({"role": "user", "content": pregunta})
            with st.chat_message("user"): st.markdown(pregunta)
            
            with st.chat_message("assistant"):
                try:
                    # Instrucción de contexto rápida para el modelo
                    contexto = f"Actúa como experto en Tax Lease España (Art 39.7 LIS). Pregunta: {pregunta}"
                    resultado = model.generate_content(contexto)
                    st.markdown(resultado.text)
                    st.session_state.chat_history.append({"role": "assistant", "content": resultado.text})
                except Exception as e:
                    st.error(f"Error de la IA: {e}. Intenta refrescar la página.")
