import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from datetime import datetime
from .mongodb_utils import MongoDBManager

db = MongoDBManager()


def load_medications_data():
    """Завантажуємо всі медикаменти з БД у DataFrame"""
    meds = db.get_all_medications()
    df = pd.DataFrame(meds)
    
    # Переводимо дати у datetime
    if 'expiry_date' in df.columns:
        df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce')
    if 'last_update' in df.columns:
        df['last_update'] = pd.to_datetime(df['last_update'], errors='coerce')
    elif 'last_updated' in df.columns:
        df['last_update'] = pd.to_datetime(df['last_updated'], errors='coerce')
    else:
        df['last_update'] = pd.Timestamp(datetime.today())

    if 'quantity' not in df.columns:
        df['quantity'] = 0
    if 'critical_level' not in df.columns:
        df['critical_level'] = 0

    return df


def medication_basic_stats():
    """Базова статистика медикаментів"""
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


def medication_quantity_trend(months=12):
    """
    Тренд кількості медикаментів за останні місяці
    """
    df = load_medications_data()
    
    if df.empty:
       
        today = pd.Timestamp(datetime.today())
        return {today.to_period('M'): 0}

   
    cutoff = pd.Timestamp(datetime.today()) - pd.DateOffset(months=months)
    df_recent = df[df['last_update'] >= cutoff]

    if df_recent.empty:
       
        last_month = pd.Timestamp(datetime.today()).to_period('M')
        total_qty = df['quantity'].sum()
        return {last_month: total_qty}

    df_recent['month'] = df_recent['last_update'].dt.to_period('M')
    monthly_quantity = df_recent.groupby('month')['quantity'].sum().sort_index()
    return monthly_quantity.to_dict()


def medication_forecast(months_ahead=2):
    """
    Прогноз кількості медикаментів на основі лінійної регресії
    """
    ts_dict = medication_quantity_trend(months=12)
    if not ts_dict:
        return []

    ts = pd.Series(ts_dict)
    ts.index = ts.index.to_timestamp()

    X = np.array(range(len(ts))).reshape(-1, 1)
    y = ts.values

    if len(X) < 2:
       
        last_value = y[-1] if len(y) > 0 else 0
        forecast_result = []
        for i in range(1, months_ahead + 1):
            month = (ts.index[-1] + pd.DateOffset(months=i)).strftime('%Y-%m')
            forecast_result.append({
                'month': month,
                'predicted_quantity': float(last_value)
            })
        return forecast_result

    model = LinearRegression()
    model.fit(X, y)

    future_X = np.array(range(len(ts), len(ts) + months_ahead)).reshape(-1, 1)
    forecast = model.predict(future_X)

    # Дати для прогнозу
    future_months = pd.date_range(
        start=ts.index[-1] + pd.offsets.MonthBegin(),
        periods=months_ahead,
        freq='MS'
    )

    forecast_result = [
        {'month': m.strftime('%Y-%m'), 'predicted_quantity': max(0, float(f))}
        for m, f in zip(future_months, forecast)
    ]

    return forecast_result

