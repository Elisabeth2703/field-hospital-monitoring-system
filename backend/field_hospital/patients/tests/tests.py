from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from patients.models import Patient, VitalSigns, InjuryClassification, MedicalStaff


class PatientModelTest(TestCase):
  """Тести для моделі Patient"""
  
  def setUp(self):
    """Підготовка тестових даних"""
    self.patient = Patient.objects.create(
      full_name='Тест Пацієнт',
      age=30,
      bracelet_id='TEST-MODEL-001',
      injury_type='Вогнепальне поранення',
      severity='Середній',
      blood_type='A+',
      bed_number='101',
      status='На лікуванні',
      notes='Тестові примітки'
    )
  
  def test_patient_creation(self):
    """Тест: створення пацієнта"""
    self.assertIsNotNone(self.patient._id)
    self.assertEqual(self.patient.full_name, 'Тест Пацієнт')
    self.assertEqual(self.patient.age, 30)
    self.assertEqual(self.patient.bracelet_id, 'TEST-MODEL-001')
    print(f" Patient created with ID: {self.patient._id}")
  
  def test_patient_str_method(self):
    """Тест: метод __str__ пацієнта"""
    expected = f"{self.patient.full_name} - {self.patient.bracelet_id}"
    self.assertEqual(str(self.patient), expected)
  
  def test_patient_unique_bracelet_id(self):
    """Тест: унікальність bracelet_id"""
    with self.assertRaises(Exception):
      Patient.objects.create(
        full_name='Інший Пацієнт',
        age=25,
        bracelet_id='TEST-MODEL-001',
        injury_type='Переломи',
        severity='Легкий'
      )
  
  def test_patient_fields(self):
    """Тест: всі поля пацієнта"""
    self.assertEqual(self.patient.injury_type, 'Вогнепальне поранення')
    self.assertEqual(self.patient.severity, 'Середній')
    self.assertEqual(self.patient.blood_type, 'A+')
    self.assertEqual(self.patient.bed_number, '101')
    self.assertEqual(self.patient.status, 'На лікуванні')
    self.assertEqual(self.patient.notes, 'Тестові примітки')
  
  def test_patient_default_status(self):
    """Тест: статус за замовчуванням"""
    new_patient = Patient.objects.create(
      full_name='Новий Пацієнт',
      age=28,
      bracelet_id='NEW-001',
      injury_type='Опіки',
      severity='Легкий'
    )
    self.assertEqual(new_patient.status, 'На лікуванні')

  def test_patient_update(self):
    """Тест: оновлення даних пацієнта"""
    self.patient.severity = 'Важкий'
    self.patient.bed_number = '205'
    self.patient.save()
    
    updated = Patient.objects.get(bracelet_id='TEST-MODEL-001')
    self.assertEqual(updated.severity, 'Важкий')
    self.assertEqual(updated.bed_number, '205')
  
  def test_patient_delete(self):
    """Тест: видалення пацієнта"""
    bracelet_id = self.patient.bracelet_id
    self.patient.delete()
    
    with self.assertRaises(Patient.DoesNotExist):
      Patient.objects.get(bracelet_id=bracelet_id)
  
  def test_patient_admission_date(self):
    """Тест: дата прийому автоматично встановлюється"""
    self.assertIsNotNone(self.patient.admission_date)
    time_diff = timezone.now() - self.patient.admission_date
    self.assertLess(time_diff.total_seconds(), 60)


