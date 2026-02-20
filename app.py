import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import google.generativeai as genai

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Dertogest AI Platform", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal & Gestión")

# 2. CONEXIÓN Y LIMPIEZA QUIRÚRGICA (Solución al error de la imagen d20fc9)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    def cargar_datos(hoja):
        df = conn.read(worksheet=hoja, ttl=0)
        # Limpiamos espacios invisibles para que encuentre 'Representante Legal' siempre
        df.columns = df.columns.str.strip() 
        return df
except Exception as e:
    st.error(f"Error de conexión: {e}")

# 3. ACTIVAR CEREBRO IA (Se activa solo cuando pongas la clave en Secrets)
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    # Instrucción de sistema para que sea tu experto personal
    instrucciones = "Eres el Asesor Senior de DERTOGEST. Experto en Art. 39.7 LIS y 68.2 LIRPF en España."
    model = genai.GenerativeModel('gemini-1.5-flash', system_instruction=instrucciones)

# 4. MENÚ
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "🤖 Asesor IA Fiscal"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN PARTNERS (Sincronizada con tu imagen d20bcf) ---
if choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners")
    try:
        df = cargar_datos("PARTNERS")
        st.dataframe(df)
        
        # Mapeo exacto de tus columnas
        col_id = "NIF (ID único)"
        col_nombre = "Nombre Partner (Razón Social)"
        col_rep = "Representante Legal"
        col_dom = "Domicilio Social"

        nif_sel = st.selectbox("Selecciona Partner por NIF", df[col_id].tolist())
        d = df[df[col_id] == nif_sel].iloc[0]

        if st.button("Generar Borrador para Google Docs"):
            contrato = f"""
CONTRATO DE COLABORACIÓN (JOINT VENTURE)
---------------------------------------
PARTNER: {d[col_nombre]}
NIF: {d[col_id]}
REPRESENTANTE: {d[col_rep]}
DOMICILIO: {d[col_dom]}

CLÁUSULA DE PROTECCIÓN DE CARTERA: DERTOGEST reconoce la propiedad exclusiva de los clientes 
del Socio Comercial y se compromete a NO ofrecerles servicios ajenos al Tax Lease.
---------------------------------------
"""
            st.text_area("Copia este texto en Google Docs:", contrato, height=400)
    except Exception as e:
        st.error(f"Error: {e}")

# --- SECCIÓN ASESOR IA (El cerebro de Dertogest) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    if "GOOGLE_API_KEY" not in st.secrets:
        st.warning("Pega tu clave AIza... en los Secrets de Streamlit para activar el consultor.")
    else:
        if prompt := st.chat_input("¿Qué duda legal o comercial tienes?"):
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                respuesta = model.generate_content(prompt).text
                st.markdown(respuesta)
