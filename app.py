# --- LÓGICA MEJORADA ---

st.header("🧮 Simulador de Inversión Tax Lease")

# 1. CÁLCULO DE CAPACIDAD (Límite Legal)
st.subheader("Paso 1: Capacidad Fiscal del Cliente")
col_cap1, col_cap2 = st.columns(2)

with col_cap1:
    cuota_is = st.number_input("Cuota Íntegra IS (€)", value=100000)
    facturacion = st.number_input("Facturación Anual (€)", value=25000000)
    
    limite_pct = 0.15 if facturacion > 20000000 else 0.50
    capacidad_deduccion = cuota_is * limite_pct
    # Inversión necesaria para agotar ese límite
    inv_maxima_legal = capacidad_deduccion / 1.20

with col_cap2:
    st.info(f"**Límite Legal:** {limite_pct*100:.0f}% de la cuota.")
    st.metric("Deducción Máxima posible", f"{capacidad_deduccion:,.2f} €")
    st.success(f"Techo de Inversión: {inv_maxima_legal:,.2f} €")

st.divider()

# 2. INTRODUCCIÓN DE LA PROPUESTA (Lo que realmente se va a firmar)
st.subheader("Paso 2: Inversión Propuesta")
inv_propuesta = st.number_input("Introduce el importe de la Propuesta Real (€)", 
                                min_value=0.0, 
                                max_value=float(inv_maxima_legal * 2), # Permitimos superar el límite para avisar
                                value=float(inv_maxima_legal))

# 3. RESULTADO REAL DE LA PROPUESTA
st.subheader("Paso 3: Resultado de la Operación")

deduccion_real = inv_propuesta * 1.20
ahorro_neto = inv_propuesta * 0.20
exceso_limite = max(0.0, deduccion_real - capacidad_deduccion)

c1, c2, c3 = st.columns(3)
c1.metric("Deducción Generada", f"{deduccion_real:,.2f} €")
c2.metric("Ahorro Neto (Beneficio)", f"{ahorro_neto:,.2f} €")

if exceso_limite > 0:
    c3.metric("⚠️ Exceso no deducible", f"{exceso_limite:,.2f} €", delta_color="inverse")
    st.error(f"Ojo: La propuesta supera la capacidad fiscal del cliente en {exceso_limite:,.2f} €. Tendrá que aplicar el exceso en años siguientes.")
else:
    c3.metric("Cuota IS Final", f"{cuota_is - deduccion_real:,.2f} €")
    st.balloons()
