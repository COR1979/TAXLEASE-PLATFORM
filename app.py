import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CARGA DE LIBRERÍA DE IA (Con manejo de errores)
IA_ACTIVA = False
try:
    import google.generativeai as genai
    IA_ACTIVA = True
except ImportError:
    pass

# 2. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest AI Hub v3.1", layout="wide")
st.title("🏛️ Dertogest: Gestión & Inteligencia Fiscal")

# 3. FUNCIÓN DE DATOS SEGURA (Limpia espacios invisibles en columnas)
def cargar_datos_seguros(hoja):
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        df = conn.read(worksheet=hoja, ttl=0)
        # ESCUDO: Limpia nombres de columnas para evitar fallos como en image_d20fc9
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error al conectar con la pestaña '{hoja}': {e}")
        return None

# 4. CONFIGURAR IA (Corrección para el error 404 de image_d43f9b)
model = None
if IA_ACTIVA and "GOOGLE_API_KEY" in st.secrets:
    try:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
        # Intentamos instanciar el modelo directamente
        model = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
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
        st.info(f"Ahorro Neto Directo (20%): {inv_opt * 0.20:,.2f} €")

# --- SECCIÓN 2: PARTNERS (TEXTO LEGAL ÍNTEGRO) ---
elif choice == "🤝 Partners (JV)":
    st.header("🤝 Gestión de Partners Mercantiles")
    df_p = cargar_datos_seguros("PARTNERS")
    if df_p is not None:
        st.dataframe(df_p)
        nif_sel = st.selectbox("Selecciona Partner (NIF)", df_p["NIF (ID único)"].tolist())
        d = df_p[df_p["NIF (ID único)"] == nif_sel].iloc[0]
        
        if st.button("Generar Contrato JV Profesional Íntegro"):
            # TEXTO LEGAL COMPLETO SIN RESÚMENES
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

SEXTA. CONFIDENCIALIDAD, PROPIEDAD Y NO CIRCUNVENCIÓN.
1. PROPIEDAD DE CARTERA: DERTOGEST reconoce la propiedad exclusiva de los clientes del SOCIO COMERCIAL y se compromete formalmente a NO ofrecerles servicios de asesoría general ni cualquier gestión ajena al presente contrato de Tax Lease.
2. NO CIRCUNVENCIÓN: El SOCIO COMERCIAL no contactará plataformas directamente durante la vigencia y 2 años posteriores.

SÉPTIMA. RGPD. Cumplimiento del Reglamento (UE) 2016/679.
OCTAVA. DURACIÓN. Un año prorrogable automáticamente, salvo preaviso de 30 días.
NOVENA. FIRMA DIGITAL. Formalización mediante firma digital avanzada con plena validez.
"""
            st.text_area("Contrato íntegro para copiar:", contrato_jv, height=600)

# --- SECCIÓN 3: INVERSORES (TEXTO LEGAL ÍNTEGRO + FIX IndexError) ---
elif choice == "💰 Inversores":
    st.header("💰 Gestión de Inversores")
    df_i = cargar_datos_seguros("INVERSORES")
    if df_i is not None:
        st.dataframe(df_i)
        nif_inv = st.selectbox("Selecciona Inversor (NIF)", df_i.iloc[:, 0].tolist())
        
        # SOLUCIÓN DEFINITIVA PARA image_d3da04:
        filas = df_i[df_i.iloc[:, 0] == nif_inv]
        if not filas.empty:
            di = filas.iloc[0]
            if st.button("Generar Contrato de Encargo Íntegro"):
                # Determinamos representante por posición si los nombres de columna fallan
                rep_inv = di[3] if len(di) > 3 else "[Nombre Representante]"
                contrato_inv = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS: 
De una parte, DERTOGEST, S.L. (GESTOR).
De otra parte, {di[1]}, con NIF {di[0]}, representada por D./Dña. {rep_inv} (CLIENTE).

CLÁUSULAS:
PRIMERA. OBJETO. Localización de activos con rentabilidad neta garantizada del 20% sobre aportación.
SEGUNDA. HONORARIOS. Apertura: 300 € (Netos + IVA), descontables de la factura final. Success Fee: 4% (Neto + IVA).
TERCERA. GARANTÍA. Devolución íntegra de los 300 € si no se presenta propuesta viable en el plazo pactado.
CUARTA. PAGO. Los honorarios se abonarán coincidiendo con el periodo de liquidación de impuestos (Junio/Julio).
QUINTA. RGPD. Los datos facilitados se tratarán exclusivamente para la formalización de la inversión.
SEXTA. FIRMA. El presente encargo se formaliza mediante firma digital avanzada.
"""
                st.text_area("Texto del Encargo completo:", contrato_inv, height=450)
        else:
            st.warning("Selecciona un NIF válido de la lista.")

# --- SECCIÓN 4: ASESOR IA (CORRECCIÓN 404 Y ATTRIBUTEERROR) ---
elif choice == "🤖 Asesor IA Fiscal":
    st.header("🤖 Consultor Inteligente Dertogest")
    
    # CORRECCIÓN image_d3c6e3: Aseguramos que la lista 'messages' exista siempre
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    
    if prompt := st.chat_input("Escribe tu duda legal aquí..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                # Contexto enviado directamente para mayor compatibilidad
                ctx = f"Eres el asesor legal de Dertogest. Experto en Tax Lease (Art 39.7 LIS). Pregunta: {prompt}"
                resultado = model.generate_content(ctx)
                txt_resp = resultado.text
                st.markdown(txt_resp)
                st.session_state.messages.append({"role": "assistant", "content": txt_resp})
            except Exception as e:
                # Informe de error detallado para el error 404
                st.error(f"Error de conexión con la IA de Google: {e}.")
                st.info("Sugerencia: Si el error es 404, comprueba en tu Google AI Studio que tu API Key está asociada a un proyecto con la 'Generative Language API' habilitada.")
