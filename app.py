import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE IA
try:
    import google.generativeai as genai
    IA_READY = True
except ImportError:
    IA_READY = False

# 2. CONFIGURACIÓN
st.set_page_config(page_title="Dertogest AI Hub", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal & Gestión")

# 3. FUNCIÓN DE DATOS SEGURA (Evita el error 'Representante Legal')
def cargar_datos(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        df.columns = df.columns.str.strip() # Limpieza de espacios invisibles
        return df
    except Exception as e:
        st.error(f"Error en pestaña {hoja}: {e}")
        return None

# 4. CONFIGURAR IA
if IA_READY and "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos el nombre de modelo más estable
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        IA_READY = False

# 5. MENÚ LATERAL
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"]
choice = st.sidebar.selectbox("Menú", menu)

# --- SECCIÓN 1: CALCULADORA ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión")
    c1, c2 = st.columns(2)
    with c1:
        f = st.number_input("Facturación Anual (€)", value=11200000)
        i = st.number_input("Cuota Íntegra IS (€)", value=102000)
    limite = 0.15 if f > 20000000 else 0.50
    inv_opt = (i * limite) / 1.20
    with c2:
        st.metric("Límite Fiscal", f"{limite*100:.0f}%")
        st.success(f"Inversión Óptima: {inv_opt:,.2f} €")
        st.info(f"Beneficio Neto (20%): {inv_opt * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners")
    df_p = cargar_datos("PARTNERS")
    if df_p is not None:
        st.dataframe(df_p)
        nif = st.selectbox("Selecciona NIF", df_p["NIF (ID único)"].tolist())
        d = df_p[df_p["NIF (ID único)"] == nif].iloc[0]
        if st.button("Generar Borrador"):
            # Limpieza para asegurar que 'Representante Legal' existe
            st.text_area("Contrato:", f"PARTNER: {d['Nombre Partner (Razón Social)']}\nREP: {d['Representante Legal']}\nNIF: {d['NIF (ID único)']}", height=250)

# --- SECCIÓN 3: INVERSORES ---
elif choice == "💰 Inversores":
    st.header("Gestión de Inversores")
    df_i = cargar_datos("INVERSORES")
    if df_i is not None:
        st.dataframe(df_i)

# --- SECCIÓN 4: ASESOR IA (CORREGIDO) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    
    if "GOOGLE_API_KEY" not in st.secrets:
        st.warning("Verifica la API Key en los Secrets.")
    else:
        # CORRECCIÓN: Inicializamos 'messages' para evitar el AttributeError
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Mostramos historial
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        
        if prompt := st.chat_input("¿Qué duda legal tienes?"):
            # Guardamos la pregunta del usuario
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                try:
                    # Instrucción de contexto directa
                    ctx = f"Eres experto en Tax Lease (Art. 39.7 LIS). Pregunta: {prompt}"
                    response = model.generate_content(ctx)
                    st.markdown(response.text)
                    # Guardamos la respuesta
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                except Exception as e:
                    st.error(f"Error en la IA: {e}")