class VitalSignsModelTest(TestCase):
  """Тести для моделі VitalSigns"""
  
  def setUp(self):
    """Підготовка тестових даних"""
    self.patient = Patient.objects.create(
      full_name='Пацієнт для Віталс',
      age=35,
      bracelet_id='VITAL-TEST-001',
      injury_type='Контузія',
      severity='Середній'
    )
    
    self.vital_signs = VitalSigns.objects.create(
      patient_bracelet_id=self.patient.bracelet_id,
      heart_rate=75,
      temperature=36.6,
      blood_pressure_sys=120,
      blood_pressure_dia=80,
      oxygen_saturation=98
    )
  
  def test_vital_signs_creation(self):
    """Тест: створення життєвих показників"""
    self.assertIsNotNone(self.vital_signs._id)
    self.assertEqual(self.vital_signs.patient_bracelet_id, self.patient.bracelet_id)
    self.assertEqual(self.vital_signs.heart_rate, 75)
    print(f" VitalSigns created with ID: {self.vital_signs._id}")
  
  def test_vital_signs_str_method(self):
    """Тест: метод __str__ життєвих показників"""
    result = str(self.vital_signs)
    self.assertIn(self.vital_signs.patient_bracelet_id, result)
  
  def test_vital_signs_fields(self):
    """Тест: всі поля життєвих показників"""
    self.assertEqual(self.vital_signs.heart_rate, 75)
    self.assertEqual(float(self.vital_signs.temperature), 36.6)
    self.assertEqual(self.vital_signs.blood_pressure_sys, 120)
    self.assertEqual(self.vital_signs.blood_pressure_dia, 80)
    self.assertEqual(self.vital_signs.oxygen_saturation, 98)
  
  def test_vital_signs_timestamp(self):
    """Тест: timestamp автоматично встановлюється"""
    self.assertIsNotNone(self.vital_signs.timestamp)
    time_diff = timezone.now() - self.vital_signs.timestamp
    self.assertLess(time_diff.total_seconds(), 60)
  
  def test_multiple_vital_signs_for_patient(self):
    """Тест: кілька вимірювань для одного пацієнта"""
    vital_signs_2 = VitalSigns.objects.create(
      patient_bracelet_id=self.patient.bracelet_id,
      heart_rate=80,
      temperature=36.8,
      blood_pressure_sys=125,
      blood_pressure_dia=82,
      oxygen_saturation=97
    )
    
    all_vitals = VitalSigns.objects.filter(
      patient_bracelet_id=self.patient.bracelet_id
    )
    self.assertEqual(all_vitals.count(), 2)
  
  def test_vital_signs_query_by_bracelet(self):
    """Тест: пошук життєвих показників по bracelet_id"""
    vitals = VitalSigns.objects.filter(
      patient_bracelet_id=self.patient.bracelet_id
    )
    self.assertEqual(vitals.count(), 1)
    self.assertEqual(vitals.first()._id, self.vital_signs._id)
  
  def test_vital_signs_default_blood_pressure(self):
    """Тест: значення тиску за замовчуванням"""
    vital = VitalSigns.objects.create(
      patient_bracelet_id=self.patient.bracelet_id,
      heart_rate=70,
      temperature=36.5,
      oxygen_saturation=99
    )
    self.assertEqual(vital.blood_pressure_sys, 120)
    self.assertEqual(vital.blood_pressure_dia, 80)


