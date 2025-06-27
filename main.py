# filepath: mqtt-ws-bridge/src/main.py
import asyncio
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import websockets
from dotenv import load_dotenv
import ssl

# Carica variabili d'ambiente
load_dotenv()

# Configurazione
MQTT_BROKER = "185.131.248.7"
MQTT_PORT = 1883
MQTT_USER = "wisegrid"
MQTT_PASSWORD = "wisegrid"
MQTT_TOPICS = [
    "A2MQTT_EMOTION/MINUTI_PERM_MEDIA_GIORNALIERA/CV",
    "A2MQTT_EMOTION/STALLI_OCCUPATI/CV"
]

# Configurazione WebSocket
WS_HOST = "emotion-projects.eu"
WS_PORT = 443
WS_URL = f"wss://{WS_HOST}:{WS_PORT}"

# Variabile globale per la connessione WebSocket
ws_connection = None


async def connect_websocket():
    """Stabilisce la connessione WebSocket con il server remoto"""
    global ws_connection
    ssl_context = ssl.create_default_context()
    
    while True:
        try:
            ws_connection = await websockets.connect(WS_URL, ssl=ssl_context)
            print(f"Connesso a WebSocket: {WS_URL}")
            return
        except Exception as e:
            print(f"Errore di connessione al WebSocket: {e}")
            await asyncio.sleep(5)  # Attendi 5 secondi prima di riprovare


async def send_message(message):
    """Invia il messaggio al server WebSocket"""
    global ws_connection
    try:
        if ws_connection and ws_connection.open:
            await ws_connection.send(message)
        else:
            print("Riconnessione al WebSocket...")
            await connect_websocket()
            if ws_connection:
                await ws_connection.send(message)
    except Exception as e:
        print(f"Errore nell'invio del messaggio: {e}")
        ws_connection = None


def on_mqtt_message(client, userdata, message):
    """Callback per i messaggi MQTT ricevuti"""
    try:
        payload = message.payload.decode()
        topic = message.topic
        
        # Prepara il messaggio da inviare via WebSocket
        ws_message = json.dumps({
            "topic": topic,
            "payload": payload,
            "timestamp": datetime.now().isoformat()
        })
        
        # Invia al WebSocket remoto
        asyncio.run(send_message(ws_message))
        
    except Exception as e:
        print(f"Errore nella gestione del messaggio MQTT: {e}")


def setup_mqtt():
    """Configura e avvia il client MQTT"""
    client = mqtt.Client()
    client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    
    # Callbacks
    client.on_connect = lambda client, userdata, flags, rc: \
        print(f"Connesso al broker MQTT con codice: {rc}")
    client.on_message = on_mqtt_message
    
    # Connessione
    client.connect(MQTT_BROKER, MQTT_PORT)
    
    # Sottoscrizione ai topic
    for topic in MQTT_TOPICS:
        client.subscribe(topic)
    
    return client


async def main():
    """Funzione principale"""
    print("Avvio MQTT-WebSocket bridge...")
    
    # Stabilisci la connessione WebSocket
    await connect_websocket()
    
    # Avvia client MQTT in un thread separato
    mqtt_client = setup_mqtt()
    mqtt_client.loop_start()
    
    # Mantieni il programma in esecuzione
    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())