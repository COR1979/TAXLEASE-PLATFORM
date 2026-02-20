import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# Intentamos importar la IA, pero si falla que no rompa la App
try:
    import google.generativeai as genai
    IA_DISPONIBLE = True
except ImportError:
    IA_DISPONIBLE = False

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest Platform", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal")

# 2. FUNCIÓN DE CARGA SEGURA (Evita el error 'Representante Legal')
def cargar_datos_seguro(nombre_hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=nombre_hoja, ttl=0)
        df.columns = df.columns.str.strip() # Limpieza de espacios invisibles
        return df
    except Exception as e:
        st.error(f"Error al conectar con la hoja {nombre_hoja}: {e}")
        return None

# 3. CONFIGURAR IA
if IA_DISPONIBLE and "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        model = genai.GenerativeModel('gemini-1.5-flash', 
            system_instruction="Eres el Asesor Senior de DERTOGEST. Experto en Art. 39.7 LIS.")
    except:
        IA_DISPONIBLE = False

# 4. NAVEGACIÓN
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"]
choice = st.sidebar.selectbox("Menú Principal", menu)

# --- SECCIÓN 1: CALCULADORA ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión")
    c1, c2 = st.columns(2)
    with c1:
        f = st.number_input("Facturación Anual (€)", value=11200000)
        i = st.number_input("Cuota Íntegra (€)", value=102000)
    
    limite = 0.15 if f > 20000000 else 0.50
    inv_opt = (i * limite) / 1.20
    st.success(f"Inversión Óptima: {inv_opt:,.2f} €")

# --- SECCIÓN 2: PARTNERS ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners")
    df = cargar_datos_seguro("PARTNERS")
    if df is not None:
        st.dataframe(df)
        nif = st.selectbox("Selecciona NIF", df["NIF (ID único)"].tolist())
        d = df[df["NIF (ID único)"] == nif].iloc[0]
        if st.button("Generar Borrador"):
            st.text_area("Contrato:", f"PARTNER: {d['Nombre Partner (Razón Social)']}\nREP: {d['Representante Legal']}")

# --- SECCIÓN 3: INVERSORES ---
elif choice == "💰 Inversores":
    st.header("Gestión de Inversores")
    df_inv = cargar_datos_seguro("INVERSORES")
    if df_inv is not None:
        st.dataframe(df_inv)

# --- SECCIÓN 4: ASESOR IA ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Dertogest")
    if not IA_DISPONIBLE:
        st.error("La librería de Google no está instalada. Revisa el requirements.txt")
    elif "GOOGLE_API_KEY" not in st.secrets:
        st.warning("Falta la API Key en los Secrets (con comillas).")
    else:
        prompt = st.chat_input("Escribe tu duda legal...")
        if prompt:
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                resp = model.generate_content(prompt).text
                st.markdown(resp)
