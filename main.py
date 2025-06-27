# filepath: mqtt-ws-bridge/src/main.py
import asyncio
import json
import os
from datetime import datetime
import paho.mqtt.client as mqtt
import websockets
from dotenv import load_dotenv

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
WS_PORT = 8765

# Store connessioni WebSocket attive
active_connections = set()

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
        
        # Invia a tutti i client WebSocket connessi
        asyncio.run(broadcast_message(ws_message))
        
    except Exception as e:
        print(f"Errore nella gestione del messaggio MQTT: {e}")

async def broadcast_message(message):
    """Invia il messaggio a tutti i client WebSocket connessi"""
    if active_connections:
        await asyncio.gather(
            *[connection.send(message) for connection in active_connections]
        )

async def handle_websocket(websocket, path):
    """Gestisce una connessione WebSocket"""
    try:
        print(f"Nuovo client WebSocket connesso")
        active_connections.add(websocket)
        
        # Mantieni la connessione attiva
        await websocket.wait_closed()
        
    except websockets.exceptions.ConnectionClosed:
        print("Client WebSocket disconnesso")
    finally:
        active_connections.remove(websocket)

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
    
    # Avvia client MQTT in un thread separato
    mqtt_client = setup_mqtt()
    mqtt_client.loop_start()
    
    # Avvia server WebSocket
    async with websockets.serve(handle_websocket, "0.0.0.0", WS_PORT):
        print(f"Server WebSocket in ascolto sulla porta {WS_PORT}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())