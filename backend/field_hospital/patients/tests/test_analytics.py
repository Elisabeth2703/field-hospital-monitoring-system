from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from patients.models import Patient, VitalSigns, InjuryClassification, MedicalStaff
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


class InjuryClassificationAnalyticsTest(TestCase):
  """Тести для аналітики класифікації поранень"""
  
  def setUp(self):
    """Підготовка тестових даних"""
    injury_data = [
        ('Вогнепальне поранення', 'Важкий'),
        ('Вогнепальне поранення', 'Критичний'),
        ('Осколкове поранення', 'Середній'),
        ('Осколкове поранення', 'Важкий'),
        ('Контузія', 'Легкий'),
        ('Контузія', 'Середній'),
        ('Опіки', 'Важкий'),
        ('Опіки', 'Критичний'),
        ('Переломи', 'Легкий'),
        ('Переломи', 'Середній'),
    ]
        
    for i, (injury_type, severity) in enumerate(injury_data):
      patient = Patient.objects.create(
        full_name=f'Пацієнт Аналітика {i+1}',
        age=25 + i,
        bracelet_id=f'ANAL-{i+1:03d}',
        injury_type=injury_type,
        severity=severity
      )
          
      InjuryClassification.objects.create(
        patient_bracelet_id=patient.bracelet_id,
        injury_type=injury_type,
        severity=severity,
        diagnosis=f'Діагноз {injury_type}',
        treatment_plan=f'План лікування {severity}'
      )
    
  def test_injury_type_distribution(self):
    """Тест: розподіл за типами поранень"""
    injury_counts = {}
    all_patients = Patient.objects.all()
    
    for patient in all_patients:
      injury_type = patient.injury_type
      injury_counts[injury_type] = injury_counts.get(injury_type, 0) + 1
    
    self.assertGreater(len(injury_counts), 0)
    total = sum(injury_counts.values())
    self.assertEqual(total, 10)
    
    print(f"\n Розподіл за типами поранень:")
    for injury, count in injury_counts.items():
      print(f"  {injury}: {count}")
  
  def test_severity_distribution(self):
    """Тест: розподіл за важкістю"""
    severity_counts = {}
    all_patients = Patient.objects.all()
    
    for patient in all_patients:
      severity = patient.severity
      severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    self.assertGreater(len(severity_counts), 0)
    
    print(f"\n Розподіл за важкістю:")
    for severity, count in severity_counts.items():
      print(f"  {severity}: {count}")
  
  def test_classification_statistics(self):
    """Тест: статистика класифікацій"""
    total_classifications = InjuryClassification.objects.count()
    self.assertEqual(total_classifications, 10)
    
    injury_types = ['Вогнепальне поранення', 'Осколкове поранення', 'Контузія', 'Опіки', 'Переломи']
    
    for injury_type in injury_types:
      count = InjuryClassification.objects.filter(
          injury_type=injury_type
      ).count()
      self.assertGreaterEqual(count, 0)


