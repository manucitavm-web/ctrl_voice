import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import json
import paho.mqtt.client as paho

# --- CONFIGURACIÓN ESTÉTICA ---
st.set_page_config(
    page_title="Voice IoT Controller",
    page_icon="🎙️",
    layout="wide"
)

# Estilo CSS para mejorar la UI
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA MQTT ---
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBMANU-WEB")

# --- INTERFAZ LATERAL (Sidebar) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    st.info("Este panel controla la conexión MQTT y el estado del sistema.")
    status_placeholder = st.empty()
    status_placeholder.markdown("🟢 **Sistema Online**")
    
    if st.button("Limpiar historial"):
        st.cache_data.clear()

# --- CUERPO PRINCIPAL ---
col_img, col_text = st.columns([1, 2])

with col_img:
    try:
        # Intenta cargar la imagen (asegúrate de que esté en tu repo de GitHub)
        image = Image.open('voice_ctrl.jpg')
        st.image(image, use_container_width=True, caption="Escucha activa")
    except:
        st.image("https://via.placeholder.com/400x400.png?text=Icono+Voz", use_container_width=True)

with col_text:
    st.title("Interfaces Multimodales")
    st.subheader("Control de Voz e IoT")
    st.write("Presiona el botón verde para dictar un comando. El texto se enviará automáticamente al broker MQTT.")

    # --- BOTÓN BOKEH PERSONALIZADO ---
    stt_button = Button(label="🎙️ HABLAR AHORA", width=300, button_type="success")
    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'es-ES';
        
        recognition.onresult = function (e) {
            var value = e.results[0][0].transcript;
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
        """))

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=80,
        debounce_time=0)

    # --- MANEJO DE RESULTADOS ---
    if result and "GET_TEXT" in result:
        comando = result.get("GET_TEXT")
        
        # Mostrar el comando en un recuadro llamativo
        st.success(f"**Comando detectado:** {comando}")
        
        # Enviar vía MQTT
        try:
            client1.connect(broker, port)
            message = json.dumps({"Act1": comando.strip()})
            client1.publish("voice_manu", message)
            st.toast(f"Publicado: {comando}", icon="📤")
        except Exception as e:
            st.error(f"Error al conectar con el broker: {e}")

# Crear carpeta temporal si no existe
if not os.path.exists("temp"):
    os.makedirs("temp")
