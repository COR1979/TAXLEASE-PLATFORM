import streamlit as st

st.set_page_config(page_title="TaxLease Calc", layout="wide")

st.title("📊 Calculadora Fiscal TaxLease")

cuota_is = st.number_input("Cuota Íntegra IS (€)", value=100000)
facturacion = st.number_input("Facturación Anual (€)", value=25000000)

limite = 0.15 if facturacion > 20000000 else 0.50
max_deduccion = cuota_is * limite

st.metric("Deducción Máxima", f"{max_deduccion:,.2f} €")
st.write(f"Basado en un límite del {limite*100:.0f}%")
