import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="TaxLease Platform v4.0", layout="wide")

st.title("🏛️ TaxLease Platform-Manager")

# --- MENÚ LATERAL ---
menu = ["📊 Calculadora Fiscal", "🤝 Partners", "💰 Inversores", "🚀 Nueva Operación"]
choice = st.sidebar.selectbox("Menú de Gestión", menu)

# ==========================================
# SECCIÓN: CALCULADORA DE AHORRO FISCAL
# ==========================================
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Calculadora de Impacto Fiscal (Tax Lease)")
    st.info("Utiliza esta herramienta para determinar la inversión óptima de un cliente.")

    # --- ENTRADA DE DATOS ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Datos del Cliente")
        facturacion = st.number_input("Facturación Anual de la Empresa (€)", min_value=0, value=25000000, step=1000000)
        cuota_is_inicial = st.number_input("Cuota Íntegra IS Inicial (€)", min_value=0, value=100000, step=10000)
        
        # Lógica de Límites Fiscales
        es_gran_empresa = facturacion > 20000000
        limite_pct = 0.15 if es_gran_empresa else 0.50
        tipo_empresa = "Grande Empresa (>20M€)" if es_gran_empresa else "Pyme / Resto"

    # --- CÁLCULOS INTERNOS ---
    max_deduccion_posible = cuota_is_inicial * limite_pct
    # Inversión Óptima para agotar el cupo (Rentabilidad 20% fija)
    inv_optima = max_deduccion_posible / 1.20
    rentabilidad_esperada = inv_optima * 0.20

    with col2:
        st.subheader("Diagnóstico de Capacidad")
        st.write(f"**Perfil:** {tipo_empresa}")
        st.write(f"**Límite Legal:** {limite_pct*100:.0f}% de la cuota íntegra.")
        
        st.metric("Deducción Máxima", f"{max_deduccion_posible:,.2f} €")
        st.success(f"🎯 **Inversión Óptima Sugerida:** {inv_optima:,.2f} €")

    st.divider()

    # --- SIMULADOR DE IMPACTO ---
    st.subheader("📉 Simulador de Impacto Final")
    
    # Slider para que el usuario pueda ajustar el importe real que el cliente quiere invertir
    monto_final = st.slider("Ajustar Inversión Real (€)", 0.0, float(inv_optima * 1.5), float(inv_optima))
    
    # Resultados del simulador
    deduccion_generada = monto_final * 1.20
    ahorro_neto_cliente = monto_final * 0.20
    cuota_final_pagar = cuota_is_inicial - deduccion_generada

    # Asegurar que la cuota no sea negativa (solo a efectos visuales)
    cuota_final_pagar = max(0.0, cuota_final_pagar)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Deducción Generada", f"{deduccion_generada:,.2f} €")
    with c2:
        st.metric("Ahorro Neto (Beneficio)", f"{ahorro_neto_cliente:,.2f} €", delta="20% neto")
    with c3:
        st.metric("Nueva Cuota a Pagar", f"{cuota_final_pagar:,.2f} €", delta=f"-{deduccion_generada:,.2f} €", delta_color="normal")

    # --- MENSAJE COMERCIAL ---
    if cuota_final_pagar < (cuota_is_inicial * 0.5):
        st.warning("⚠️ Atención: La inversión supera el límite estándar de deducción. Revisar con fiscalista.")

# ==========================================
# RESTO DE SECCIONES (Partners, Inversores...)
# ==========================================
elif choice == "🤝 Partners":
    st.header("Gestión de Partners")
    st.write("Consulta tus datos directamente en el Excel.")
    # (Aquí va tu código de visualización de Partners)
