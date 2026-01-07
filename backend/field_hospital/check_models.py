from patients.models import Patient, VitalSigns
from django.utils import timezone

patient = Patient.objects.create(
    first_name='Test',
    last_name='Patient',
    date_of_birth='1990-01-01',
    gender='M',
    admission_date=timezone.now()
)
print(f"✅ Patient створено: ID={patient.id}")

vital = VitalSigns.objects.create(
    patient=patient,
    heart_rate=75,
    blood_pressure_systolic=120,
    blood_pressure_diastolic=80,
    temperature=36.6,
    respiratory_rate=18,
    oxygen_saturation=98,
    recorded_at=timezone.now()
)
print(f"✅ VitalSigns створено: ID={vital.id}")

vitals = VitalSigns.objects.filter(patient=patient)
print(f"Знайдено {vitals.count()} VitalSigns")

try:
    print(f"patient.vital_signs: {patient.vital_signs.count()}")
except:
    print("⚠️ related_name 'vital_signs' не працює")
    try:
        print(f"patient.vitalsigns_set: {patient.vitalsigns_set.count()}")
    except:
        print("❌ Не можу отримати vital signs")

vital.delete()
patient.delete()
print("✅ Тестові дані видалено")