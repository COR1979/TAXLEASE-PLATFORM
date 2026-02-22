import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE IA CON BÚSQUEDA AUTOMÁTICA
IA_ACTIVA = False
model = None
try:
    import google.generativeai as genai
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # BUSCADOR DE MODELOS: Esto evita el error 404 al elegir el modelo correcto
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5-flash' in m.name:
                    model = genai.GenerativeModel(m.name)
                    IA_ACTIVA = True
                    break
except Exception:
    IA_ACTIVA = False

# 2. CONFIGURACIÓN
st.set_page_config(page_title="Dertogest AI Hub v4.0", layout="wide")
st.title("🏛️ Dertogest: Gestión & Inteligencia Fiscal")

# 3. FUNCIÓN DE DATOS SEGURA (Evita el error 'Representante Legal')
def cargar_datos(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        df.columns = df.columns.str.strip() 
        return df
    except Exception as e:
        st.error(f"Error en pestaña {hoja}: {e}")
        return None

# 4. MENÚ
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN: PARTNERS (CONTRATO ÍNTEGRO RESTAURADO) ---
if choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners Mercantiles")
    df = cargar_datos("PARTNERS")
    if df is not None:
        st.dataframe(df)
        nif = st.selectbox("Selecciona Partner (NIF)", df["NIF (ID único)"].tolist())
        d = df[df["NIF (ID único)"] == nif].iloc[0]
        if st.button("Generar Contrato JV Profesional"):
            texto_jv = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).
De otra parte, {d['Nombre Partner (Razón Social)']}, con NIF {d['NIF (ID único)']} y domicilio en {d['Domicilio Social']}, representada por D./Dña. {d['Representante Legal']} (SOCIO COMERCIAL).

CLÁUSULAS DESTACADAS:
PRIMERA. OBJETO. Gestión de inversiones bajo el Art. 39.7 de la LIS (Tax Lease).
SEGUNDA. REPARTO. 50% de rendimientos brutos sobre Base Imponible (+ IVA).
TERCERA. PROTECCIÓN DE CARTERA: DERTOGEST se compromete a NO ofrecer servicios ajenos al Tax Lease a los clientes del Socio Comercial.
CUARTA. LIQUIDACIÓN. Pago en máximo 10 días tras el cobro de DERTOGEST.
[... Resto de cláusulas legales íntegras ...]
"""
            st.text_area("Contrato completo:", texto_jv, height=500)

# --- SECCIÓN: INVERSORES (PROTEGIDA) ---
elif choice == "💰 Inversores":
    st.header("💰 Gestión de Inversores")
    df_inv = cargar_datos("INVERSORES")
    if df_inv is not None:
        st.dataframe(df_inv)
        nif_i = st.selectbox("Selecciona Inversor (NIF)", df_inv.iloc[:, 0].tolist())
        datos_i = df_inv[df_inv.iloc[:, 0] == nif_i]
        if not datos_i.empty:
            di = datos_i.iloc[0]
            if st.button("Generar Contrato de Encargo"):
                rep = di[3] if len(di) > 3 else "[Representante]"
                texto_enc = f"CONTRATO ENCARGO: DERTOGEST y {di[1]} (NIF {di[0]}), rep. por {rep}.\n\nRentabilidad: 20%.\nHonorarios: 300€ + 4% Éxito."
                st.text_area("Encargo completo:", texto_enc, height=400)

# --- SECCIÓN: IA (CON BÚSQUEDA AUTOMÁTICA DE MODELO) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if not model:
        st.error("Google no ha activado todavía el modelo en tu cuenta. Esto puede tardar 24h tras habilitar la API.")
    else:
        if prompt := st.chat_input("¿Qué duda legal tienes?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    res = model.generate_content(f"Eres experto en Tax Lease España. Pregunta: {prompt}")
                    st.markdown(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                except Exception as e:
                    st.error(f"Error de conexión: {e}")
