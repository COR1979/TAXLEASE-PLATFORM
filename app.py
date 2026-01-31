import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="TaxLease Optimización", layout="wide")
conn = st.connection("gsheets", type=GSheetsConnection)

st.title("🏛️ Optimizador de Inversión TaxLease")

# --- ANÁLISIS DE CAPACIDAD ---
st.header("🔍 1. Perfil Fiscal y Cálculo de Óptimos")
col1, col2 = st.columns(2)

with col1:
    facturacion = st.number_input("Facturación Anual de la Empresa (€)", min_value=0, value=25000000, step=100000)
    cuota_is = st.number_input("Cuota Íntegra IS del Cliente (€)", min_value=0, value=36000, step=1000)
    
    # LÓGICA DE GRAN EMPRESA
    es_gran_empresa = facturacion > 20000000
    # Ajustamos el porcentaje de deducción según facturación
    pct_deduccion = 0.15 if es_gran_empresa else 0.25
    
    tipo_txt = "🏢 Gran Empresa (>20M€)" if es_gran_empresa else "🏭 Pyme / Resto"
    st.warning(f"Tipo de Entidad: **{tipo_txt}** | Deducción aplicada: **{pct_deduccion*100:.0f}%**")

# Definimos los techos sobre la cuota (25% o 50% de la cuota íntegra)
techo_std = cuota_is * 0.25
techo_intensivo = cuota_is * 0.50

# Inversión necesaria: (Inv * (1 + Rentabilidad)) = Techo
# Aquí la rentabilidad del 20% se mantiene, pero la base es el pct_deduccion
inv_optima_std = techo_std / (1 + 0.20)
inv_optima_int = techo_intensivo / (1 + 0.20)

with col2:
    st.subheader(f"Capacidad de Inversión (Límite {pct_deduccion*100:.0f}%)")
    st.write(f"✅ **Escenario 25% Cuota:** Inversión de **{inv_optima_std:,.2f} €**")
    st.write(f"🚀 **Escenario 50% Cuota:** Inversión de **{inv_optima_int:,.2f} €**")
    st.caption("Fórmula: Inversión + 20% rentabilidad = Deducción total aplicada.")

st.divider()

# --- REGISTRO ---
# (El resto del código de registro se mantiene igual, usando pct_deduccion para validar)
