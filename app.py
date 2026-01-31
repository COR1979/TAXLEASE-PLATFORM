import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="Plataforma TaxLease", layout="wide", page_icon="⚖️")

# Conexión principal
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Plataforma TaxLease v2.0")

with st.sidebar:
    st.header("Navegación")
    perfil = st.radio("Ir a:", ["📊 Calculadora Fiscal", "💰 Panel Inversores", "🏢 Área Asesorías"])

if perfil == "📊 Calculadora Fiscal":
    st.header("🧮 Simulación de Ahorro Fiscal (I+D+i)")
    
    with st.form("calc_form"):
        col1, col2 = st.columns(2)
        with col1:
            cliente = st.text_input("Empresa Beneficiaria")
            facturacion = st.number_input("Facturación Anual (€)", min_value=0, step=1000000)
            import_inv = st.number_input("Inversión en el Proyecto (€)", min_value=0, step=1000)
        with col2:
            cuota_is = st.number_input("Cuota Íntegra IS Estimada (€)", min_value=1, step=1000)
            fecha = st.date_input("Fecha de Simulación")
        
        submit = st.form_submit_button("Calcular y Registrar en Excel")

    if submit:
        # --- LÓGICA LEGAL Y SEGURIDAD ---
        coef_seguridad = 0.95  # Margen del 5%
        
        # 1. Porcentaje de deducción (Regla General 25% I+D)
        porcentaje_deduc = 25
        
        # 2. Límite sobre Cuota (Salto al 50% si inversión > 10% cuota)
        if import_inv > (cuota_is * 0.10):
            limite_cuota = 50
            nota_limite = "Límite incrementado al 50% (Inversión intensiva)"
        else:
            limite_cuota = 25
            nota_limite = "Límite estándar del 25%"

        # 3. Cálculos finales
        ahorro_bruto = import_inv * (porcentaje_deduc / 100)
        ahorro_con_seguridad = ahorro_bruto * coef_seguridad
        
        # --- MOSTRAR RESULTADOS ---
        st.subheader("Análisis de la Operación")
        c1, c2, c3 = st.columns(3)
        c1.metric("Deducción Aplicada", f"{porcentaje_deduc}%")
        c2.metric("Límite s/ Cuota", f"{limite_cuota}%")
        c3.metric("Ahorro Neto (Oferta)", f"{ahorro_con_seguridad:,.2f} €", delta="-5% Seguridad")
        
        st.info(f"ℹ️ {nota_limite}")

        # --- SINCRONIZACIÓN ---
        new_data = pd.DataFrame([{
            "Fecha": str(fecha),
            "Cliente": cliente,
            "Facturación": facturacion,
            "Inversión": import_inv,
            "Ahorro Bruto": ahorro_bruto,
            "Oferta Inversor": ahorro_con_seguridad,
            "Estado": "Validando"
        }])
        
        try:
            df_actual = conn.read(worksheet="Sheet1")
            df_final = pd.concat([df_actual, new_data], ignore_index=True)
            conn.update(worksheet="Sheet1", data=df_final)
            st.balloons()
            st.success("✅ Operación registrada y sincronizada con el panel de control.")
        except Exception as e:
            st.warning("Cálculo realizado, pero no se pudo escribir en el Excel. ¿Están bien los Secrets?")

# Los otros paneles quedan como placeholders para la siguiente fase
elif perfil == "💰 Panel Inversores":
    st.header("💰 Oportunidades para Inversores")
    st.write("Próximamente: Listado de operaciones validadas listas para inversión.")

elif perfil == "🏢 Área Asesorías":
    st.header("🏢 Gestión de Despachos")
    st.write("Próximamente: Histórico de expedientes y documentación.")
