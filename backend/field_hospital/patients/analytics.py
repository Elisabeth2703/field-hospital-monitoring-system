import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from django.db.models import Count, Avg, Q
from .models import Patient, VitalSigns, InjuryClassification
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import json

class PatientAnalytics:
  """Клас для аналізу даних пацієнтів"""
    
  def __init__(self):
    self.label_encoder = LabelEncoder()
  
  def get_patients_dataframe(self, period_days=None):
    """Отримати DataFrame з пацієнтами"""
    queryset = Patient.objects.all()
    
    if period_days:
      start_date = datetime.now() - timedelta(days=period_days)
      queryset = queryset.filter(admission_date__gte=start_date)
    
    data = list(queryset.values(
      'full_name', 'age', 'bracelet_id', 'injury_type', 
      'severity', 'admission_date', 'bed_number', 'blood_type', 'status'
    ))
    
    df = pd.DataFrame(data)
    
    if not df.empty:
      df['admission_date'] = pd.to_datetime(df['admission_date'])
      df['admission_day'] = df['admission_date'].dt.date
      df['admission_hour'] = df['admission_date'].dt.hour
      df['day_of_week'] = df['admission_date'].dt.day_name()
    
    return df
  
  def get_vital_signs_dataframe(self, bracelet_id=None):
    """Отримати DataFrame з життєвими показниками"""
    queryset = VitalSigns.objects.all()
    
    if bracelet_id:
      queryset = queryset.filter(patient_bracelet_id=bracelet_id)
    
    data = list(queryset.values(
      'patient_bracelet_id', 'timestamp', 'heart_rate',
      'temperature', 'blood_pressure_sys', 'blood_pressure_dia',
      'oxygen_saturation'
    ))
    
    df = pd.DataFrame(data)
    
    if not df.empty:
      df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    return df
  
  def analyze_by_period(self, period='week'):
    """Аналіз надходжень за період"""
    period_map = {
      'week': 7,
      'three_months': 90,
      'year': 365
    }
    
    days = period_map.get(period, 7)
    df = self.get_patients_dataframe(period_days=days)
    
    if df.empty:
      return {
        'total_patients': 0,
        'by_injury': {},
        'by_severity': {},
        'by_day': {},
        'statistics': {}
      }
    
    injury_counts = df['injury_type'].value_counts().to_dict()
    
    severity_counts = df['severity'].value_counts().to_dict()
    
    daily_counts = df.groupby('admission_day').size().to_dict()
    daily_counts = {str(k): v for k, v in daily_counts.items()}
    
    age_stats = {
      'mean': float(df['age'].mean()),
      'median': float(df['age'].median()),
      'min': int(df['age'].min()),
      'max': int(df['age'].max()),
      'std': float(df['age'].std())
    }
    
    return {
      'total_patients': len(df),
      'by_injury': injury_counts,
      'by_severity': severity_counts,
      'by_day': daily_counts,
      'age_statistics': age_stats,
      'period': period,
      'days': days
    }
  
  def classify_injury_severity(self):
      """Класифікація поранень за важкістю з використанням ML"""
      df = self.get_patients_dataframe()
      
      if df.empty or len(df) < 5:
          return None
      
      # Підготовка даних для ML
      # Кодування категоріальних змінних
      df['injury_encoded'] = self.label_encoder.fit_transform(df['injury_type'])
      df['severity_encoded'] = df['severity'].map({
          'Легкий': 1,
          'Середній': 2,
          'Важкий': 3,
          'Критичний': 4
      })
      
      # Розрахунок статистики
      injury_severity_stats = df.groupby('injury_type').agg({
          'severity_encoded': ['mean', 'std', 'count']
      }).round(2)
      
      result = {}
      for injury_type in df['injury_type'].unique():
          stats = injury_severity_stats.loc[injury_type]
          result[injury_type] = {
              'average_severity': float(stats[('severity_encoded', 'mean')]),
              'std_deviation': float(stats[('severity_encoded', 'std')]),
              'count': int(stats[('severity_encoded', 'count')])
          }
      
      return result
  
  def analyze_time_series(self, bracelet_id):
    """Аналіз часових рядів життєвих показників"""
    df = self.get_vital_signs_dataframe(bracelet_id)
    
    if df.empty:
      return None
    
    df = df.sort_values('timestamp')
    
    stats = {
      'heart_rate': {
        'mean': float(df['heart_rate'].mean()),
        'std': float(df['heart_rate'].std()),
        'min': int(df['heart_rate'].min()),
        'max': int(df['heart_rate'].max()),
        'trend': self._calculate_trend(df['heart_rate'].values)
      },
      'temperature': {
        'mean': float(df['temperature'].mean()),
        'std': float(df['temperature'].std()),
        'min': float(df['temperature'].min()),
        'max': float(df['temperature'].max()),
        'trend': self._calculate_trend(df['temperature'].values)
      },
      'oxygen_saturation': {
        'mean': float(df['oxygen_saturation'].mean()),
        'std': float(df['oxygen_saturation'].std()),
        'min': int(df['oxygen_saturation'].min()),
        'max': int(df['oxygen_saturation'].max()),
        'trend': self._calculate_trend(df['oxygen_saturation'].values)
      },
      'blood_pressure': {
        'sys_mean': float(df['blood_pressure_sys'].mean()),
        'dia_mean': float(df['blood_pressure_dia'].mean()),
      }
    }
    
    anomalies = self._detect_anomalies(df)
    
    return {
      'statistics': stats,
      'anomalies': anomalies,
      'measurements_count': len(df),
      'time_span_hours': (df['timestamp'].max() - df['timestamp'].min()).total_seconds() / 3600
    }
  
  def _calculate_trend(self, values):
    """Розрахунок тренду (зростання/спадання)"""
    if len(values) < 2:
      return 'insufficient_data'
    
    X = np.arange(len(values)).reshape(-1, 1)
    y = values
    
    model = LinearRegression()
    model.fit(X, y)
    
    slope = model.coef_[0]
    
    if slope > 0.5:
      return 'increasing'
    elif slope < -0.5:
      return 'decreasing'
    else:
      return 'stable'
  
  def _detect_anomalies(self, df):
    """Виявлення аномалій у життєвих показниках"""
    anomalies = []
    
    hr_mean = df['heart_rate'].mean()
    hr_std = df['heart_rate'].std()
    hr_anomalies = df[
      (df['heart_rate'] < hr_mean - 2*hr_std) | 
      (df['heart_rate'] > hr_mean + 2*hr_std)
    ]
    
    for _, row in hr_anomalies.iterrows():
      anomalies.append({
        'timestamp': row['timestamp'].isoformat(),
        'type': 'heart_rate',
        'value': int(row['heart_rate']),
        'severity': 'high' if row['heart_rate'] > 120 else 'low'
      })
    
    temp_anomalies = df[
      (df['temperature'] < 36.0) | 
      (df['temperature'] > 38.0)
    ]
    
    for _, row in temp_anomalies.iterrows():
      anomalies.append({
        'timestamp': row['timestamp'].isoformat(),
        'type': 'temperature',
        'value': float(row['temperature']),
        'severity': 'high' if row['temperature'] > 38.0 else 'low'
      })
    
    o2_anomalies = df[df['oxygen_saturation'] < 95]
    
    for _, row in o2_anomalies.iterrows():
      anomalies.append({
        'timestamp': row['timestamp'].isoformat(),
        'type': 'oxygen',
        'value': int(row['oxygen_saturation']),
        'severity': 'critical' if row['oxygen_saturation'] < 90 else 'warning'
      })
    
    return anomalies
  
  def predict_patient_flow(self, days_ahead=7):
    """Прогнозування потоку пацієнтів"""
    df = self.get_patients_dataframe(period_days=30)
    
    if df.empty or len(df) < 7:
      return None
    
    daily_admissions = df.groupby('admission_day').size().reset_index(name='count')
    daily_admissions['day_index'] = range(len(daily_admissions))
    
    X = daily_admissions[['day_index']].values
    y = daily_admissions['count'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    last_day_index = daily_admissions['day_index'].max()
    future_days = np.arange(last_day_index + 1, last_day_index + days_ahead + 1).reshape(-1, 1)
    predictions = model.predict(future_days)
    
    return {
      'predicted_daily_average': float(predictions.mean()),
      'predicted_total': float(predictions.sum()),
      'trend': 'increasing' if model.coef_[0] > 0 else 'decreasing',
      'confidence': float(model.score(X, y))
    }
  
  def get_correlation_analysis(self):
    """Кореляційний аналіз між віком та важкістю"""
    df = self.get_patients_dataframe()
    
    if df.empty:
      return None
    
    df['severity_code'] = df['severity'].map({
      'Легкий': 1,
      'Середній': 2,
      'Важкий': 3,
      'Критичний': 4
    })
    
    correlation = df[['age', 'severity_code']].corr().iloc[0, 1]
    
    df['age_group'] = pd.cut(df['age'], bins=[0, 25, 35, 45, 100], 
      labels=['18-25', '26-35', '36-45', '46+'])
    
    age_group_severity = df.groupby('age_group')['severity_code'].mean().to_dict()
    
    return {
      'correlation_age_severity': float(correlation),
      'age_group_severity': {str(k): float(v) for k, v in age_group_severity.items()}
    }