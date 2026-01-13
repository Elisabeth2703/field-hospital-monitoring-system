import os
import sys
import json
from datetime import datetime
import paho.mqtt.client as mqtt

CURRENT_FILE = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_FILE)))
sys.path.append(BASE_DIR)

from equipment.mongodb_utils import MongoDBManager
from equipment.mqtt.mqtt_config import mqtt_config

mongo_client = MongoDBManager()
db = mongo_client.client["field_hospital_db"]
collection = db["equipment_status"]

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe(mqtt_config.EQUIPMENT_TOPIC, qos=mqtt_config.QOS_DATA)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode("utf-8"))
        qr_code = data.get("qr_code")
        if not qr_code:
            return
        last_updated = datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.utcnow()
        collection.update_one(
            {"qr_code": qr_code},
            {"$set": {
                "name": data.get("name", "-"),
                "qr_code": qr_code,
                "quantity": data.get("quantity", 0),
                "critical_level": data.get("critical_level", 0),
                "status": data.get("status", "unknown"),
                "last_updated": last_updated,
                "topic": msg.topic
            }},
            upsert=True
        )
    except Exception:
        pass

client = mqtt.Client(client_id=f"{mqtt_config.CLIENT_ID_PREFIX}_main", protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message
client.connect(mqtt_config.BROKER_HOST, mqtt_config.BROKER_PORT, mqtt_config.KEEP_ALIVE)
client.loop_forever()


