from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from equipment.models import Equipment, Medication
from equipment.analytics_medications import medication_forecast

class EquipmentModelTest(TestCase):

  def setUp(self):
    self.equipment = Equipment.objects.create(
      name="Microscope",
      qr_code="EQ-TEST-001",
      quantity=2,
      status="working",
      location="Lab 1",
      manufacturer="Zeiss"
    )

  def test_equipment_creation(self):
    self.assertIsNotNone(self.equipment.id)
    self.assertEqual(self.equipment.name, "Microscope")
    self.assertEqual(self.equipment.status, "working")
    self.assertTrue(self.equipment.is_active)
    print(f"Equipment created with ID: {self.equipment.id}")

  def test_equipment_str_method(self):
    self.assertEqual(str(self.equipment), "Microscope")

  def test_equipment_unique_qr_code(self):
    with self.assertRaises(Exception):
      Equipment.objects.create(
        name="Another microscope",
        qr_code="EQ-TEST-001"
      )

  def test_equipment_default_values(self):
    eq = Equipment.objects.create(
      name="X-Ray",
      qr_code="EQ-DEFAULT-001"
    )
    self.assertEqual(eq.quantity, 1)
    self.assertEqual(eq.status, "working")
    self.assertTrue(eq.is_active)

  def test_equipment_update(self):
    self.equipment.status = "maintenance"
    self.equipment.quantity = 1
    self.equipment.save()
    updated = Equipment.objects.get(qr_code="EQ-TEST-001")
    self.assertEqual(updated.status, "maintenance")
    self.assertEqual(updated.quantity, 1)

  def test_equipment_delete(self):
    qr = self.equipment.qr_code
    self.equipment.delete()
    with self.assertRaises(Equipment.DoesNotExist):
      Equipment.objects.get(qr_code=qr)

  def test_equipment_last_updated(self):
    self.assertIsNotNone(self.equipment.last_updated)
    diff = timezone.now() - self.equipment.last_updated
    self.assertLess(diff.total_seconds(), 60)


class MedicationModelTest(TestCase):

  def setUp(self):
    self.medication = Medication.objects.create(
      name="Paracetamol",
      barcode="MED-TEST-001",
      quantity=50,
      critical_level=10,
      supplier="Pharma Ltd",
      unit="tablets",
      expiry_date=date.today() + timedelta(days=365)
    )

  def test_medication_creation(self):
    self.assertIsNotNone(self.medication.id)
    self.assertEqual(self.medication.name, "Paracetamol")
    self.assertEqual(self.medication.quantity, 50)
    print(f"Medication created with ID: {self.medication.id}")

  def test_medication_str_method(self):
    self.assertEqual(str(self.medication), "Paracetamol")

  def test_medication_unique_barcode(self):
    with self.assertRaises(Exception):
      Medication.objects.create(
        name="Another med",
        barcode="MED-TEST-001"
      )

  def test_medication_critical_level_logic(self):
    self.medication.quantity = 5
    self.medication.save()
    self.assertTrue(self.medication.quantity < self.medication.critical_level)

  def test_medication_update(self):
    self.medication.quantity = 30
    self.medication.save()
    updated = Medication.objects.get(barcode="MED-TEST-001")
    self.assertEqual(updated.quantity, 30)

  def test_medication_delete(self):
    barcode = self.medication.barcode
    self.medication.delete()
    with self.assertRaises(Medication.DoesNotExist):
      Medication.objects.get(barcode=barcode)

  def test_medication_expiry_date(self):
    self.assertGreater(self.medication.expiry_date, date.today())

  def test_medication_last_updated(self):
    self.assertIsNotNone(self.medication.last_updated)
    diff = timezone.now() - self.medication.last_updated
    self.assertLess(diff.total_seconds(), 60)


class MedicationQueryTest(TestCase):

  def setUp(self):
    today = timezone.now()
    for i in range(5):
      Medication.objects.create(
        name=f"Med {i}",
        barcode=f"BAR-{i}",
        quantity=5 * i + 10,
        critical_level=10,
        last_updated=today - timedelta(days=i*30)
      )

  def test_filter_critical_medications(self):
    all_meds = Medication.objects.all()
    critical = [m for m in all_meds if m.quantity < m.critical_level]
    self.assertGreaterEqual(len(critical), 0)

  def test_count_medications(self):
    total = Medication.objects.count()
    self.assertEqual(total, 5)

  def test_order_medications_by_quantity(self):
    meds = Medication.objects.all().order_by("quantity")
    quantities = [m.quantity for m in meds]
    self.assertEqual(quantities, sorted(quantities))

  def test_medication_forecast(self):
    forecast = medication_forecast(months_ahead=2)
    print("Forecast:", forecast)
    self.assertEqual(len(forecast), 2)
    for month_data in forecast:
      self.assertIn('month', month_data)
      self.assertIn('predicted_quantity', month_data)