class InjuryClassificationModelTest(TestCase):
  """Тести для моделі InjuryClassification"""
  
  def setUp(self):
    """Підготовка тестових даних"""
    self.patient = Patient.objects.create(
      full_name='Пацієнт для Класифікації',
      age=40,
      bracelet_id='CLASS-TEST-001',
      injury_type='Осколкове поранення',
      severity='Важкий'
    )
    
    self.classification = InjuryClassification.objects.create(
      patient_bracelet_id=self.patient.bracelet_id,
      injury_type='Осколкове поранення',
      severity='Важкий',
      diagnosis='Осколкове поранення грудної клітки',
      treatment_plan='Термінова операція, інтенсивна терапія'
    )
  
  def test_classification_creation(self):
    """Тест: створення класифікації"""
    self.assertIsNotNone(self.classification._id)
    self.assertEqual(
      self.classification.patient_bracelet_id, 
      self.patient.bracelet_id
    )
    print(f" Classification created with ID: {self.classification._id}")
  
  def test_classification_str_method(self):
    """Тест: метод __str__ класифікації"""
    expected = f"{self.classification.injury_type} - {self.classification.severity}"
    self.assertEqual(str(self.classification), expected)
  
  def test_classification_fields(self):
    """Тест: всі поля класифікації"""
    self.assertEqual(self.classification.injury_type, 'Осколкове поранення')
    self.assertEqual(self.classification.severity, 'Важкий')
    self.assertEqual(
      self.classification.diagnosis, 
      'Осколкове поранення грудної клітки'
    )
    self.assertIn('операція', self.classification.treatment_plan)

  def test_classification_date(self):
    """Тест: дата класифікації автоматично встановлюється"""
    self.assertIsNotNone(self.classification.classification_date)
    time_diff = timezone.now() - self.classification.classification_date
    self.assertLess(time_diff.total_seconds(), 60)
  
  def test_multiple_classifications_for_patient(self):
    """Тест: кілька класифікацій для одного пацієнта"""
    classification_2 = InjuryClassification.objects.create(
      patient_bracelet_id=self.patient.bracelet_id,
      injury_type='Осколкове поранення',
      severity='Критичний',
      diagnosis='Ускладнення: внутрішня кровотеча',
      treatment_plan='Повторна операція'
    )
    
    all_classifications = InjuryClassification.objects.filter(
      patient_bracelet_id=self.patient.bracelet_id
    )
    self.assertEqual(all_classifications.count(), 2)


class MedicalStaffModelTest(TestCase):
  """Тести для моделі MedicalStaff"""
  
  def setUp(self):
    """Підготовка тестових даних"""
    self.staff = MedicalStaff.objects.create(
      username='testdoctor',
      full_name='Тестовий Лікар',
      role='Лікар',
      email='doctor@test.com',
      phone='+380501234567',
      specialization='Хірургія',
      is_active=True
    )
    self.staff.set_password('testpass123')
    self.staff.save()
  
  def test_staff_creation(self):
    """Тест: створення медперсоналу"""
    self.assertIsNotNone(self.staff._id)
    self.assertEqual(self.staff.username, 'testdoctor')
    self.assertEqual(self.staff.full_name, 'Тестовий Лікар')
    print(f" Staff created with ID: {self.staff._id}")
  
  def test_staff_str_method(self):
    """Тест: метод __str__ медперсоналу"""
    expected = f"{self.staff.full_name} ({self.staff.role})"
    self.assertEqual(str(self.staff), expected)
  
  def test_staff_password_hashing(self):
    """Тест: хешування пароля"""
    self.assertNotEqual(self.staff.password, 'testpass123')
    self.assertTrue(self.staff.check_password('testpass123'))
    self.assertFalse(self.staff.check_password('wrongpassword'))
  
  def test_staff_unique_username(self):
    """Тест: унікальність username"""
    with self.assertRaises(Exception):
        MedicalStaff.objects.create(
          username='testdoctor',
          full_name='Інший Лікар',
          role='Медсестра'
        )
  
  def test_staff_fields(self):
    """Тест: всі поля медперсоналу"""
    self.assertEqual(self.staff.role, 'Лікар')
    self.assertEqual(self.staff.email, 'doctor@test.com')
    self.assertEqual(self.staff.phone, '+380501234567')
    self.assertEqual(self.staff.specialization, 'Хірургія')
    self.assertTrue(self.staff.is_active)
  
  def test_staff_default_avatar(self):
    """Тест: аватар за замовчуванням"""
    self.assertEqual(self.staff.avatar, '👤')
  
  def test_staff_registration_date(self):
    """Тест: дата реєстрації автоматично встановлюється"""
    self.assertIsNotNone(self.staff.registration_date)
    time_diff = timezone.now() - self.staff.registration_date
    self.assertLess(time_diff.total_seconds(), 60)
    
    def test_staff_update_last_login(self):
      """Тест: оновлення часу останнього входу"""
      self.staff.last_login = timezone.now()
      self.staff.save()
      
      updated_staff = MedicalStaff.objects.get(username='testdoctor')
      self.assertIsNotNone(updated_staff.last_login)


