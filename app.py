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

# --- CONFIGURACIÓN VISUAL Y CSS ---
st.set_page_config(page_title="Interfaces Multimodales", page_icon="🌸")

st.markdown("""
    <style>
    /* Fondo de la página */
    .main { background-color: #fffafa; }
    
    /* Títulos en fucsia */
    h1, h2, h3, .stSubheader { color: #ff1493 !important; }

    /* ESTILO PARA EL BOTÓN DE INICIO (ROSADO) */
    .bk-btn {
        background-color: #ff69b4 !important; /* Rosado principal */
        color: white !important;
        border-radius: 10px !important;
        border: 2px solid #db7093 !important;
        font-weight: bold !important;
        height: 50px !important;
    }
    
    .bk-btn:hover {
        background-color: #ff1493 !important; /* Rosado más oscuro al pasar el mouse */
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA ORIGINAL (MANTENIDA EXACTAMENTE IGUAL) ---
def on_publish(client,userdata,result):
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received=str(message.payload.decode("utf-8"))
    st.write(message_received)

broker="broker.mqttdashboard.com"
port=1883
client1= paho.Client("GIT-HUBMANU")
client1.on_message = on_message

# --- INTERFAZ ---
st.title("Interfaces Multimodales")
st.subheader("Control de voz")

try:
    image = Image.open('voice_ctrl.jpg')
    st.image(image, width=200)
except:
    pass

st.write("Presiona el Botón y habla")

# El botón ahora heredará el estilo .bk-btn que definimos arriba
stt_button = Button(label=" Inicio ", width=200)

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
        st.write(result.get("GET_TEXT"))
        client1.on_publish = on_publish                             
        client1.connect(broker,port)  
        message = json.dumps({"Act1":result.get("GET_TEXT").strip()})
        ret= client1.publish("voice_manu", message)

    try:
        os.mkdir("temp")
    except:
        pass
