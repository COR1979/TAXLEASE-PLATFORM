import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Plataforma TaxLease", layout="wide", page_icon="⚖️")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Plataforma TaxLease v2.0")

perfil = st.sidebar.radio("Navegación:", ["📊 Calculadora Fiscal", "💰 Panel Inversores", "🏢 Área Asesorías"])

if perfil == "📊 Calculadora Fiscal":
    st.header("🧮 Registro de Nuevo Expediente")
    
    with st.form("form_expediente"):
        col1, col2 = st.columns(2)
        with col1:
            nombre_inv = st.text_input("Nombre del Inversor")
            nif_inv = st.text_input("NIF Inversor")
            monto = st.number_input("Importe Inversión (€)", min_value=0, step=1000)
            facturacion = st.number_input("Facturación Anual Empresa (€)", min_value=0, step=10000)
        with col2:
            cuota_is = st.number_input("Cuota Íntegra IS Estimada (€)", min_value=1, step=1000)
            nif_partner = st.text_input("NIF Partner (Asesoría)")
            fecha_op = st.date_input("Fecha Operación")
            
        btn_registrar = st.form_submit_button("Calcular y Guardar en EXPEDIENTES")

    if btn_registrar:
        # --- LÓGICA FISCAL CON SEGURIDAD ---
        # 1. Porcentaje base deducción
        porcentaje_deduc = 25
        # 2. Límite sobre cuota (Regla del 10%)
        limite_cuota = 50 if monto > (cuota_is * 0.10) else 25
        # 3. Cálculo con 5% de seguridad
        ahorro_neto = (monto * (porcentaje_deduc/100)) * 0.95
        
        # --- MOSTRAR RESULTADOS ---
        st.subheader("Análisis de la Operación")
        c1, c2, c3 = st.columns(3)
        c1.metric("Límite s/ Cuota", f"{limite_cuota}%")
        c2.metric("Ahorro Neto (Oferta)", f"{ahorro_neto:,.2f} €", delta="-5% Seguridad")
        c3.metric("Disponible Fiscal", f"{ahorro_neto:,.2f} €")

        # --- MAPEO A TU EXCEL (EXPEDIENTES) ---
        nueva_fila = pd.DataFrame([{
            "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%d%m%y%H%M')}",
            "Nombre Inversor": nombre_inv,
            "NIF Inversor": nif_inv,
            "Importe Inversión": monto,
            "Provisión 300": monto * 0.03,
            "Honorarios 4": monto * 0.04,
            "Estado": "Simulación",
            "NIF Partner": nif_partner
        }])

        try:
            st.cache_data.clear()
            df_actual = conn.read(worksheet="EXPEDIENTES", ttl=0)
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="EXPEDIENTES", data=df_final)
            st.balloons()
            st.success("✅ Datos integrados en la pestaña EXPEDIENTES.")
        except Exception as e:
            st.error(f"Error de sincronización: {e}")

elif perfil == "💰 Panel Inversores":
    st.header("Oportunidades")
    st.write("Cargando datos desde PREVISIONES...")