class DatabaseRelationshipsTest(TestCase):
  """Тести зв'язків між моделями"""
  
  def setUp(self):
    """Підготовка тестових даних"""
    self.patient = Patient.objects.create(
      full_name='Тест Зв\'язки',
      age=32,
      bracelet_id='REL-TEST-001',
      injury_type='Переломи',
      severity='Середній'
    )
  
  def test_patient_vitals_relationship(self):
    """Тест: зв'язок пацієнт-віталс через bracelet_id"""
    for i in range(3):
      VitalSigns.objects.create(
        patient_bracelet_id=self.patient.bracelet_id,
        heart_rate=70 + i * 5,
        temperature=36.5 + i * 0.1,
        blood_pressure_sys=120,
        blood_pressure_dia=80,
        oxygen_saturation=98
      )
    
    vitals = VitalSigns.objects.filter(
      patient_bracelet_id=self.patient.bracelet_id
    )
    self.assertEqual(vitals.count(), 3)
  
  def test_patient_classification_relationship(self):
    """Тест: зв'язок пацієнт-класифікація через bracelet_id"""
    InjuryClassification.objects.create(
      patient_bracelet_id=self.patient.bracelet_id,
      injury_type=self.patient.injury_type,
      severity=self.patient.severity,
      diagnosis='Перелом стегнової кістки'
    )
    
    classifications = InjuryClassification.objects.filter(
      patient_bracelet_id=self.patient.bracelet_id
    )
    self.assertEqual(classifications.count(), 1)
    self.assertEqual(
      classifications.first().patient_bracelet_id,
      self.patient.bracelet_id
    )
  
  def test_cascade_deletion_simulation(self):
    """Тест: видалення пов'язаних даних"""
    VitalSigns.objects.create(
      patient_bracelet_id=self.patient.bracelet_id,
      heart_rate=75,
      temperature=36.6,
      blood_pressure_sys=120,
      blood_pressure_dia=80,
      oxygen_saturation=98
    )
    
    InjuryClassification.objects.create(
      patient_bracelet_id=self.patient.bracelet_id,
      injury_type=self.patient.injury_type,
      severity=self.patient.severity,
      diagnosis='Тест'
    )
    
    bracelet_id = self.patient.bracelet_id
    self.patient.delete()
    
    vitals_count = VitalSigns.objects.filter(
      patient_bracelet_id=bracelet_id
    ).count()
    
    print(f"Vitals after patient deletion: {vitals_count}")


class PatientQueryTest(TestCase):
  """Тести запитів до пацієнтів"""
  
  def setUp(self):
    """Створюємо тестових пацієнтів"""
    injury_types = ['Вогнепальне поранення', 'Осколкове поранення', 'Контузія']
    severities = ['Легкий', 'Середній', 'Важкий']
    
    for i in range(10):
      Patient.objects.create(
        full_name=f'Пацієнт {i+1}',
        age=20 + i,
        bracelet_id=f'QUERY-{i+1:03d}',
        injury_type=injury_types[i % 3],
        severity=severities[i % 3],
        bed_number=f'{100 + i}'
      )
  
  def test_filter_by_injury_type(self):
    """Тест: фільтр по типу поранення"""
    gunshot_patients = Patient.objects.filter(
      injury_type='Вогнепальне поранення'
    )
    self.assertGreater(gunshot_patients.count(), 0)
  
  def test_filter_by_severity(self):
    """Тест: фільтр по важкості"""
    severe_patients = Patient.objects.filter(severity='Важкий')
    self.assertGreater(severe_patients.count(), 0)
  
  def test_count_patients(self):
    """Тест: підрахунок пацієнтів"""
    total = Patient.objects.count()
    self.assertEqual(total, 10)
  
  def test_order_patients(self):
    """Тест: сортування пацієнтів"""
    patients = Patient.objects.all().order_by('age')
    ages = [p.age for p in patients]
    self.assertEqual(ages, sorted(ages))