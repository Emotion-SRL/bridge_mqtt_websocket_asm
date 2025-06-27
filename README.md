# MQTT-WebSocket Bridge

Bridge per la conversione di messaggi MQTT in WebSocket per il sistema di parcheggio Emotion.

## Descrizione

Questo servizio agisce come bridge tra un broker MQTT e client WebSocket. Riceve messaggi MQTT da specifici topic relativi ai dati di parcheggio e li inoltra a tutti i client WebSocket connessi.

## Prerequisiti

- Python 3.7+
- pip

## Installazione

1. Clonare il repository:
```bash
git clone https://github.com/Emotion-SRL/bridge_mqtt_websocket
cd bridge_mqtt_websocket
```

2. Installare le dipendenze:
```bash
pip install -r requirements.txt
```

3. Configurare le variabili d'ambiente (opzionale):
Creare un file `.env` nella root del progetto con le seguenti variabili:
```
MQTT_BROKER=your_broker_address
MQTT_PORT=1883
MQTT_USER=your_username
MQTT_PASSWORD=your_password
```

## Utilizzo

Per avviare il servizio:
```bash
python main.py
```

Il servizio si connetterà al broker MQTT specificato e aprirà un server WebSocket sulla porta 8765.

## Docker

Il servizio può essere eseguito anche tramite Docker:

```bash
cd scripts
docker-compose up -d
```

## Licenza

Copyright (c) 2025 Emotion SRL. Tutti i diritti riservati.
