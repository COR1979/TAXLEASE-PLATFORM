import streamlit as st
from st_gsheets_connection import GSheetsConnection
import pandas as pd
from datetime import datetime
import math

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Dertogest Platform | Tax Lease Management",
    page_icon="⚖️",
    layout="wide"
)

# --- CONSTANTES Y LÓGICA FINANCIERA ---
IVA = 0.21
FEE_APERTURA = 300.0
FEE_SUCCESS_RATE = 0.04
ROI_TARGET = 0.20

class TaxLeaseLogic:
    @staticmethod
    def calcular_limite_cuota(tipo_persona, facturacion_anual):
        """Calcula el límite de deducción según Art. 39.7 LIS y 68.2 LIRPF"""
        if tipo_persona == "Persona Jurídica (S.L./S.A.)":
            return 0.15 if facturacion_anual > 20_000_000 else 0.50
        else: # Persona Física
            return 0.50

    @staticmethod
    def calcular_simulacion(cuota_integra, limite_pct, meses_recuperacion):
        deduccion_maxima = cuota_integra * limite_pct
        inversion_optima = deduccion_maxima / (1 + ROI_TARGET)
        beneficio_neto = deduccion_maxima - inversion_optima
        
        # Honorarios (Base Imponible)
        h_apertura = FEE_APERTURA
        h_success = inversion_optima * FEE_SUCCESS_RATE
        total_bi = h_apertura + h_success
        total_iva = total_bi * IVA
        total_factura = total_bi + total_iva
        
        # Rentabilidad
        rentabilidad_mensual = (ROI_TARGET / meses_recuperacion)
        tae = (math.pow(1 + ROI_TARGET, 12 / meses_recuperacion) - 1)
        
        return {
            "deduccion_max": deduccion_maxima,
            "inversion": inversion_optima,
            "beneficio": beneficio_neto,
            "h_apertura": h_apertura,
            "h_success": h_success,
            "total_iva": total_iva,
            "total_factura": total_factura,
            "tae": tae
        }

# --- CONEXIÓN A DATOS ---
@st.cache_data(ttl=600)
def load_data():
    try:
        conn = st.connection("gsheets", type=GSheetsConnection)
        partners = conn.read(worksheet="PARTNERS")
        inversores = conn.read(worksheet="INVERSORES")
        return partners, inversores
    except Exception:
        # Silencioso para el usuario, devuelve DF vacíos para no romper la UI
        return pd.DataFrame(), pd.DataFrame()

# --- INTERFAZ DE USUARIO ---
def render_sidebar():
    st.sidebar.image("https://via.placeholder.com/150x50?text=DERTOGEST", use_column_width=True)
    st.sidebar.title("Navegación")
    return st.sidebar.radio("Ir a:", ["📊 Calculadora Fiscal", "🤝 Partners", "💰 Inversores"])

