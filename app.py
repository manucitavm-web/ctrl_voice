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
    page_title="Voice IoT Pink Edition",
    page_icon="🌸",
    layout="wide"
)

# --- CSS PERSONALIZADO (AQUÍ ESTÁ EL ROSADO) ---
st.markdown("""
    <style>
    /* Fondo general */
    .main { background-color: #fff0f5; }
    
    /* Botón de Streamlit (el de limpiar) */
    .stButton>button {
        border-radius: 20px;
        background-color: #ff69b4;
        color: white;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff1493;
        color: white;
    }

    /* Forzar color rosado al botón de Bokeh */
    .bk-btn-success {
        background-color: #ff69b4 !important;
        border-color: #ff1493 !important;
        color: white !important;
        border-radius: 15px !important;
        font-weight: bold !important;
    }

    /* Tarjetas de mensajes */
    .stSuccess {
        background-color: #ffe4e1;
        border: 1px solid #ffb6c1;
        color: #d02090;
    }
    
    /* Títulos */
    h1, h2, h3 { color: #d02090 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA MQTT ---
broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBMANU-PINK")

# --- INTERFAZ LATERAL ---
with st.sidebar:
    st.header("🌸 Ajustes")
    st.write("Estado de la conexión:")
    st.markdown("<span style='color: #ff69b4;'>💖 Conectado</span>", unsafe_allow_html=True)
    
    if st.button("Limpiar historial"):
        st.cache_data.clear()

# --- CUERPO PRINCIPAL ---
st.title("🎙️ Interfaces Multimodales")
st.subheader("Control de Voz - Pink Edition")

col_img, col_ctrl = st.columns([1, 2], gap="large")

with col_img:
    try:
        image = Image.open('voice_ctrl.jpg')
        st.image(image, use_container_width=True)
    except:
        st.image("https://via.placeholder.com/400x400.png/FFC0CB/000000?text=Voice+Control", use_container_width=True)

with col_ctrl:
    st.write("### Panel de Control")
    st.write("Presiona el botón para enviar un comando al broker MQTT:")
    
    # --- BOTÓN BOKEH ---
    stt_button = Button(label="🎤 INICIAR ESCUCHA", width=300, button_type="success")
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

    # --- PROCESAMIENTO ---
    if result and "GET_TEXT" in result:
        comando = result.get("GET_TEXT")
        
        # Cuadro de texto detectado en rosado
        st.markdown(f"""
            <div style="background-color: white; padding: 20px; border-radius: 15px; border-left: 5px solid #ff69b4; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
                <p style="margin:0; font-size: 14px; color: #ff69b4;">Texto capturado:</p>
                <h3 style="margin:0; color: #444;">{comando}</h3>
            </div>
        """, unsafe_allow_html=True)
        
        try:
            client1.connect(broker, port)
            message = json.dumps({"Act1": comando.strip()})
            client1.publish("voice_manu", message)
            st.toast("Enviado con éxito 🌸")
        except Exception as e:
            st.error(f"Error: {e}")

if not os.path.exists("temp"):
    os.makedirs("temp")
