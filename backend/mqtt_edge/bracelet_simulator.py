"""
Симулятор медичного браслету пацієнта
Відправляє дані життєвих показників через MQTT
"""

import json
import time
import random
import argparse
from datetime import datetime
from typing import Dict
import paho.mqtt.client as mqtt
from mqtt_config import mqtt_config, get_vitals_topic


class PatientBracelet:
  """Симулятор медичного браслету пацієнта"""
  
  def __init__(self, bracelet_id: str, patient_name: str, severity: str = 'stable'):
    self.bracelet_id = bracelet_id
    self.patient_name = patient_name
    self.severity = severity
    self.client = None
    self.is_connected = False
    
    self.base_vitals = self._get_base_vitals(severity)
    
    print(f" Ініціалізовано браслет: {bracelet_id}")
    print(f" Пацієнт: {patient_name}")
    print(f"  Стан: {severity}")
  
  def _get_base_vitals(self, severity: str) -> Dict:
    """Базові показники залежно від стану пацієнта"""
    vitals = {
      'stable': {
        'heart_rate': 75,
        'temperature': 36.6,
        'blood_pressure_sys': 120,
        'blood_pressure_dia': 80,
        'oxygen_saturation': 98
      },
      'moderate': {
        'heart_rate': 95,
        'temperature': 37.8,
        'blood_pressure_sys': 140,
        'blood_pressure_dia': 90,
        'oxygen_saturation': 94
      },
      'critical': {
        'heart_rate': 125,
        'temperature': 38.9,
        'blood_pressure_sys': 160,
        'blood_pressure_dia': 100,
        'oxygen_saturation': 88
      }
    }
    return vitals.get(severity, vitals['stable'])
  
  def connect(self):
    """Підключення до MQTT брокера"""
    self.client = mqtt.Client(client_id=f"bracelet_{self.bracelet_id}")
    
    self.client.on_connect = self._on_connect
    self.client.on_disconnect = self._on_disconnect
    self.client.on_publish = self._on_publish
    
    try:
      print(f"\n Підключення до MQTT брокера {mqtt_config.BROKER_HOST}:{mqtt_config.BROKER_PORT}...")
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
            
    except Exception as e:
      print(f" Помилка підключення: {e}")
      raise
  
  def _on_connect(self, client, userdata, flags, rc):
    """Callback при підключенні"""
    if rc == 0:
      self.is_connected = True
      print(" Підключено до MQTT брокера")
    else:
      print(f" Помилка підключення, код: {rc}")

  def _on_disconnect(self, client, userdata, rc):
    """Callback при відключенні"""
    self.is_connected = False
    if rc != 0:
      print(f" Несподіване відключення, код: {rc}")
  
  def _on_publish(self, client, userdata, mid):
    """Callback при публікації"""
    pass
  
  def generate_vitals(self) -> Dict:
    """Генерація даних життєвих показників"""
    vitals = {
      'bracelet_id': self.bracelet_id,
      'patient_name': self.patient_name,
      'timestamp': datetime.now().isoformat(),
      'heart_rate': int(self.base_vitals['heart_rate'] + random.randint(-5, 5)),
      'temperature': round(self.base_vitals['temperature'] + random.uniform(-0.3, 0.3), 1),
      'blood_pressure_sys': int(self.base_vitals['blood_pressure_sys'] + random.randint(-10, 10)),
      'blood_pressure_dia': int(self.base_vitals['blood_pressure_dia'] + random.randint(-5, 5)),
      'oxygen_saturation': int(self.base_vitals['oxygen_saturation'] + random.randint(-2, 2)),
      'battery_level': random.randint(60, 100),
      'signal_strength': random.randint(70, 100)
    }
    
    if self.severity == 'critical' and random.random() < 0.2:
      vitals['heart_rate'] = random.randint(140, 160)
      vitals['oxygen_saturation'] = random.randint(85, 89)
    
    return vitals
  
  def publish_vitals(self) -> bool:
    """Відправка даних життєвих показників"""
    if not self.is_connected:
      print(" Не підключено до MQTT брокера")
      return False
    
    try:
      vitals = self.generate_vitals()
      
      payload = json.dumps(vitals)
      
      topic = get_vitals_topic(self.bracelet_id)
      result = self.client.publish(
        topic,
        payload,
        qos=mqtt_config.QOS_VITALS
      )
      
      if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f" [{datetime.now().strftime('%H:%M:%S')}] Відправлено: "
          f"HR={vitals['heart_rate']} bpm, "
          f"T={vitals['temperature']}°C, "
          f"O2={vitals['oxygen_saturation']}%")
        return True
      else:
        print(f" Помилка відправки, код: {result.rc}")
        return False
            
    except Exception as e:
      print(f" Помилка генерації/відправки даних: {e}")
      return False

  def start_monitoring(self, interval: int = 5, duration: int = None):
    start_time = time.time()
    try:
      while True:
        self.publish_vitals()
        
        if duration and (time.time() - start_time) >= duration:
          print(f"\n Завершено моніторинг (тривалість: {duration}s)")
          break
        
        time.sleep(interval)
            
    except KeyboardInterrupt:
      print("\n Моніторинг зупинено користувачем")

  def disconnect(self):
    """Відключення від MQTT брокера"""
    if self.client:
      self.client.loop_stop()
      self.client.disconnect()
      print(" Відключено від MQTT брокера")


def main():
  """Головна функція"""
  parser = argparse.ArgumentParser(description='Симулятор медичного браслету')
  parser.add_argument('--id', required=True, help='ID браслету (напр. BR-001)')
  parser.add_argument('--name', required=True, help='Ім\'я пацієнта')
  parser.add_argument('--severity', 
    choices=['stable', 'moderate', 'critical'],
    default='stable',
    help='Стан пацієнта')
  parser.add_argument('--interval', type=int, default=5,
    help='Інтервал відправки (секунди)')
  parser.add_argument('--duration', type=int, default=None,
    help='Тривалість (секунди), за замовчуванням - нескінченно')
  
  args = parser.parse_args()
  
  bracelet = PatientBracelet(
    bracelet_id=args.id,
    patient_name=args.name,
    severity=args.severity
  )
  
  try:
    bracelet.connect()
    
    bracelet.start_monitoring(
      interval=args.interval,
      duration=args.duration
    )
    
  except Exception as e:
    print(f" Критична помилка: {e}")
  
  finally:
    bracelet.disconnect()


if __name__ == '__main__':
  main()