class TimeSeriesAnalyticsTest(TestCase):
  """Тести для аналізу часових рядів"""
  
  def setUp(self):
    """Створюємо дані за різні періоди"""
    base_date = timezone.now()
    
    for days_ago in [1, 7, 30, 90, 180, 365]:
      for i in range(3):
        patient = Patient.objects.create(
          full_name=f'Пацієнт День-{days_ago}-{i+1}',
          age=30,
          bracelet_id=f'TIME-{days_ago}-{i+1}',
          injury_type='Вогнепальне поранення',
          severity='Середній'
        )
          
        patient.admission_date = base_date - timedelta(days=days_ago)
        patient.save()
  
  def test_weekly_statistics(self):
    """Тест: статистика за тиждень"""
    week_ago = timezone.now() - timedelta(days=7)
    
    weekly_patients = Patient.objects.filter(
      admission_date__gte=week_ago
    )
    
    count = weekly_patients.count()
    self.assertGreaterEqual(count, 0)
    print(f"\n Пацієнтів за тиждень: {count}")
  
  def test_monthly_statistics(self):
    """Тест: статистика за місяць"""
    month_ago = timezone.now() - timedelta(days=30)
    
    monthly_patients = Patient.objects.filter(
      admission_date__gte=month_ago
    )
    
    count = monthly_patients.count()
    self.assertGreaterEqual(count, 0)
    print(f"\n Пацієнтів за місяць: {count}")
  
  def test_quarterly_statistics(self):
    """Тест: статистика за квартал (3 місяці)"""
    three_months_ago = timezone.now() - timedelta(days=90)
    
    quarterly_patients = Patient.objects.filter(
      admission_date__gte=three_months_ago
    )
    
    count = quarterly_patients.count()
    self.assertGreaterEqual(count, 0)
    print(f"\n Пацієнтів за квартал: {count}")
  
  def test_yearly_statistics(self):
    """Тест: статистика за рік"""
    year_ago = timezone.now() - timedelta(days=365)
    
    yearly_patients = Patient.objects.filter(
      admission_date__gte=year_ago
    )
    
    count = yearly_patients.count()
    self.assertGreaterEqual(count, 12)
    print(f"\n Пацієнтів за рік: {count}")
  
  def test_time_range_filtering(self):
    """Тест: фільтрація за діапазон часу"""
    start_date = timezone.now() - timedelta(days=100)
    end_date = timezone.now() - timedelta(days=10)
    
    patients_in_range = Patient.objects.filter(
      admission_date__gte=start_date,
      admission_date__lte=end_date
    )
    
    count = patients_in_range.count()
    self.assertGreaterEqual(count, 0)


class PandasAnalyticsTest(TestCase):
  """Тести аналітики з використанням Pandas"""
  
  def setUp(self):
    """Створюємо дані для pandas аналізу"""
    for i in range(20):
        patient = Patient.objects.create(
          full_name=f'Pandas Пацієнт {i+1}',
          age=20 + i,
          bracelet_id=f'PANDAS-{i+1:03d}',
          injury_type=['Вогнепальне поранення', 'Осколкове поранення', 'Контузія'][i % 3],
          severity=['Легкий', 'Середній', 'Важкий'][i % 3]
        )
        
        VitalSigns.objects.create(
          patient_bracelet_id=patient.bracelet_id,
          heart_rate=60 + i * 2,
          temperature=36.0 + (i % 5) * 0.2,
          blood_pressure_sys=110 + i,
          blood_pressure_dia=70 + i // 2,
          oxygen_saturation=95 + (i % 5)
        )
  
  def test_pandas_dataframe_creation(self):
    """Тест: створення DataFrame з даних пацієнтів"""
    patients = Patient.objects.all().values(
      'full_name', 'age', 'injury_type', 'severity', 'bracelet_id'
    )
    
    df = pd.DataFrame(list(patients))
    
    self.assertIsInstance(df, pd.DataFrame)
    self.assertEqual(len(df), 20)
    self.assertIn('age', df.columns)
    self.assertIn('injury_type', df.columns)
    
    print(f"\n DataFrame створено: {df.shape}")
  
  def test_pandas_groupby_analysis(self):
    """Тест: групування та агрегація з pandas"""
    patients = Patient.objects.all().values('injury_type', 'severity', 'age')
    df = pd.DataFrame(list(patients))
    
    grouped = df.groupby('injury_type')['age'].mean()
    
    self.assertIsInstance(grouped, pd.Series)
    self.assertGreater(len(grouped), 0)
    
    print(f"\n Середній вік по типах поранень:")
    print(grouped)
  
  def test_pandas_vital_signs_analysis(self):
    """Тест: аналіз життєвих показників з pandas"""
    vitals = VitalSigns.objects.all().values(
      'patient_bracelet_id', 'heart_rate', 'temperature', 
      'blood_pressure_sys', 'oxygen_saturation'
    )
    
    df = pd.DataFrame(list(vitals))
    
    stats = df.describe()
    
    self.assertIsInstance(stats, pd.DataFrame)
    self.assertIn('heart_rate', stats.columns)
    
    print(f"\n Статистика життєвих показників:")
    print(stats)
  
  def test_pandas_pivot_table(self):
    """Тест: зведена таблиця"""
    patients = Patient.objects.all().values('injury_type', 'severity')
    df = pd.DataFrame(list(patients))
    
    pivot = pd.crosstab(df['injury_type'], df['severity'])
    
    self.assertIsInstance(pivot, pd.DataFrame)
    print(f"\n Зведена таблиця (тип * важкість):")
    print(pivot)


