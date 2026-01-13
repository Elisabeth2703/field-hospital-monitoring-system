import json
import random
import time
from datetime import datetime
import paho.mqtt.client as mqtt

from equipment.mqtt.mqtt_config import mqtt_config


class EquipmentSimulator:
    def __init__(self, qr_code: str, name: str):
        self.qr_code = qr_code
        self.name = name
        self.client = mqtt.Client(client_id=f"equipment_{qr_code}")

    def connect(self):
        self.client.connect(
            mqtt_config.BROKER_HOST,
            mqtt_config.BROKER_PORT,
            mqtt_config.KEEP_ALIVE
        )
        self.client.loop_start()
        print("✅ MQTT connected")

    def generate_payload(self):
        quantity = random.randint(0, 50)
        status = "working" if quantity > 0 else "broken"

        return {
            "qr_code": self.qr_code,
            "name": self.name,
            "quantity": quantity,
            "critical_level": 5,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }

    def publish(self):
        payload = self.generate_payload()
        topic = f"{mqtt_config.TOPIC_PREFIX}/equipment/{self.qr_code}"

        self.client.publish(
            topic,
            json.dumps(payload),
            qos=mqtt_config.QOS_DATA
        )

        print(
            f"[{payload['timestamp']}] "
            f"{self.qr_code} | qty={payload['quantity']} | {payload['status']}"
        )

    def start(self, interval=5):
        try:
            while True:
                self.publish()
                time.sleep(interval)
        except KeyboardInterrupt:
            self.client.loop_stop()
            self.client.disconnect()


if __name__ == "__main__":
    sim = EquipmentSimulator("EQ-001", "Аналізатор крові")
    sim.connect()
    sim.start()