from django.test import TestCase, Client
from django.utils import timezone
from datetime import timedelta
from patients.models import Patient, VitalSigns, InjuryClassification, MedicalStaff


class FullWorkflowIntegrationTest(TestCase):
  """Тести повних робочих процесів"""
  
  def setUp(self):
    """Підготовка даних для тестів"""
    self.client = Client()
    
    try:
      self.staff = MedicalStaff.objects.create(
        username='testdoctor',
        full_name='Test Doctor',
        role='Лікар',
        email='doctor@test.com'
      )
      self.staff.set_password('testpass123')
      self.staff.save()
    except Exception as e:
      print(f"Staff creation: {e}")
  
  def test_complete_patient_registration_workflow(self):
    """Тест повного процесу реєстрації пацієнта"""
    
    print("\n=== Starting Complete Patient Registration Workflow Test ===")
    
    print("Step 1: Creating patient...")
    patient = Patient.objects.create(
      full_name='Іван Петренко',
      age=30,
      bracelet_id='TEST-001',
      injury_type='Вогнепальне поранення',
      severity='Середній',
      blood_type='A+',
      bed_number='101',
      status='На лікуванні'
    )
    
    self.assertIsNotNone(patient._id)
    self.assertEqual(patient.full_name, 'Іван Петренко')
    self.assertEqual(patient.bracelet_id, 'TEST-001')
    print(f" Patient created with bracelet_id: {patient.bracelet_id}")
    
    print("Step 2: Creating vital signs...")
    vital_sign = VitalSigns.objects.create(
      patient_bracelet_id=patient.bracelet_id,
      heart_rate=75,
      temperature=36.6,
      blood_pressure_sys=120,
      blood_pressure_dia=80,
      oxygen_saturation=98
    )
    
    self.assertIsNotNone(vital_sign._id)
    print(f" VitalSigns created for bracelet: {vital_sign.patient_bracelet_id}")
    
    print("Step 3: Verifying vital signs in database...")
    vital_signs = VitalSigns.objects.filter(
      patient_bracelet_id=patient.bracelet_id
    )
    
    print(f"Found {vital_signs.count()} vital signs records")
    
    self.assertEqual(vital_signs.count(), 1, 
      f"Expected 1 vital sign record, found {vital_signs.count()}")
    
    print("Step 4: Checking vital signs details...")
    retrieved = vital_signs.first()
    self.assertIsNotNone(retrieved)
    self.assertEqual(retrieved.heart_rate, 75)
    self.assertEqual(retrieved.blood_pressure_sys, 120)
    self.assertEqual(retrieved.blood_pressure_dia, 80)
    self.assertEqual(float(retrieved.temperature), 36.6)
    self.assertEqual(retrieved.oxygen_saturation, 98)
    
    print(" All vital signs details correct")
    
    print("Step 5: Verifying patient-vitals relationship via bracelet_id...")
    self.assertEqual(retrieved.patient_bracelet_id, patient.bracelet_id)
    
    print(" Patient-vitals relationship verified via bracelet_id")
    
    print("Step 6: Creating injury classification...")
    classification = InjuryClassification.objects.create(
      patient_bracelet_id=patient.bracelet_id,
      injury_type=patient.injury_type,
      severity=patient.severity,
      diagnosis='Вогнепальне поранення нижньої кінцівки',
      treatment_plan='Хірургічне втручання, антибіотики'
    )
    
    self.assertIsNotNone(classification._id)
    print(f" Injury classification created")
    
    print("=== Test Completed Successfully ===\n")
  
  def test_multiple_patients_with_vitals(self):
    """Тест створення кількох пацієнтів з віталами"""
    
    patients_data = [
      {'name': 'Петро Петренко', 'bracelet': 'BR-001', 'hr': 70},
      {'name': 'Марія Марієнко', 'bracelet': 'BR-002', 'hr': 80},
      {'name': 'Олена Оленко', 'bracelet': 'BR-003', 'hr': 75},
    ]
    
    for data in patients_data:
      patient = Patient.objects.create(
        full_name=data['name'],
        age=30,
        bracelet_id=data['bracelet'],
        injury_type='Переломи',
        severity='Легкий'
      )
      
      VitalSigns.objects.create(
        patient_bracelet_id=patient.bracelet_id,
        heart_rate=data['hr'],
        temperature=36.6,
        blood_pressure_sys=120,
        blood_pressure_dia=80,
        oxygen_saturation=98
      )
    
    self.assertEqual(Patient.objects.count(), 3)
    self.assertEqual(VitalSigns.objects.count(), 3)
    
    for patient in Patient.objects.all():
      vitals_count = VitalSigns.objects.filter(
        patient_bracelet_id=patient.bracelet_id
      ).count()
      self.assertEqual(vitals_count, 1)
  
  def test_injury_classification_workflow(self):
    """Тест класифікації поранень"""
    
    injury_types = [
      'Вогнепальне поранення',
      'Осколкове поранення',
      'Контузія',
      'Опіки'
    ]
    
    for i, injury_type in enumerate(injury_types):
      patient = Patient.objects.create(
        full_name=f'Пацієнт {i+1}',
        age=25,
        bracelet_id=f'INJ-{i+1:03d}',
        injury_type=injury_type,
        severity='Середній'
      )
      
      InjuryClassification.objects.create(
        patient_bracelet_id=patient.bracelet_id,
        injury_type=injury_type,
        severity='Середній',
        diagnosis=f'Діагноз для {injury_type}'
      )
    
    self.assertEqual(Patient.objects.count(), 4)
    self.assertEqual(InjuryClassification.objects.count(), 4)
    
    for injury_type in injury_types:
      count = InjuryClassification.objects.filter(
        injury_type=injury_type
      ).count()
      self.assertEqual(count, 1)