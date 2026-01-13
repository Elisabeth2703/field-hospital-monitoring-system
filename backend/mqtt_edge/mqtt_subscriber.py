"""
MQTT Subscriber для Django
Отримує дані з браслетів і зберігає в MongoDB
"""

import os
import sys
import django
import json
import time
from datetime import datetime
from typing import Dict, Optional

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

OUTER_FH_DIR = os.path.join(BACKEND_DIR, 'field_hospital')
if OUTER_FH_DIR not in sys.path:
    sys.path.insert(0, OUTER_FH_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'field_hospital.settings')

try:
  django.setup()
  print(" Django успешно инициализирован")
except Exception as e:
  print(f" Ошибка инициализации: {e}")
  print(f"DEBUG: BACKEND_DIR = {BACKEND_DIR}")
  print(f"DEBUG: sys.path = {sys.path[:3]}") 
  sys.exit(1)

import paho.mqtt.client as mqtt
from patients.models import Patient, VitalSigns
from mqtt_config import (
  mqtt_config, 
  validate_vitals_data, 
  check_critical_vitals,
  AlertLevels
)


class MQTTSubscriber:
  """MQTT Subscriber для отримання даних з браслетів"""
  
  def __init__(self):
    self.client = None
    self.is_connected = False
    self.messages_received = 0
    self.messages_saved = 0
    self.alerts_generated = 0
    
    print(" Ініціалізація MQTT Subscriber для Field Hospital")

  def connect(self):
    """Підключення до MQTT брокера"""
    client_id = f"{mqtt_config.CLIENT_ID_PREFIX}_{int(time.time())}"
    self.client = mqtt.Client(client_id=client_id)
    
    self.client.on_connect = self._on_connect
    self.client.on_message = self._on_message
    self.client.on_disconnect = self._on_disconnect
    self.client.on_subscribe = self._on_subscribe
    
    try:
      print(f"\n Підключення до MQTT брокера...")
      print(f" Host: {mqtt_config.BROKER_HOST}")
      print(f" Port: {mqtt_config.BROKER_PORT}")
      
      self.client.connect(
        mqtt_config.BROKER_HOST,
        mqtt_config.BROKER_PORT,
        mqtt_config.KEEP_ALIVE
      )
      
      self.client.loop_start()
      
      timeout = 10
      while not self.is_connected and timeout > 0:
        time.sleep(0.5)
        timeout -= 0.5
      
      if not self.is_connected:
        raise ConnectionError("Не вдалося підключитись до MQTT брокера")
      
      return True
        
    except Exception as e:
      print(f" Помилка підключення: {e}")
      return False
  
  def _on_connect(self, client, userdata, flags, rc):
    """Callback при підключенні"""
    if rc == 0:
      self.is_connected = True
      print(" Підключено до MQTT брокера")
      
      print(f"\n Підписка на topics...")
      
      client.subscribe(mqtt_config.VITALS_TOPIC, qos=mqtt_config.QOS_VITALS)
      print(f" {mqtt_config.VITALS_TOPIC}")
      
      client.subscribe(mqtt_config.ALERTS_TOPIC, qos=mqtt_config.QOS_ALERTS)
      print(f" {mqtt_config.ALERTS_TOPIC}")
        
    else:
      error_messages = {
        1: "Неправильна версія протоколу",
        2: "Некоректний client ID",
        3: "Сервер недоступний",
        4: "Неправильний username/password",
        5: "Немає авторизації"
      }
      print(f" Помилка підключення: {error_messages.get(rc, f'Код {rc}')}")

  def _on_subscribe(self, client, userdata, mid, granted_qos):
    """Callback при підписці"""
    print(f" Підписка успішна (QoS: {granted_qos[0]})")
  
  def _on_disconnect(self, client, userdata, rc):
    """Callback при відключенні"""
    self.is_connected = False
    if rc != 0:
      print(f" Несподіване відключення (код: {rc}). Спроба переподключення...")
  
  def _on_message(self, client, userdata, msg):
    """Callback при отриманні повідомлення"""
    try:
      payload = msg.payload.decode('utf-8')
      data = json.loads(payload)
      
      self.messages_received += 1
      
      if '/vitals/' in msg.topic:
        self._handle_vitals_message(data)
      elif '/alerts' in msg.topic:
        self._handle_alert_message(data)
        
    except json.JSONDecodeError as e:
      print(f" Помилка декодування JSON: {e}")
    except Exception as e:
      print(f" Помилка обробки повідомлення: {e}")
  
  def _handle_vitals_message(self, data: Dict):
    """Обробка повідомлення з життєвими показниками"""
    bracelet_id = data.get('bracelet_id')
    
    if not bracelet_id:
      print(" Відсутній bracelet_id в повідомленні")
      return
    
    is_valid, errors = validate_vitals_data(data)
    if not is_valid:
      print(f" Невалідні дані для {bracelet_id}: {', '.join(errors)}")
      return
    
    timestamp = datetime.fromisoformat(data['timestamp']).strftime('%H:%M:%S')
    print(f"\n [{timestamp}] {bracelet_id} ({data.get('patient_name', 'N/A')})")
    print(f" Пульс: {data['heart_rate']} bpm")
    print(f" Температура: {data['temperature']}°C")
    print(f" Тиск: {data.get('blood_pressure_sys', 'N/A')}/{data.get('blood_pressure_dia', 'N/A')} mmHg")
    print(f" Сатурація: {data['oxygen_saturation']}%")
    
    alerts = check_critical_vitals(data)
    if alerts:
      self._process_alerts(bracelet_id, alerts, data)
    
    if self._save_vitals_to_db(data):
      self.messages_saved += 1
      print(f" Збережено в БД (всього: {self.messages_saved})")
    else:
      print(f" Не вдалося зберегти в БД")
  
  def _handle_alert_message(self, data: Dict):
    """Обробка повідомлення-алерту"""
    print(f"\n ALERT: {data}")
  
  def _process_alerts(self, bracelet_id: str, alerts: list, vitals_data: Dict):
    """Обробка алертів"""
    self.alerts_generated += len(alerts)
    
    for alert in alerts:
      level_emoji = {
        AlertLevels.INFO: 'ℹ️',
        AlertLevels.WARNING: '⚠️',
        AlertLevels.CRITICAL: '🔴',
        AlertLevels.EMERGENCY: '🆘'
      }
      
      emoji = level_emoji.get(alert['level'], '⚠️')
      print(f" {emoji} {alert['level'].upper()}: {alert['message']}")
      
      self._publish_alert(bracelet_id, alert, vitals_data)
  
  def _publish_alert(self, bracelet_id: str, alert: Dict, vitals_data: Dict):
    """Публікація алерту в MQTT"""
    try:
      alert_payload = {
        'bracelet_id': bracelet_id,
        'patient_name': vitals_data.get('patient_name', 'Unknown'),
        'timestamp': datetime.now().isoformat(),
        'level': alert['level'],
        'parameter': alert['parameter'],
        'value': alert['value'],
        'message': alert['message']
      }
      
      topic = f"{mqtt_config.ALERTS_TOPIC}/{bracelet_id}"
      self.client.publish(
        topic,
        json.dumps(alert_payload),
        qos=mqtt_config.QOS_ALERTS
      )
        
    except Exception as e:
      print(f" Помилка публікації алерту: {e}")
  
  def _save_vitals_to_db(self, data: Dict) -> bool:
    """Збереження даних у MongoDB"""
    try:
      patient = Patient.objects.filter(
        bracelet_id=data['bracelet_id']
      ).first()
      
      if not patient:
        patient = Patient.objects.create(
          bracelet_id=data['bracelet_id'],
          full_name=data.get('patient_name', 'Unknown Patient'),
          age=30,
          injury_type='Невідомо',
          severity='Середній'
        )
        print(f" Створено нового пацієнта: {patient.bracelet_id}")
      
      VitalSigns.objects.create(
        patient_bracelet_id=patient.bracelet_id,
        heart_rate=data['heart_rate'],
        temperature=data['temperature'],
        blood_pressure_sys=data.get('blood_pressure_sys', 120),
        blood_pressure_dia=data.get('blood_pressure_dia', 80),
        oxygen_saturation=data['oxygen_saturation']
      )
      
      return True
        
    except Exception as e:
      print(f" Помилка збереження в БД: {e}")
      import traceback
      traceback.print_exc()
      return False
  
  def disconnect(self):
    """Відключення від MQTT брокера"""
    if self.client:
      self.client.loop_stop()
      self.client.disconnect()
      print("\n Відключено від MQTT брокера")
      print(f"\n Статистика:")
      print(f" Отримано повідомлень: {self.messages_received}")
      print(f" Збережено в БД: {self.messages_saved}")
      print(f" Алертів згенеровано: {self.alerts_generated}")
  
  def run(self):
    """Запуск subscriber"""
    try:
      if not self.connect():
        return
      
      print("\n MQTT Subscriber запущено")
      print(" Очікування повідомлень...")
      print(" Натисніть Ctrl+C для зупинки\n")
      
      while True:
        time.sleep(1)
            
    except KeyboardInterrupt:
      print("\n Зупинка subscriber...")
    
    finally:
      self.disconnect()


def main():
  """Головна функція"""
  subscriber = MQTTSubscriber()
  subscriber.run()


if __name__ == '__main__':
  main()