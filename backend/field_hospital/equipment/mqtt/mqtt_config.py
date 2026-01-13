from dataclasses import dataclass
import os

@dataclass
class MQTTConfig:
    BROKER_HOST: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    BROKER_PORT: int = int(os.getenv("MQTT_BROKER_PORT", 1883))

    TOPIC_PREFIX: str = "field_hospital"

    EQUIPMENT_TOPIC: str = f"{TOPIC_PREFIX}/equipment/+"
    ALERTS_TOPIC: str = f"{TOPIC_PREFIX}/alerts/+"

    QOS_DATA: int = 1
    QOS_ALERTS: int = 2

    KEEP_ALIVE: int = 60
    CLIENT_ID_PREFIX: str = "equipment_subscriber"


@dataclass
class EquipmentThresholds:
    MIN_QUANTITY: int = 5


mqtt_config = MQTTConfig()
equipment_thresholds = EquipmentThresholds()