class NumpyAnalyticsTest(TestCase):
  """Тести математичних обчислень з NumPy"""
  
  def setUp(self):
    """Створюємо дані для numpy аналізу"""
    for i in range(30):
      patient = Patient.objects.create(
        full_name=f'NumPy Пацієнт {i+1}',
        age=25 + i,
        bracelet_id=f'NUMPY-{i+1:03d}',
        injury_type='Вогнепальне поранення',
        severity='Середній'
      )
        
      VitalSigns.objects.create(
        patient_bracelet_id=patient.bracelet_id,
        heart_rate=65 + np.random.randint(-10, 10),
        temperature=36.6 + np.random.uniform(-0.5, 0.5),
        blood_pressure_sys=120 + np.random.randint(-15, 15),
        blood_pressure_dia=80 + np.random.randint(-10, 10),
        oxygen_saturation=97 + np.random.randint(-2, 3)
      )

  def test_numpy_basic_statistics(self):
    """Тест: базова статистика з numpy"""
    vitals = VitalSigns.objects.all().values_list('heart_rate', flat=True)
    heart_rates = np.array(list(vitals))
    
    mean = np.mean(heart_rates)
    median = np.median(heart_rates)
    std = np.std(heart_rates)
    min_val = np.min(heart_rates)
    max_val = np.max(heart_rates)
    
    self.assertIsInstance(mean, (float, np.floating))
    self.assertGreater(mean, 0)
    self.assertGreater(std, 0)
    
    print(f"\n Статистика пульсу:")
    print(f"  Середнє: {mean:.2f}")
    print(f"  Медіана: {median:.2f}")
    print(f"  Станд. відхилення: {std:.2f}")
    print(f"  Мін-Макс: {min_val}-{max_val}")
  
  def test_numpy_correlation(self):
    """Тест: кореляційний аналіз"""
    vitals = VitalSigns.objects.all().values(
      'heart_rate', 'blood_pressure_sys', 'oxygen_saturation'
    )
    df = pd.DataFrame(list(vitals))
    
    correlation_matrix = np.corrcoef(
      df['heart_rate'], 
      df['blood_pressure_sys']
    )
    
    self.assertEqual(correlation_matrix.shape, (2, 2))
    correlation = correlation_matrix[0, 1]
    
    self.assertGreaterEqual(correlation, -1)
    self.assertLessEqual(correlation, 1)
    
    print(f"\n Кореляція пульс-тиск: {correlation:.3f}")
  
  def test_numpy_percentiles(self):
    """Тест: обчислення перцентилів"""
    vitals = VitalSigns.objects.all().values_list('temperature', flat=True)
    temperatures = np.array(list(vitals))
    
    percentiles = [25, 50, 75, 90, 95]
    results = np.percentile(temperatures, percentiles)
    
    self.assertEqual(len(results), len(percentiles))
    
    print(f"\n Перцентилі температури:")
    for p, val in zip(percentiles, results):
      print(f"  P{p}: {val:.2f}°C")
  
  def test_numpy_anomaly_detection(self):
    """Тест: виявлення аномалій (за методом 3 сигм)"""
    vitals = VitalSigns.objects.all().values_list('heart_rate', flat=True)
    heart_rates = np.array(list(vitals))
    
    mean = np.mean(heart_rates)
    std = np.std(heart_rates)
    
    lower_bound = mean - 3 * std
    upper_bound = mean + 3 * std
    
    anomalies = heart_rates[(heart_rates < lower_bound) | (heart_rates > upper_bound)]
    
    self.assertIsInstance(anomalies, np.ndarray)
    print(f"\n Виявлено аномалій: {len(anomalies)} з {len(heart_rates)}")


