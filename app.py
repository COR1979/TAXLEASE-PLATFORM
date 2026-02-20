import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE LIBRERÍAS DE IA
IA_ACTIVA = False
try:
    import google.generativeai as genai
    IA_ACTIVA = True
except ImportError:
    pass

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest AI Platform v2.8", layout="wide")
st.title("🏛️ Dertogest: Inteligencia Fiscal & Gestión")

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

# 4. CONFIGURAR IA (Corrección para el error 404 de image_d3bfbf)
model = None
if IA_ACTIVA and "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Intentamos con la versión más compatible del modelo
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        IA_ACTIVA = False

# 5. MENÚ LATERAL
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores", "🤖 Asesor IA Fiscal"]
choice = st.sidebar.selectbox("Navegación", menu)

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

# --- SECCIÓN 2: PARTNERS (TEXTO ÍNTEGRO DEL CONTRATO JV) ---
elif choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners Mercantiles")
    df_p = cargar_datos_limpios("PARTNERS")
    if df_p is not None:
        st.dataframe(df_p)
        nif_sel = st.selectbox("Selecciona Partner (NIF)", df_p["NIF (ID único)"].tolist())
        d = df_p[df_p["NIF (ID único)"] == nif_sel].iloc[0]
        
        if st.button("Generar Contrato JV Profesional"):
            # TEXTO COMPLETO SEGÚN TU SOLICITUD
            contrato_full = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 y domicilio en Carrer de Borriana, 1-13, Esc. C, 2º 1ª; 08030 BARCELONA, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).

De otra parte, {d['Nombre Partner (Razón Social)']}, con NIF {d['NIF (ID único)']} y domicilio en {d['Domicilio Social']}, representada en este acto por D./Dña. {d['Representante Legal']} (SOCIO COMERCIAL).

EXPONEN:
I. Que el SOCIO TÉCNICO gestiona activos de inversión fiscal (Art. 39.7 LIS).
II. Que el SOCIO COMERCIAL cuenta con una cartera de clientes para optimizar su carga tributaria.
III. Que ambas partes desean colaborar bajo un modelo de beneficio compartido.

CLÁUSULAS:
PRIMERA. OBJETO. Regular la colaboración para captación de inversores y formalización de contratos Tax Lease.
SEGUNDA. DIVISIÓN DE FUNCIONES. DERTOGEST asume la parte técnica y financiera; el SOCIO COMERCIAL la identificación y gestión comercial.
TERCERA. MODELO ECONÓMICO. Reparto al 50% de rendimientos brutos sobre Base Imponible (+ IVA vigente).
CUARTA. TRANSPARENCIA Y LIQUIDACIÓN. Pago al SOCIO COMERCIAL en máximo 10 días tras el cobro por DERTOGEST.
QUINTA. GARANTÍAS TÉCNICAS. Operación con Certificación oficial (ICAA, INAEM) y Póliza de Seguro de Contingencia Fiscal.

SEXTA. CONFIDENCIALIDAD, PROPIEDAD Y NO CIRCUNVENCIÓN.
1. PROPIEDAD DE CARTERA: DERTOGEST reconoce la propiedad exclusiva de los clientes del SOCIO COMERCIAL y se compromete formalmente a NO ofrecerles servicios de asesoría general ni gestiones ajenas al presente contrato de Tax Lease.
2. NO CIRCUNVENCIÓN: El SOCIO COMERCIAL no contactará plataformas directamente durante la vigencia y 2 años posteriores.

SÉPTIMA. RGPD. Cumplimiento del Reglamento (UE) 2016/679.
OCTAVA. DURACIÓN. Un año prorrogable automáticamente.
NOVENA. FIRMA DIGITAL. Formalización mediante firma digital avanzada.
"""
            st.text_area("Contrato listo para Google Docs:", contrato_full, height=600)

# --- SECCIÓN 3: INVERSORES (CORRECCIÓN DE INDEXERROR image_d3da04) ---
elif choice == "💰 Inversores":
    st.header("💰 Gestión de Inversores")
    df_i = cargar_datos_limpios("INVERSORES")
    if df_i is not None:
        st.dataframe(df_i)
        nif_inv = st.selectbox("Inversor (NIF)", df_i.iloc[:, 0].tolist())
        
        # Corrección del IndexError: comprobamos que la fila existe antes de acceder
        filas_filtradas = df_i[df_i.iloc[:, 0] == nif_inv]
        if not filas_filtradas.empty:
            di = filas_filtradas.iloc[0]
            if st.button("Generar Contrato de Encargo"):
                rep_inv = di[3] if len(di) > 3 else "[Representante]"
                contrato_inv = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS: DERTOGEST, S.L. (GESTOR) y {di[1]}, con NIF {di[0]}, representada por D./Dña. {rep_inv} (CLIENTE).

CLÁUSULAS:
1. OBJETO. Localización de activos con rentabilidad neta del 20%.
2. HONORARIOS. 300 € (Apertura) + 4% Éxito (Netos + IVA). Los 300€ se descuentan del pago final.
3. GARANTÍA. Devolución de los 300 € si no se presenta propuesta viable.
4. PAGO. En el periodo de liquidación de impuestos (Junio/Julio).
"""
                st.text_area("Texto del Encargo:", contrato_inv, height=400)

# --- SECCIÓN 4: ASESOR IA (CORRECCIÓN DE ERROR 404 image_d3dd86) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("¿Qué duda legal tienes?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                # Contexto directo para evitar errores de configuración de versión
                ctx = f"Eres el experto en Tax Lease de Dertogest (Art 39.7 LIS). Pregunta: {prompt}"
                resultado = model.generate_content(ctx)
                st.markdown(resultado.text)
                st.session_state.messages.append({"role": "assistant", "content": resultado.text})
            except Exception as e:
                st.error(f"Error en la conexión con la IA de Google: {e}. Intenta refrescar o verifica tu API Key.")
