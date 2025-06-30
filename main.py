import paho.mqtt.client as mqtt
import logging

# === Configurazione logging ===
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mqtt_relay.log"),
        logging.StreamHandler()
    ]
)

# === Configurazione broker MQTT di origine ===
MQTT_BROKER = "185.131.248.7"
MQTT_PORT = 1883
MQTT_USER = "wisegrid"
MQTT_PASSWORD = "wisegrid"

# === Configurazione broker WebSocket MQTT di destinazione ===
WS_HOST = "emotion-projects.eu"
WS_PORT = 443
WS_URL = f"wss://{WS_HOST}:{WS_PORT}/mqtt"

TOPIC_MAPPING = {
    "A2MQTT_EMOTION/MINUTI_PERM_MEDIA_GIORNALIERA/CV": "parking-asm/average_duration",
    "A2MQTT_EMOTION/STALLI_OCCUPATI/CV": "parking-asm/occupied_spots"
}

# === Client MQTT (origine) ===
def on_connect_source(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connesso con successo al broker MQTT di origine.")
        for topic in TOPIC_MAPPING:
            client.subscribe(topic)
            logging.info(f"Iscritto al topic: {topic}")
    else:
        logging.error(f"Errore nella connessione al broker di origine. Codice: {rc}")

def on_message(client, userdata, msg):
    target_topic = TOPIC_MAPPING.get(msg.topic)
    payload = msg.payload.decode()

    if target_topic:
        logging.info(f"Messaggio ricevuto da {msg.topic}: {payload}")
        try:
            result = ws_client.publish(target_topic, msg.payload)
            status = result[0]
            if status == mqtt.MQTT_ERR_SUCCESS:
                logging.info(f"Messaggio inoltrato a {target_topic} con successo.")
            else:
                logging.error(f"Errore durante la pubblicazione su {target_topic}. Codice: {status}")
        except Exception as e:
            logging.exception(f"Eccezione durante la pubblicazione su {target_topic}: {e}")
    else:
        logging.warning(f"Topic non mappato: {msg.topic}")

# === Client MQTT (WebSocket destinazione) ===
ws_client = mqtt.Client(transport="websockets")
ws_client.tls_set()
ws_client.tls_insecure_set(True)  # Se necessario per evitare errori con certificati self-signed

try:
    ws_client.connect(WS_HOST, WS_PORT, 60)
    ws_client.loop_start()
    logging.info("Connesso al broker WebSocket MQTT di destinazione.")
except Exception as e:
    logging.exception(f"Errore nella connessione al broker WebSocket: {e}")

# === Connessione client sorgente ===
source_client = mqtt.Client()
source_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
source_client.on_connect = on_connect_source
source_client.on_message = on_message

try:
    source_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    source_client.loop_forever()
except Exception as e:
    logging.exception(f"Errore nella connessione al broker di origine: {e}")