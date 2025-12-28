import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from .models import Equipment


def load_equipment_data():
    queryset = Equipment.objects.all().values()
    df = pd.DataFrame(list(queryset))
    return df


def equipment_status_analysis():
    df = load_equipment_data()
    return df['status'].value_counts()


def low_quantity_equipment(threshold=2):
    df = load_equipment_data()
    low_eq = df[df['quantity'] <= threshold][['name', 'quantity']]
    return low_eq


def equipment_time_series():
    df = load_equipment_data()

    df['purchase_date'] = pd.to_datetime(df['purchase_date'])
    df = df.dropna(subset=['purchase_date'])

    df = df.set_index('purchase_date')
    monthly = df.resample('M')['quantity'].sum()

    return monthly


def equipment_forecast(months_ahead=3):
    ts = equipment_time_series()

    if len(ts) < 2:
        return []

    X = np.array(range(len(ts))).reshape(-1, 1)
    y = ts.values

    model = LinearRegression()
    model.fit(X, y)

    future_X = np.array(
        range(len(ts), len(ts) + months_ahead)
    ).reshape(-1, 1)

    forecast = model.predict(future_X)
    return forecast