def render_calculator():
    st.header("📊 Calculadora de Inversión Tax Lease")
    st.info("Basado en Art. 39.7 LIS y Art. 68.2 LIRPF (Incentivos al Cine/I+D)")

    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Datos Fiscales")
        tipo = st.selectbox("Tipo de Contribuyente", ["Persona Física (IRPF)", "Persona Jurídica (S.L./S.A.)"])
        facturacion = st.number_input("Facturación Anual (€)", min_value=0.0, value=500000.0, step=10000.0)
        cuota_integra = st.number_input("Cuota Íntegra Estimada (€)", min_value=0.0, value=50000.0)
        meses = st.slider("Plazo de recuperación (Meses)", 1, 12, 6)

    limite_pct = TaxLeaseLogic.calcular_limite_cuota(tipo, facturacion)
    res = TaxLeaseLogic.calcular_simulacion(cuota_integra, limite_pct, meses)

    with col2:
        st.subheader("Resultado de la Simulación")
        metrics_col1, metrics_col2 = st.columns(2)
        metrics_col1.metric("Inversión Óptima", f"{res['inversion']:,.2f} €")
        metrics_col1.metric("Deducción Fiscal", f"{res['deduccion_max']:,.2f} €")
        metrics_col2.metric("Beneficio Neto", f"{res['beneficio']:,.2f} €", delta="20%")
        metrics_col2.metric("TAE Anualizada", f"{res['tae']:.2%}")

    with st.expander("Detalle de Costes y Honorarios"):
        st.write(f"**Límite aplicado:** {limite_pct:.0%}")
        st.write(f"**Honorarios Apertura:** {res['h_apertura']:,.2f} €")
        st.write(f"**Success Fee (4%):** {res['h_success']:,.2f} €")
        st.write(f"**IVA (21%):** {res['total_iva']:,.2f} €")
        st.divider()
        st.write(f"**TOTAL A PAGAR (Factura Dertogest): {res['total_factura']:,.2f} €**")

    # Generación de Informe TXT
    report_text = f"""
    DERTOGEST PLATFORM - RESUMEN EJECUTIVO
    Fecha: {datetime.now().strftime('%Y-%m-%d')}
    -------------------------------------------
    Tipo Contribuyente: {tipo}
    Cuota Íntegra: {cuota_integra:,.2f} €
    Límite Deducción: {limite_pct:.0%}
    
    INVERSIÓN SUGERIDA: {res['inversion']:,.2f} €
    DEDUCCIÓN A OBTENER: {res['deduccion_max']:,.2f} €
    BENEFICIO NETO: {res['beneficio']:,.2f} €
    TAE: {res['tae']:.2%}
    
    HONORARIOS TOTALES (IVA INC): {res['total_factura']:,.2f} €
    -------------------------------------------
    Cláusula RGPD: Los datos proporcionados se tratarán conforme a la LOPD GDD 3/2018
    con el fin exclusivo de realizar la simulación fiscal solicitada.
    """
    st.download_button("Descargar Resumen Ejecutivo (.txt)", report_text, file_name="simulacion_dertogest.txt")

def render_partners_view(df):
    st.header("🤝 Gestión de Partners")
    if df.empty:
        st.warning("No se pudo conectar con la base de datos de Partners.")
    else:
        st.dataframe(df, use_container_width=True)

def render_investors_view(df):
    st.header("💰 Cartera de Inversores")
    if df.empty:
        st.warning("No se pudo conectar con la base de datos de Inversores.")
    else:
        search = st.text_input("Buscar por Nombre o NIF")
        if search:
            df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        st.dataframe(df, use_container_width=True)
        
        st.subheader("Generación de Contratos")
        selected_investor = st.selectbox("Seleccionar Inversor para contrato:", df['NOMBRE'].tolist() if not df.empty else [])
        if st.button("Generar Contrato (Google Docs)"):
            st.info(f"Lógica de API de Google Docs activada para {selected_investor}. Conectando con plantilla...")
            # Aquí iría la llamada a la función de Google Docs API descrita abajo

# --- INTEGRACIÓN GOOGLE DOCS (EJEMPLO LÓGICA) ---
def push_to_google_docs(data):
    """
    Función conceptual para Google Docs API.
    Requiere google-api-python-client y credenciales en st.secrets
    """
    # 1. Autenticación (secreto 'service_account')
    # 2. docs_service.documents().get(documentId=TEMPLATE_ID).execute()
    # 3. docs_service.documents().batchUpdate(documentId=NEW_DOC_ID, body=requests).execute()
    pass

# --- MAIN ---
def main():
    selection = render_sidebar()
    partners_df, inversores_df = load_data()

    if selection == "📊 Calculadora Fiscal":
        render_calculator()
    elif selection == "🤝 Partners":
        render_partners_view(partners_df)
    elif selection == "💰 Inversores":
        render_investors_view(inversores_df)

if __name__ == "__main__":
    main()
