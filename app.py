import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE LIBRERÍAS DE IA (Con seguridad)
IA_INSTALADA = False
try:
    import google.generativeai as genai
    IA_INSTALADA = True
except ImportError:
    pass

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest AI Hub", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal & Gestión")

# 3. FUNCIÓN DE DATOS SEGURA (Limpia espacios invisibles como en image_d20bcf)
def cargar_datos(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        # Limpieza quirúrgica de columnas para evitar errores como image_d20fc9
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al conectar con la pestaña '{hoja}': {e}")
        return None

# 4. CONFIGURAR IA (Con prevención de error 404 de image_d3bfbf)
model = None
if IA_INSTALADA and "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos el nombre de modelo estándar para evitar el error 404
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.warning(f"Aviso: La IA no está disponible temporalmente ({e}). El resto de la App funcionará.")

# 5. MENÚ LATERAL (RESTAURADO)
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN 1: CALCULADORA (RESTAURADA) ---
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
        st.success(f"Inversión Óptima Sugerida: {inv_opt:,.2f} €")
        st.info(f"Ahorro Neto (20%): {inv_opt * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS (RESTAURADA Y SEGURA) ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners")
    df_p = cargar_datos("PARTNERS")
    if df_p is not None:
        st.dataframe(df_p)
        nif_sel = st.selectbox("Selecciona Partner (NIF)", df_p["NIF (ID único)"].tolist())
        d = df_p[df_p["NIF (ID único)"] == nif_sel].iloc[0]
        if st.button("Generar Borrador Contrato"):
            # Aquí ya no fallará 'Representante Legal' gracias a la limpieza previa
            st.text_area("Contrato:", f"PARTNER: {d['Nombre Partner (Razón Social)']}\nREP: {d['Representante Legal']}\nNIF: {d['NIF (ID único)']}", height=250)

# --- SECCIÓN 3: INVERSORES (RESTAURADA) ---
elif choice == "💰 Inversores":
    st.header("Gestión de Inversores")
    df_i = cargar_datos("INVERSORES")
    if df_i is not None:
        st.dataframe(df_i)

# --- SECCIÓN 4: ASESOR IA (CON SOLUCIÓN AL ERROR 404) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    if model is None:
        st.error("La IA no está configurada correctamente en los Secrets o el modelo no responde.")
    else:
        if "chat_history" not in st.session_state: st.session_state.chat_history = []
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if prompt := st.chat_input("¿En qué puedo ayudarte?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    # Contexto directo para evitar errores de versión
                    response = model.generate_content(f"Actúa como experto en Tax Lease España. Pregunta: {prompt}")
                    st.markdown(response.text)
                except Exception as e:
                    st.error(f"Error de conexión con la IA: {e}")
