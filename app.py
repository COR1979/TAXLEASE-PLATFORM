import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Dertogest Platform v1.6", layout="wide")
st.title("🏛️ Dertogest: Gestión de Incentivos Fiscales")

# 2. CONEXIÓN (ttl=0 para evitar errores de caché al modificar el Excel)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de conexión: {e}")

# 3. MENÚ
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN 1: CALCULADORA ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión")
    col1, col2 = st.columns(2)
    with col1:
        factu = st.number_input("Facturación Anual (€)", value=11200000)
        cuota = st.number_input("Cuota Íntegra IS (€)", value=102000)
    
    limite = 0.15 if factu > 20000000 else 0.50
    inv_opt = (cuota * limite) / 1.20
    st.success(f"Inversión Óptima Sugerida: {inv_opt:,.2f} €")

# --- SECCIÓN 2: PARTNERS (Contrato JV Completo) ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners")
    try:
        # Leemos y limpiamos nombres de columnas para evitar KeyErrors
        df = conn.read(worksheet="PARTNERS", ttl=0)
        df.columns = df.columns.str.strip() 
        st.dataframe(df)
        
        st.subheader("📝 Generar Contrato de Colaboración (JV)")
        
        # Mapeo exacto basado en tus capturas
        col_id = "NIF (ID único)"
        col_nombre = "Nombre Partner (Razón Social)"
        col_dom = "Domicilio Social"
        col_rep = "Representante Legal" 

        nif_sel = st.selectbox("Selecciona Partner por NIF", df[col_id].tolist())
        d = df[df[col_id] == nif_sel].iloc[0]

        if st.button("Generar Texto Legal Completo"):
            contrato_full = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 y domicilio en Carrer de Borriana, 1-13, Esc. C, 2º 1ª; 08030 BARCELONA, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).

De otra parte, {d[col_nombre]}, con NIF {d[col_id]} y domicilio en {d[col_dom]}, representada en este acto por D./Dña. {d[col_rep]} (SOCIO COMERCIAL).

EXPONEN:
I. Que el SOCIO TÉCNICO cuenta con el conocimiento e infraestructura para gestionar activos de inversión fiscal basados en el Art. 39.7 de la LIS (Tax Lease).
II. Que el SOCIO COMERCIAL cuenta con una cartera de clientes susceptibles de optimizar su carga tributaria mediante dichos activos.
III. Que ambas partes desean colaborar bajo un modelo de transparencia total y beneficio compartido.

CLÁUSULAS:
PRIMERA. OBJETO. Regular la colaboración para la captación de inversores y la formalización de contratos de financiación en proyectos de I+D+i y Cultura.
SEGUNDA. DIVISIÓN DE FUNCIONES. 
- SOCIO TÉCNICO (DERTOGEST): Búsqueda, auditoría técnica y financiera, interlocución con plataformas y preparación legal.
- SOCIO COMERCIAL: Identificación de clientes, cálculo de cuota íntegra, presentación comercial y gestión de firmas.
TERCERA. MODELO ECONÓMICO Y IVA. Reparto al 50% de rendimientos brutos (Comisión de Origen, Setup y Success Fee). Importes en Base Imponible + IVA vigente.
CUARTA. TRANSPARENCIA Y LIQUIDACIÓN. Pago al SOCIO COMERCIAL en un máximo de 10 días tras el cobro por parte de DERTOGEST.
QUINTA. GARANTÍAS TÉCNICAS. Operación con Certificación oficial (ICAA, INAEM) y Póliza de Seguro de Contingencia Fiscal.

SEXTA. CONFIDENCIALIDAD, PROPIEDAD Y NO CIRCUNVENCIÓN.
1. Propiedad de Cartera: DERTOGEST reconoce la propiedad exclusiva de los clientes por parte del SOCIO COMERCIAL y se compromete formalmente a NO ofrecerles servicios de asesoría general ni cualquier gestión ajena al presente contrato de Tax Lease.
2. No Circunvención: El SOCIO COMERCIAL no contactará directamente con las plataformas presentadas por DERTOGEST durante la vigencia y 2 años posteriores.

SÉPTIMA. PROTECCIÓN DE DATOS (RGPD). Cumplimiento del Reglamento (UE) 2016/679.
OCTAVA. DURACIÓN. Un año prorrogable automáticamente, salvo preaviso de 30 días.
NOVENA. FIRMA DIGITAL. Formalización mediante firma digital avanzada con plena validez.
"""
            st.text_area("Contrato listo para copiar:", contrato_full, height=600)
            st.download_button("📥 Descargar Contrato .txt", contrato_full, file_name=f"JV_{d[col_id]}.txt")

    except Exception as e:
        st.error(f"Error: {e}")

# --- SECCIÓN 3: INVERSORES (Contrato de Encargo Completo) ---
elif choice == "💰 Inversores":
    st.header("Gestión de Inversores")
    try:
        df_i = conn.read(worksheet="INVERSORES", ttl=0)
        df_i.columns = df_i.columns.str.strip()
        st.dataframe(df_i)
        
        st.subheader("📝 Generar Contrato de Encargo")
        nif_inv = st.selectbox("Inversor (NIF)", df_i.iloc[:, 0].tolist())
        di = df_i[df_i.iloc[:, 0] == nif_inv].iloc[0]

        if st.button("Generar Texto de Encargo"):
            # Usamos índices si los nombres de columna varían en Inversores
            rep_inv = di[3] if len(di) > 3 else "[Nombre Representante]"
            
            encargo_full = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS: DERTOGEST, S.L. (GESTOR), y de otra parte, {di[1]}, con NIF {di[0]}, representada por D./Dña. {rep_inv} (CLIENTE).

CLÁUSULAS:
PRIMERA. OBJETO. Localización de activos con rentabilidad neta del 20% sobre aportación.
SEGUNDA. HONORARIOS. Apertura: 300 € (Netos + IVA), descontables de la factura final. Success Fee: 4% (Neto + IVA).
TERCERA. PAGO. Coincidiendo con liquidación de impuestos (30 junio o 25 julio).
CUARTA. GARANTÍA. Devolución de los 300 € si no se presenta propuesta viable (sin intereses).
QUINTA. PROTECCIÓN DE DATOS. Procesamiento exclusivo para formalizar la inversión.
SEXTA. FIRMA. Formalización mediante firma digital avanzada.
"""
            st.text_area("Contrato de Encargo:", encargo_full, height=500)
    except Exception as e:
        st.error(f"Error: {e}")
