import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

# --- PARTE ESTÉTICA (CSS) ---
st.set_page_config(page_title="Interfaces Multimodales", page_icon="🌸")

st.markdown("""
    <style>
    .main { background-color: #fff5f7; }
    h1, h2, h3 { color: #d02090 !important; }
    /* Estilo para el botón de Bokeh */
    .bk-btn-success {
        background-color: #ff69b4 !important;
        border-color: #ff1493 !important;
        color: white !important;
        border-radius: 15px !important;
    }
    /* Estilo para los textos de Streamlit */
    .stWrite { color: #8b008b; }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA ORIGINAL (SIN CAMBIOS) ---
def on_publish(client,userdata,result):             #create function for callback
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("GIT-HUBMANU") # Nombre de cliente original
client1.on_message = on_message

# --- INTERFAZ VISUAL ---
st.title("Interfaces Multimodales")
st.subheader("Control de voz")

try:
    image = Image.open('voz.png')
    st.image(image, width=400)
except:
    st.write("🌸 (Imagen: voz.png)")

st.write("Presiona el Botón y habla")

# Botón Bokeh con color forzado por CSS
stt_button = Button(label=" Inicio ", width=200, button_type="success")

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
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
    override_height=75,
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        detectado = result.get("GET_TEXT")
        st.write(f"Detectado: {detectado}")
        
        # --- LÓGICA DE PUBLICACIÓN ORIGINAL ---
        client1.on_publish = on_publish                             
        client1.connect(broker,port)  
        message = json.dumps({"Act1":detectado.strip()})
        ret= client1.publish("voice_manu", message) # Tópico y mensaje original

    try:
        os.mkdir("temp")
    except:
        pass
