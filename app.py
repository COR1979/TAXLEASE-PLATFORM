import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE IA (Detección Automática de Modelo)
IA_ACTIVA = False
model = None
try:
    import google.generativeai as genai
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # BUSCADOR DE MODELO: Buscamos qué Gemini tienes activo (Flash 1.5 o 3)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        if available_models:
            # Seleccionamos el primero disponible (el más moderno)
            model_name = available_models[0]
            model = genai.GenerativeModel(model_name)
            IA_ACTIVA = True
except Exception:
    IA_ACTIVA = False

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest AI Hub v7.0", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal & Gestión")

# 3. FUNCIÓN DE DATOS SEGURA
def cargar_datos_limpios(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        df.columns = df.columns.str.strip() # Limpia espacios invisibles
        return df
    except Exception as e:
        st.error(f"Error en pestaña {hoja}: {e}")
        return None

# 4. MENÚ LATERAL (Estable y Permanente)
st.sidebar.title("Herramientas")
choice = st.sidebar.selectbox("Selecciona:", 
                             ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"])

# --- SECCIÓN 1: CALCULADORA ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión Tax Lease")
    c1, c2 = st.columns(2)
    with c1:
        f = st.number_input("Facturación Anual (€)", value=11200000)
        i = st.number_input("Cuota Íntegra IS (€)", value=102000)
    limite = 0.15 if f > 20000000 else 0.50
    inv_opt = (i * limite) / 1.20
    with c2:
        st.metric("Límite Fiscal", f"{limite*100:.0f}%")
        st.success(f"Inversión Óptima Sugerida: {inv_opt:,.2f} €")
        st.info(f"Ahorro Neto Directo (20%): {inv_opt * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS (CONTRATO ÍNTEGRO PALABRA POR PALABRA) ---
elif choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners Mercantiles")
    df_p = cargar_datos_limpios("PARTNERS")
    if df_p is not None:
        st.dataframe(df_p)
        nif_sel = st.selectbox("Selecciona Partner (NIF)", df_p["NIF (ID único)"].tolist())
        d = df_p[df_p["NIF (ID único)"] == nif_sel].iloc[0]
        
        if st.button("Generar Contrato JV"):
            contrato_jv = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 y domicilio en Carrer de Borriana, 1-13, Esc. C, 2º 1ª; 08030 BARCELONA, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).

De otra parte, {d['Nombre Partner (Razón Social)']}, con NIF {d['NIF (ID único)']} y domicilio en {d['Domicilio Social']}, representada en este acto por D./Dña. {d['Representante Legal']} (SOCIO COMERCIAL).

EXPONEN:
I. Que el SOCIO TÉCNICO gestiona activos de inversión fiscal basados en el Art. 39.7 de la LIS (Tax Lease).
II. Que el SOCIO COMERCIAL cuenta con una cartera de clientes para optimizar su carga tributaria mediante dichos activos.
III. Que ambas partes desean colaborar bajo un modelo de transparencia total y beneficio compartido.

CLÁUSULAS:
PRIMERA. OBJETO. Regular la colaboración para la captación de inversores y la formalización de contratos de financiación en proyectos de I+D+i y Cultura.
SEGUNDA. DIVISIÓN DE FUNCIONES. DERTOGEST asume la búsqueda, auditoría técnica y financiera; el SOCIO COMERCIAL asume la identificación de clientes y gestión comercial.
TERCERA. MODELO ECONÓMICO Y IVA. Reparto al 50% de rendimientos brutos (Comisión de Origen, Setup y Success Fee). Importes en Base Imponible + IVA vigente.
CUARTA. TRANSPARENCIA Y LIQUIDACIÓN. Pago al SOCIO COMERCIAL en un máximo de 10 días tras el cobro efectivo por parte de DERTOGEST.
QUINTA. GARANTÍAS TÉCNICAS. Operación bajo Certificación oficial (ICAA, INAEM) y Póliza de Seguro de Contingencia Fiscal.
SEXTA. CONFIDENCIALIDAD Y PROTECCIÓN DE CARTERA. DERTOGEST reconoce la propiedad exclusiva de los clientes del SOCIO COMERCIAL y se compromete formalmente a NO ofrecerles servicios de asesoría general ni cualquier gestión ajena al presente contrato de Tax Lease.
SÉPTIMA. NO CIRCUNVENCIÓN. El SOCIO COMERCIAL no contactará plataformas directamente durante la vigencia y 2 años posteriores.
OCTAVA. RGPD. Cumplimiento del Reglamento (UE) 2016/679.
NOVENA. DURACIÓN Y FIRMA. Un año prorrogable automáticamente. Formalización mediante firma avanzada.
"""
            st.text_area("Copia el contrato completo:", contrato_jv, height=600)

# --- SECCIÓN 3: INVERSORES (CONTRATO ÍNTEGRO) ---
elif choice == "💰 Inversores":
    st.header("💰 Gestión de Inversores")
    df_i = cargar_datos_limpios("INVERSORES")
    if df_i is not None:
        st.dataframe(df_i)
        nif_inv = st.selectbox("Inversor (NIF)", df_i.iloc[:, 0].tolist())
        filas = df_i[df_i.iloc[:, 0] == nif_inv]
        if not filas.empty:
            di = filas.iloc[0]
            if st.button("Generar Encargo"):
                rep_inv = di[3] if len(di) > 3 else "[Representante]"
                contrato_inv = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS: DERTOGEST, S.L. (GESTOR) y {di[1]}, con NIF {di[0]}, representada por D./Dña. {rep_inv} (CLIENTE).

CLÁUSULAS:
1. OBJETO. Localización de activos con rentabilidad neta garantizada del 20% sobre aportación.
2. HONORARIOS. Apertura: 300 € (Netos + IVA), descontables de la factura final. Success Fee: 4% (Neto + IVA).
3. GARANTÍA. Devolución íntegra de los 300 € si no se presenta propuesta viable en el plazo pactado.
4. PAGO. Los honorarios se abonarán coincidiendo con el periodo de liquidación de impuestos (Junio/Julio).
"""
                st.text_area("Encargo completo:", contrato_inv, height=450)

# --- SECCIÓN 4: ASESOR IA (SIN ERROR 404) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if not model:
        st.error("No se detectó ningún modelo de Gemini disponible para tu API Key.")
    else:
        if prompt := st.chat_input("¿Qué duda legal tienes?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    res = model.generate_content(f"Eres experto legal de Dertogest en Tax Lease España. Pregunta: {prompt}")
                    st.markdown(res.text)
                    st.session_state.messages.append({"role": "assistant", "content": res.text})
                except Exception as e:
                    st.error(f"Error: {e}")
