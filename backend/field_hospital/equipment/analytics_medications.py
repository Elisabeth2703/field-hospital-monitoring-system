import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime
from .mongodb_utils import MongoDBManager

db = MongoDBManager()


def load_medications_data():
  meds = db.get_all_medications()
  df = pd.DataFrame(meds)
  if 'expiry_date' in df.columns:
      df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce')
  if 'last_update' in df.columns:
      df['last_update'] = pd.to_datetime(df['last_update'], errors='coerce')
  return df


def medication_basic_stats():
  df = load_medications_data()

  total_items = len(df)
  total_quantity = df['quantity'].sum()

  critical = df[df['quantity'] <= df['critical_level']]
  expired = df[df['expiry_date'] < pd.Timestamp(datetime.today())]

  sufficient = df[df['quantity'] > df['critical_level']]

  return {
    'total_items': total_items,
    'total_quantity': total_quantity,
    'critical_count': len(critical),
    'expired_count': len(expired),
    'sufficient_count': len(sufficient),
    'critical': critical.to_dict(orient='records'),
    'expired': expired.to_dict(orient='records'),
  }


def medication_quantity_trend(months=6):
  """
  Простий тренд кількості медикаментів за останні місяці
  - Припускаємо, що є поле last_update з датою останнього оновлення запасу
  """
  df = load_medications_data()
  if 'last_update' not in df.columns:
      return {}

  cutoff = pd.Timestamp(datetime.today()) - pd.DateOffset(months=months)
  df_recent = df[df['last_update'] >= cutoff]

  df_recent['month'] = df_recent['last_update'].dt.to_period('M')
  monthly_quantity = df_recent.groupby('month')['quantity'].sum().sort_index()

  return monthly_quantity.to_dict()


def medication_forecast(months_ahead=3):
  """
  Простий прогноз кількості медикаментів на основі лінійної регресії
  по місячним даним
  """
  ts_dict = medication_quantity_trend(months=12)
  if not ts_dict:
      return []

  ts = pd.Series(ts_dict)
  ts.index = ts.index.to_timestamp()

  X = np.array(range(len(ts))).reshape(-1, 1)
  y = ts.values

  if len(X) < 2:
      return []

  model = LinearRegression()
  model.fit(X, y)

  future_X = np.array(range(len(ts), len(ts) + months_ahead)).reshape(-1, 1)
  forecast = model.predict(future_X)

  
  future_months = pd.date_range(start=ts.index[-1] + pd.offsets.MonthBegin(),
    periods=months_ahead, freq='MS')

  forecast_result = [
    {'month': m.strftime('%Y-%m'), 'predicted_quantity': max(0, float(f))}
    for m, f in zip(future_months, forecast)
  ]

  return forecast_result
