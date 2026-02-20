import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE IA (Con manejo de errores para que no rompa la App)
IA_READY = False
try:
    import google.generativeai as genai
    IA_READY = True
except ImportError:
    pass

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest AI Hub v2.7", layout="wide")
st.title("🏛️ Dertogest: Gestión & Inteligencia Fiscal")

# 3. FUNCIÓN DE DATOS SEGURA (Limpia espacios invisibles como en image_d20bcf)
def cargar_datos_limpios(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        # ESCUDO: Limpieza de nombres de columnas para evitar el error image_d20fc9
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al conectar con la pestaña '{hoja}': {e}")
        return None

# 4. CONFIGURAR IA (Solución al error 404 de image_d3ceda)
if IA_READY and "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Usamos el nombre de modelo más estable
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        IA_READY = False

# 5. MENÚ LATERAL
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"]
choice = st.sidebar.selectbox("Navegación Principal", menu)

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
        st.success(f"Inversión Óptima Sugerida: {inv_opt:,.2f} €")
        st.info(f"Ahorro Neto (20%): {inv_opt * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS (CONTRATO COMPLETO RECUPERADO) ---
elif choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners Mercantiles")
    df_p = cargar_datos_limpios("PARTNERS")
    if df_p is not None:
        st.dataframe(df_p)
        nif = st.selectbox("Selecciona Partner (NIF)", df_p["NIF (ID único)"].tolist())
        d = df_p[df_p["NIF (ID único)"] == nif].iloc[0]
        
        if st.button("Generar Contrato JV Profesional"):
            # RECUPERAMOS EL TEXTO LARGO
            texto_jv = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).
De otra parte, {d['Nombre Partner (Razón Social)']}, con NIF {d['NIF (ID único)']} y domicilio en {d['Domicilio Social']}, representada por D./Dña. {d['Representante Legal']} (SOCIO COMERCIAL).

CLÁUSULAS DESTACADAS:
PRIMERA. OBJETO. Gestión de inversiones bajo el Art. 39.7 de la LIS.
SEGUNDA. REPARTO ECONÓMICO. 50% de rendimientos brutos sobre Base Imponible (+ IVA).
TERCERA. PROTECCIÓN DE CARTERA: DERTOGEST reconoce la propiedad exclusiva de los clientes del Socio Comercial y se compromete a NO ofrecerles servicios ajenos al Tax Lease.
CUARTA. LIQUIDACIÓN. Pago en máximo 10 días tras el cobro efectivo por DERTOGEST.
"""
            st.text_area("Copia este borrador para Google Docs:", texto_jv, height=450)

# --- SECCIÓN 3: INVERSORES (CONTRATO DE ENCARGO RECUPERADO) ---
elif choice == "💰 Inversores":
    st.header("💰 Gestión de Clientes Inversores")
    df_i = cargar_datos_limpios("INVERSORES")
    if df_i is not None:
        st.dataframe(df_i)
        nif_inv = st.selectbox("Selecciona Inversor por NIF", df_i.iloc[:, 0].tolist())
        di = df_i[df_i.iloc[:, 0] == nif_inv].iloc[0]

        if st.button("Generar Contrato de Encargo"):
            # Buscamos al representante (asumiendo columna 4 si no hay nombre)
            rep_inv = di[3] if len(di) > 3 else "[Representante]"
            texto_enc = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS: DERTOGEST, S.L. y {di[1]}, con NIF {di[0]}, representada por D./Dña. {rep_inv} (CLIENTE).

CLÁUSULAS:
1. Rentabilidad neta garantizada del 20% sobre aportación.
2. Honorarios: 300 € (Apertura) + 4% Éxito (Netos + IVA).
3. Garantía de devolución de los 300 € si no hay propuesta viable.
"""
            st.text_area("Borrador del Encargo:", texto_enc, height=350)

# --- SECCIÓN 4: ASESOR IA (FIXED: Attribute & 404 Errors) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    
    # CORRECCIÓN DE image_d3c6e3: Inicializar siempre 'messages'
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("¿Qué duda legal o comercial tienes?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                # Contexto enviado directamente para evitar fallos de versión
                ctx = f"Eres el experto en Tax Lease de Dertogest (Art 39.7 LIS). Pregunta: {prompt}"
                resultado = model.generate_content(ctx)
                st.markdown(resultado.text)
                st.session_state.messages.append({"role": "assistant", "content": resultado.text})
            except Exception as e:
                st.error(f"Error en la conexión con Google: {e}. Revisa si la API Key es válida.")
