"""
Конфігурація MQTT для системи моніторингу пацієнтів
"""

import os
from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass
class MQTTConfig:
  """Конфігурація MQTT брокера"""
  
  BROKER_HOST: str = os.getenv('MQTT_BROKER_HOST', 'localhost')
  BROKER_PORT: int = int(os.getenv('MQTT_BROKER_PORT', 1883))
  
  USERNAME: str = os.getenv('MQTT_USERNAME', '')
  PASSWORD: str = os.getenv('MQTT_PASSWORD', '')
  
  TOPIC_PREFIX: str = 'field_hospital'
  VITALS_TOPIC: str = f'{TOPIC_PREFIX}/vitals/+'
  ALERTS_TOPIC: str = f'{TOPIC_PREFIX}/alerts'
  STATUS_TOPIC: str = f'{TOPIC_PREFIX}/status/+'
  
  QOS_VITALS: int = 1
  QOS_ALERTS: int = 2
  
  RECONNECT_DELAY: int = 5
  MAX_RECONNECT_ATTEMPTS: int = 10
  
  KEEP_ALIVE: int = 60
  
  CLEAN_SESSION: bool = True
  CLIENT_ID_PREFIX: str = 'field_hospital_subscriber'


@dataclass
class VitalsThresholds:
  """Пороги для життєвих показників"""
  
  HEART_RATE_MIN: int = 40
  HEART_RATE_MAX: int = 200
  HEART_RATE_CRITICAL_LOW: int = 50
  HEART_RATE_CRITICAL_HIGH: int = 150
  
  TEMPERATURE_MIN: float = 35.0
  TEMPERATURE_MAX: float = 42.0
  TEMPERATURE_CRITICAL_LOW: float = 35.5
  TEMPERATURE_CRITICAL_HIGH: float = 38.5
  
  BP_SYS_MIN: int = 70
  BP_SYS_MAX: int = 200
  BP_SYS_CRITICAL_LOW: int = 90
  BP_SYS_CRITICAL_HIGH: int = 180
  
  BP_DIA_MIN: int = 40
  BP_DIA_MAX: int = 130
  BP_DIA_CRITICAL_LOW: int = 60
  BP_DIA_CRITICAL_HIGH: int = 110
  
  OXYGEN_MIN: int = 70
  OXYGEN_MAX: int = 100
  OXYGEN_CRITICAL: int = 90


class AlertLevels:
  """Рівні алертів"""
  INFO = 'info'
  WARNING = 'warning'
  CRITICAL = 'critical'
  EMERGENCY = 'emergency'

mqtt_config = MQTTConfig()
vitals_thresholds = VitalsThresholds()

def get_vitals_topic(bracelet_id: str) -> str:
  """Отримати topic для конкретного браслету"""
  return f"{mqtt_config.TOPIC_PREFIX}/vitals/{bracelet_id}"

def get_alert_topic(bracelet_id: str) -> str:
  """Отримати topic алертів для браслету"""
  return f"{mqtt_config.TOPIC_PREFIX}/alerts/{bracelet_id}"

def validate_vitals_data(data: Dict) -> Tuple[bool, List[str]]:
  """
  Валідація даних життєвих показників
  """
  errors = []
  
  required_fields = ['bracelet_id', 'heart_rate', 'temperature', 'oxygen_saturation']
  for field in required_fields:
    if field not in data:
      errors.append(f"Missing required field: {field}")
  
  if errors:
    return False, errors
  
  hr = data.get('heart_rate')
  if hr and (hr < vitals_thresholds.HEART_RATE_MIN or hr > vitals_thresholds.HEART_RATE_MAX):
    errors.append(f"Heart rate {hr} out of range")
  
  temp = data.get('temperature')
  if temp and (temp < vitals_thresholds.TEMPERATURE_MIN or temp > vitals_thresholds.TEMPERATURE_MAX):
    errors.append(f"Temperature {temp} out of range")
  
  oxygen = data.get('oxygen_saturation')
  if oxygen and (oxygen < vitals_thresholds.OXYGEN_MIN or oxygen > vitals_thresholds.OXYGEN_MAX):
    errors.append(f"Oxygen saturation {oxygen} out of range")
  
  return len(errors) == 0, errors


def check_critical_vitals(data: Dict) -> List[Dict]:
  """
  Перевірка критичних показників
  """
  alerts = []
  
  hr = data.get('heart_rate')
  if hr:
    if hr < vitals_thresholds.HEART_RATE_CRITICAL_LOW:
      alerts.append({
        'level': AlertLevels.CRITICAL,
        'parameter': 'heart_rate',
        'value': hr,
        'message': f'Критично низький пульс: {hr} bpm'
      })
    elif hr > vitals_thresholds.HEART_RATE_CRITICAL_HIGH:
      alerts.append({
        'level': AlertLevels.CRITICAL,
        'parameter': 'heart_rate',
        'value': hr,
        'message': f'Критично високий пульс: {hr} bpm'
      })

  temp = data.get('temperature')
  if temp:
    if temp < vitals_thresholds.TEMPERATURE_CRITICAL_LOW:
      alerts.append({
          'level': AlertLevels.CRITICAL,
          'parameter': 'temperature',
          'value': temp,
          'message': f'Критично низька температура: {temp}°C'
        })
    elif temp > vitals_thresholds.TEMPERATURE_CRITICAL_HIGH:
      alerts.append({
        'level': AlertLevels.CRITICAL,
        'parameter': 'temperature',
        'value': temp,
        'message': f'Критично висока температура: {temp}°C'
      })
  
  oxygen = data.get('oxygen_saturation')
  if oxygen and oxygen < vitals_thresholds.OXYGEN_CRITICAL:
    alerts.append({
      'level': AlertLevels.EMERGENCY,
      'parameter': 'oxygen_saturation',
      'value': oxygen,
      'message': f'НЕБЕЗПЕЧНО НИЗЬКА сатурація кисню: {oxygen}%'
    })
  
  bp_sys = data.get('blood_pressure_sys')
  if bp_sys:
    if bp_sys < vitals_thresholds.BP_SYS_CRITICAL_LOW:
      alerts.append({
        'level': AlertLevels.CRITICAL,
        'parameter': 'blood_pressure',
        'value': bp_sys,
        'message': f'Критично низький систолічний тиск: {bp_sys} mmHg'
      })
    elif bp_sys > vitals_thresholds.BP_SYS_CRITICAL_HIGH:
      alerts.append({
        'level': AlertLevels.CRITICAL,
        'parameter': 'blood_pressure',
        'value': bp_sys,
        'message': f'Критично високий систолічний тиск: {bp_sys} mmHg'
      })
  
  return alerts