class ScikitLearnAnalyticsTest(TestCase):
  """Тести машинного навчання з scikit-learn"""
  
  def setUp(self):
    """Створюємо дані для ML моделей"""
    injury_types = ['Вогнепальне поранення', 'Осколкове поранення', 'Контузія']
    severities = ['Легкий', 'Середній', 'Важкий']
    
    for i in range(50):
      patient = Patient.objects.create(
        full_name=f'ML Пацієнт {i+1}',
        age=20 + i % 30,
        bracelet_id=f'ML-{i+1:03d}',
        injury_type=injury_types[i % 3],
        severity=severities[(i + i // 3) % 3]
      )
        
      severity_multiplier = {'Легкий': 1.0, 'Середній': 1.2, 'Важкий': 1.5}[patient.severity]
        
      VitalSigns.objects.create(
        patient_bracelet_id=patient.bracelet_id,
        heart_rate=int(70 * severity_multiplier + np.random.randint(-5, 5)),
        temperature=36.6 + (severity_multiplier - 1) * 2 + np.random.uniform(-0.3, 0.3),
        blood_pressure_sys=int(120 * severity_multiplier + np.random.randint(-10, 10)),
        blood_pressure_dia=int(80 * severity_multiplier + np.random.randint(-5, 5)),
        oxygen_saturation=int(98 - (severity_multiplier - 1) * 10 + np.random.randint(-2, 2))
      )
  
  def test_classification_model(self):
    """Тест: модель класифікації важкості"""
    patients = Patient.objects.all()
    
    X = []
    y = []
    
    for patient in patients:
      vitals = VitalSigns.objects.filter(
        patient_bracelet_id=patient.bracelet_id
      ).first()
      
      if vitals:
        X.append([
          vitals.heart_rate,
          vitals.temperature,
          vitals.blood_pressure_sys,
          vitals.oxygen_saturation,
          patient.age
        ])
          
        severity_map = {'Легкий': 0, 'Середній': 1, 'Важкий': 2}
        y.append(severity_map[patient.severity])
    
    X = np.array(X)
    y = np.array(y)
    
    X_train, X_test, y_train, y_test = train_test_split(
      X, y, test_size=0.2, random_state=42
    )
      
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    
    accuracy = model.score(X_test, y_test)
    
    self.assertIsInstance(accuracy, float)
    self.assertGreaterEqual(accuracy, 0.0)
    self.assertLessEqual(accuracy, 1.0)
    
    print(f"\n Точність моделі класифікації: {accuracy:.2%}")
  
  def test_feature_importance(self):
    """Тест: важливість ознак у моделі"""
    patients = list(Patient.objects.all()[:30])
    
    X = []
    y = []
    feature_names = ['heart_rate', 'temperature', 'bp_sys', 'oxygen', 'age']
    
    for patient in patients:
      vitals = VitalSigns.objects.filter(
        patient_bracelet_id=patient.bracelet_id
      ).first()
      
      if vitals:
        X.append([
          vitals.heart_rate,
          vitals.temperature,
          vitals.blood_pressure_sys,
          vitals.oxygen_saturation,
          patient.age
        ])
          
        severity_map = {'Легкий': 0, 'Середній': 1, 'Важкий': 2}
        y.append(severity_map[patient.severity])
    
    X = np.array(X)
    y = np.array(y)
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    importances = model.feature_importances_
    
    self.assertEqual(len(importances), len(feature_names))
    self.assertAlmostEqual(np.sum(importances), 1.0, places=5)
    
    print(f"\n Важливість ознак:")
    for name, importance in zip(feature_names, importances):
      print(f"  {name}: {importance:.3f}")

  def test_prediction_on_new_data(self):
    """Тест: передбачення для нових даних"""
    patients = list(Patient.objects.all()[:40])
    
    X_train = []
    y_train = []
    
    for patient in patients:
      vitals = VitalSigns.objects.filter(
        patient_bracelet_id=patient.bracelet_id
      ).first()
      
      if vitals:
        X_train.append([
          vitals.heart_rate,
          vitals.temperature,
          vitals.blood_pressure_sys,
          vitals.oxygen_saturation,
          patient.age
        ])
        
        severity_map = {'Легкий': 0, 'Середній': 1, 'Важкий': 2}
        y_train.append(severity_map[patient.severity])
    
    X_train = np.array(X_train)
    y_train = np.array(y_train)
    
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    
    new_data = np.array([[
      85,
      37.2,
      140,
      94,
      35
    ]])
    
    prediction = model.predict(new_data)
    
    severity_map_reverse = {0: 'Легкий', 1: 'Середній', 2: 'Важкий'}
    predicted_severity = severity_map_reverse[prediction[0]]
    
    self.assertIn(predicted_severity, ['Легкий', 'Середній', 'Важкий'])
    print(f"\n Передбачена важкість: {predicted_severity}")