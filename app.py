import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

# 1. CONFIGURACIÓN
st.set_page_config(page_title="Dertogest Platform v1.3", layout="wide")
st.title("🏛️ Dertogest: Gestión de Incentivos Fiscales")

# 2. CONEXIÓN
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Error de configuración: {e}")

# 3. MENÚ
menu = ["📊 Calculadora Fiscal", "🤝 Partners (JV)", "💰 Inversores"]
choice = st.sidebar.selectbox("Navegación", menu)

# --- SECCIÓN 1: CALCULADORA (Sin cambios, funciona perfecto) ---
if choice == "📊 Calculadora Fiscal":
    st.header("🧮 Simulador de Inversión")
    col1, col2 = st.columns(2)
    with col1:
        factu = st.number_input("Facturación Anual (€)", value=11200000)
        cuota = st.number_input("Cuota Íntegra IS (€)", value=102000)
    
    limite = 0.15 if factu > 20000000 else 0.50
    inv_opt = (cuota * limite) / 1.20
    st.success(f"Inversión Óptima Sugerida: {inv_opt:,.2f} €")

# --- SECCIÓN 2: PARTNERS (JV con Representante Legal) ---
elif choice == "🤝 Partners (JV)":
    st.header("Gestión de Partners")
    try:
        df = conn.read(worksheet="PARTNERS")
        st.dataframe(df)
        
        st.subheader("📝 Generar Contrato de Colaboración (JV)")
        
        # DEFINICIÓN DE COLUMNAS (Asegúrate de que coincidan con tu Excel)
        col_id = "NIF (ID único)"
        col_nombre = "Nombre Partner (Razón Social)"
        col_domicilio = "Domicilio Social"
        col_rep = "Representante Legal" # <--- Cambia este nombre si en tu Excel es distinto

        nif_sel = st.selectbox("Selecciona Partner por NIF", df[col_id].tolist())
        d = df[df[col_id] == nif_sel].iloc[0]

        if st.button("Generar Texto Legal Completo"):
            contrato_full = f"""
CONTRATO DE COLABORACIÓN MERCANTIL Y REPARTO DE BENEFICIOS (JOINT VENTURE)

REUNIDOS:
De una parte, DERTOGEST, S.L., con NIF B61009858 y domicilio en Carrer de Borriana, 1-13, Esc. C, 2º 1ª; 08030 BARCELONA, representada por D. Daniel Orozco Gambero (SOCIO TÉCNICO).

De otra parte, {d[col_nombre]}, con NIF {d[col_id]} y domicilio en {d[col_domicilio]}, representada en este acto por D./Dña. {d[col_rep]} (SOCIO COMERCIAL).

EXPONEN:
I. Que el SOCIO TÉCNICO gestiona activos de inversión fiscal (Art. 39.7 LIS).
II. Que el SOCIO COMERCIAL cuenta con una cartera de clientes para optimizar su carga tributaria.

CLÁUSULAS:
(...) [Resto de cláusulas: Objeto, Reparto 50%, No Circunvención, etc.] (...)

SEXTA. CONFIDENCIALIDAD, PROPIEDAD Y NO CIRCUNVENCIÓN.
1. PROPIEDAD DE CARTERA: DERTOGEST reconoce la propiedad exclusiva de los clientes del SOCIO COMERCIAL y se compromete a NO ofrecerles servicios ajenos al Tax Lease.
2. NO CIRCUNVENCIÓN: El Socio Comercial no contactará plataformas directamente.
(...)
"""
            st.text_area("Contrato listo para copiar:", contrato_full, height=600)
            st.download_button("📥 Descargar .txt", contrato_full, file_name=f"JV_{d[col_id]}.txt")

    except Exception as e:
        st.error(f"Error: {e}. Revisa que la columna '{col_rep}' exista en tu Excel.")

# --- SECCIÓN 3: INVERSORES (Con Representante si es Empresa) ---
elif choice == "💰 Inversores":
    st.header("Gestión de Inversores")
    try:
        df_i = conn.read(worksheet="INVERSORES")
        st.dataframe(df_i)
        
        st.subheader("📝 Generar Contrato de Encargo")
        nif_inv = st.selectbox("Selecciona Inversor por NIF", df_i.iloc[:, 0].tolist())
        di = df_i[df_i.iloc[:, 0] == nif_inv].iloc[0]

        if st.button("Generar Texto de Encargo"):
            # Aquí también incluimos al representante (asumiendo que es la columna 4 del Excel)
            rep_inv = di[3] if len(di) > 3 else "[Nombre Representante]"
            
            encargo_full = f"""
CONTRATO DE ENCARGO DE GESTIÓN E INVERSIÓN FISCAL

REUNIDOS: 
DERTOGEST, S.L. (GESTOR), representada por D. Daniel Orozco.
Y de otra parte, {di[1]}, con NIF {di[0]}, representada por D./Dña. {rep_inv} (CLIENTE).

CLÁUSULAS:
PRIMERA. OBJETO. Rentabilidad neta garantizada del 20%.
SEGUNDA. HONORARIOS. 300 € (Apertura) + 4% Success Fee (Netos + IVA).
(...)
"""
            st.text_area("Contrato de Encargo:", encargo_full, height=500)
    except Exception as e:
        st.error(f"Error: {e}")
