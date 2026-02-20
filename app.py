import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Dertogest Platform v1.4", layout="wide")
st.title("🏛️ Dertogest: Gestión de Incentivos Fiscales")

# 2. CONEXIÓN A GOOGLE SHEETS
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de conexión: {e}")

# 3. MENÚ LATERAL
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN 1: CALCULADORA (Lógica fiscal 15%/50%) ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión y Rentabilidad")
    col1, col2 = st.columns(2)
    with col1:
        facturacion = st.number_input("Facturación Anual (€)", value=11200000)
        cuota_is = st.number_input("Cuota Íntegra IS (€)", value=102000)
        meses_recup = st.slider("Plazo de recuperación (Meses)", 1, 12, 6)
    
    # Lógica de límites fiscales en España
    limite = 0.15 if facturacion > 20000000 else 0.50
    capacidad_max = cuota_is * limite
    inv_optima = capacidad_max / 1.20

    with col2:
        st.metric("Límite de Deducción", f"{limite*100:.0f}%", "s/ Art. 39.7 LIS")
        st.success(f"Inversión Óptima Sugerida: {inv_optima:,.2f} €")
    
    st.divider()
    inv_real = st.number_input("Inversión Real Propuesta (€)", value=float(inv_optima))
    ahorro_neto = inv_real * 0.20
    
    m1, m2 = st.columns(2)
    m1.metric("Ahorro Neto (Beneficio)", f"{ahorro_neto:,.2f} €", "20% fijo")
    m2.metric("TAE Anualizada", f"{(20/meses_recup)*12:.2f} %")

# --- SECCIÓN 2: PARTNERS (Contrato JV Completo) ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners Mercantiles")
    try:
        df = conn.read(worksheet="PARTNERS")
        st.dataframe(df)
        
        st.subheader("📝 Redactar Contrato de Colaboración (JV)")
        
        # Mapeo de columnas según tu Excel (AJUSTA SI CAMBIAN LOS NOMBRES)
        col_nif = "NIF (ID único)"
        col_razon = "Nombre Partner (Razón Social)"
        col_domicilio = "Domicilio Social"
        col_rep = "Nombre del Representante" # <--- Asegúrate que este nombre es exacto en tu Excel

        nif_sel = st.selectbox("Selecciona Partner por NIF:", df[col_nif].tolist())
        d = df[df[col_nif] == nif_sel].iloc[0]

        if st.button("Generar Contrato Legal JV"):
            texto_jv = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 y domicilio en Carrer de Borriana, 1-13, Esc. C, 2º 1ª; 08030 BARCELONA, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).

De otra parte, {d[col_razon]}, con NIF {d[col_nif]} y domicilio en {d[col_domicilio]}, representada en este acto por D./Dña. {d[col_rep]} (SOCIO COMERCIAL).

EXPONEN:
I. Que el SOCIO TÉCNICO cuenta con el conocimiento para gestionar activos de inversión fiscal (Tax Lease).
II. Que el SOCIO COMERCIAL cuenta con una cartera de clientes para optimizar su carga tributaria.

CLÁUSULAS:
PRIMERA. OBJETO. Gestión de inversiones bajo el Art. 39.7 de la LIS.
SEGUNDA. FUNCIONES. DERTOGEST asume la auditoría y cierre; el SOCIO COMERCIAL la captación y firma.
TERCERA. REPARTO ECONÓMICO. 50% de rendimientos brutos sobre Base Imponible (+ IVA).
CUARTA. LIQUIDACIÓN. Pago en máximo 10 días tras el cobro efectivo por DERTOGEST.
QUINTA. GARANTÍAS. Certificación oficial (ICAA/INAEM) y Seguro de Contingencia Fiscal.

SEXTA. CONFIDENCIALIDAD Y PROPIEDAD DE CARTERA.
1. PROPIEDAD: DERTOGEST reconoce la propiedad exclusiva de los clientes del SOCIO COMERCIAL y se compromete a NO ofrecerles servicios de asesoría ni gestiones ajenas al Tax Lease.
2. NO CIRCUNVENCIÓN: El Socio Comercial no contactará plataformas directamente (2 años).

SÉPTIMA. RGPD. Cumplimiento del Reglamento (UE) 2016/679.
OCTAVA. FIRMA DIGITAL. Validez mediante firma digital avanzada.
"""
            st.text_area("Contrato listo para copiar:", texto_jv, height=600)
            st.download_button("📥 Descargar .txt", texto_jv, file_name=f"Contrato_JV_{nif_sel}.txt")

    except Exception as e:
        st.error(f"Error: No se encuentra la columna en el Excel. Detalles: {e}")

# --- SECCIÓN 3: INVERSORES (Contrato de Encargo) ---
elif choice == "💰 Inversores":
    st.header("Gestión de Clientes Inversores")
    try:
        df_i = conn.read(worksheet="INVERSORES")
        st.dataframe(df_i)
        
        st.subheader("📝 Redactar Contrato de Encargo")
        nif_inv = st.selectbox("Inversor (NIF):", df_i.iloc[:, 0].tolist())
        di = df_i[df_i.iloc[:, 0] == nif_inv].iloc[0]

        if st.button("Generar Contrato Inversor"):
            # Asumiendo que el representante es la columna 4 del Excel de Inversores
            rep_inv = di[3] if len(di) > 3 else "[Nombre Representante]"
            
            texto_inv = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS: DERTOGEST, S.L. (GESTOR), y de otra parte {di[1]}, con NIF {di[0]}, representada por D./Dña. {rep_inv} (CLIENTE).

CLÁUSULAS:
PRIMERA. OBJETO. Localización de activos con rentabilidad neta del 20%.
SEGUNDA. HONORARIOS. 300 € (Apertura) + 4% Success Fee (Base Imponible + IVA).
TERCERA. GARANTÍA. Devolución de los 300 € si no se presenta propuesta viable.
CUARTA. PAGO. En el periodo de liquidación del Impuesto de Sociedades o IRPF.
"""
            st.text_area("Texto del Encargo:", texto_inv, height=450)
    except Exception as e:
        st.error(f"Error en pestaña Inversores: {e}")
