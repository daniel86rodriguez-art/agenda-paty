import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials
import json

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Agenda de Paty", page_icon="📅")

# --- CONEXIÓN A GOOGLE SHEETS ---
@st.cache_resource
def conectar_sheets():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    # Leemos la llave secreta desde la caja fuerte de Streamlit
    credenciales_diccionario = json.loads(st.secrets["llave_secreta"])
    creds = Credentials.from_service_account_info(credenciales_diccionario, scopes=scopes)
    client = gspread.authorize(creds)
    
    sheet_url = "https://docs.google.com/spreadsheets/d/1KWlpEpHWvypDY6jljzrNaT2u4Xwy59Vqx0cYCTF0cSg/edit?gid=0#gid=0"
    return client.open_by_url(sheet_url).sheet1

# AHORA SÍ, LA VARIABLE ESTÁ AFUERA Y VISIBLE
hoja_citas = conectar_sheets()

# --- INTERFAZ PRINCIPAL ---
st.title("📅 Agenda de Citas de Paty")
st.write("Registra y consulta las citas del día. Los datos se sincronizan con la nube. ☁️")

# --- SECCIÓN DE REGISTRO ---
with st.expander("➕ Registrar Nueva Cita", expanded=True):
    with st.form("cita_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            cliente = st.text_input("Nombre del Cliente")
            servicio = st.selectbox("Servicio", ["Consulta", "Seguimiento", "Tratamiento", "Otro"])
        
        with col2:
            fecha = st.date_input("Fecha", datetime.now())
            hora = st.time_input("Hora", datetime.now())
        
            notas = st.text_area("Notas adicionales")
        
        submit = st.form_submit_button("Guardar Cita en la Nube")

# --- LÓGICA PARA GUARDAR EN SHEETS ---
if submit:
    if cliente:
        fecha_str = fecha.strftime("%d/%m/%Y")
        hora_str = hora.strftime("%H:%M")
        
        nueva_fila = [cliente, servicio, fecha_str, hora_str, notas]
        hoja_citas.append_row(nueva_fila)
        
        st.success(f"✅ ¡Listo! La cita de {cliente} se guardó en Google Sheets.")
    else:
        st.warning("⚠️ Por favor, ingresa el nombre del cliente.")

# --- SECCIÓN DE CONSULTA ---
st.divider()
st.subheader("📋 Historial de Citas")

try:
    datos = hoja_citas.get_all_records()
    if datos:
        df = pd.DataFrame(datos)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No hay citas registradas en el archivo por ahora.")
except Exception as e:
    st.error("No pudimos cargar la tabla. Asegúrate de tener los encabezados (Cliente, Servicio, etc.) en la primera fila del Excel.")
