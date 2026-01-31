import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Plataforma TaxLease", layout="wide", page_icon="⚖️")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Plataforma TaxLease v2.0")

# --- SELECTOR DE PERFIL ---
perfil = st.sidebar.radio("Navegación:", ["📊 Calculadora Fiscal", "💰 Panel Inversores", "🏢 Área Asesorías"])

if perfil == "📊 Calculadora Fiscal":
    st.header("🧮 Registro de Nuevo Expediente")
    
    with st.form("form_expediente"):
        col1, col2 = st.columns(2)
        with col1:
            nombre_inv = st.text_input("Nombre del Inversor")
            nif_inv = st.text_input("NIF Inversor")
            monto = st.number_input("Importe Inversión (€)", min_value=0)
        with col2:
            nif_partner = st.text_input("NIF Partner (Asesoría)")
            fecha_op = st.date_input("Fecha Operación")
            
        btn_registrar = st.form_submit_button("Calcular y Guardar en Excel")

    if btn_registrar:
        # Lógica de cálculo (25% deducción con 5% de seguridad)
        ahorro_neto = monto * 0.25 * 0.95
        
        # Preparamos la fila respetando TUS encabezados
        nueva_fila = pd.DataFrame([{
            "ID Expediente": f"EXP-{pd.Timestamp.now().strftime('%d%m%y%H%M')}",
            "Nombre Inversor": nombre_inv,
            "NIF Inversor": nif_inv,
            "Importe Inversión": monto,
            "Estado": "Simulación",
            "NIF Partner": nif_partner,
            # Dejamos estos como 0 o fórmulas según tu necesidad
            "Provisión 300": monto * 0.03,
            "Honorarios 4": monto * 0.04
        }])

        try:
            # 1. Limpiar caché para forzar lectura fresca
            st.cache_data.clear()
            
            # 2. Leer la pestaña (con manejo de errores de nombre)
            df_actual = conn.read(worksheet="EXPEDIENTES", ttl=0)
            
            # 3. Combinar y Actualizar
            df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
            conn.update(worksheet="EXPEDIENTES", data=df_final)
            
            st.balloons()
            st.success(f"✅ ¡Hecho! El ahorro neto calculado es de {ahorro_neto:,.2f} €")
            st.info("Revisa tu pestaña EXPEDIENTES en el Excel; la fila ya debería aparecer.")
            
        except Exception as e:
            st.error(f"No se pudo escribir: {e}")
            st.warning("Prueba esto: Haz clic en el nombre de la pestaña 'EXPEDIENTES' en tu Excel y asegúrate de que no haya un espacio después de la 'S'.")

elif perfil == "💰 Panel Inversores":
    st.header("Oportunidades")
    # Aquí leeremos de la pestaña PREVISIONES próximamente
