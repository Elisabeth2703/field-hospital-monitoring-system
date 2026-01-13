from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from datetime import date

class MedicationIntegrationTest(TestCase):

  def setUp(self):
    self.client = Client()

  @patch('equipment.views.db_manager')
  def test_full_medication_workflow(self, mock_db):

    print("\n=== Medication Full Workflow Test ===")

    mock_db.get_medication.return_value = None
    mock_db.create_medication.return_value = "mock_id"

    create_data = {
      'name': 'TestMed',
      'barcode': 'MED-INT-001',
      'quantity': 100,
      'critical_level': 20,
      'unit': 'tablets',
      'expiry_date': date.today().isoformat()
    }

    response = self.client.post(
      reverse('medication_create'),
      data=create_data
    )

    self.assertEqual(response.status_code, 302)
    mock_db.create_medication.assert_called_once()
    print(" Step 1 OK: Medication created")

    mock_db.get_medication.return_value = {
      '_id': '123',
      'name': 'TestMed',
      'barcode': 'MED-INT-001',
      'quantity': 100
    }
    mock_db.get_medication_logs.return_value = []
    mock_db.get_medication_usage_trend.return_value = []

    response = self.client.get(
      reverse('medication_detail', kwargs={'barcode': 'MED-INT-001'})
    )

    self.assertIn(response.status_code, [200, 302])
    print(" Step 2 OK: Medication detail viewed")

    update_data = {
      'name': 'TestMed Updated',
      'quantity': 80,
      'critical_level': 20,
      'unit': 'tablets'
    }

    response = self.client.post(
      reverse('medication_update', kwargs={'barcode': 'MED-INT-001'}),
      data=update_data
    )

    self.assertEqual(response.status_code, 302)
    mock_db.update_medication.assert_called_once()
    print(" Step 3 OK: Medication updated")

    mock_db.delete_medication.return_value = 1

    response = self.client.post(
      reverse('medication_delete', kwargs={'barcode': 'MED-INT-001'})
    )

    self.assertEqual(response.status_code, 302)
    mock_db.delete_medication.assert_called_once()
    print(" Step 4 OK: Medication deleted")

    print("=== Medication Workflow Completed ===\n")


class EquipmentIntegrationTest(TestCase):

  def setUp(self):
    self.client = Client()

  @patch('equipment.views.mongo')
  @patch('equipment.views.db_manager')
  def test_full_equipment_workflow(self, mock_db, mock_mongo):

    print("\n=== Equipment Full Workflow Test ===")

    create_data = {
      'name': 'Analyzer',
      'qr_code': 'EQ-INT-001',
      'quantity': 3,
      'status': 'working'
    }

    response = self.client.post(
      reverse('equipment_create'),
      data=create_data
    )

    self.assertEqual(response.status_code, 302)
    mock_mongo.create_equipment.assert_called_once()
    print(" Step 1 OK: Equipment created")

    mock_mongo.get_all_equipment.return_value = [
      {
        'name': 'Analyzer',
        'qr_code': 'EQ-INT-001',
        'quantity': 3,
        'is_deleted': False
      }
    ]

    response = self.client.get(reverse('equipment_list'))
    self.assertEqual(response.status_code, 200)
    print(" Step 2 OK: Equipment list viewed")

    mock_db.get_equipment.return_value = {
      'name': 'Analyzer',
      'qr_code': 'EQ-INT-001',
      'quantity': 3
    }

    response = self.client.get(
      reverse('equipment_detail', kwargs={'qr_code': 'EQ-INT-001'})
    )

    self.assertIn(response.status_code, [200, 302])
    print(" Step 3 OK: Equipment detail viewed")

    update_data = {
      'name': 'Analyzer Updated',
      'quantity': 2,
      'status': 'maintenance'
    }

    response = self.client.post(
      reverse('equipment_update', kwargs={'qr_code': 'EQ-INT-001'}),
      data=update_data
    )

    self.assertEqual(response.status_code, 302)
    mock_db.update_equipment.assert_called_once()
    print(" Step 4 OK: Equipment updated")

    mock_mongo.get_equipment.return_value = {
      'qr_code': 'EQ-INT-001'
    }

    response = self.client.post(
      reverse('equipment_delete', kwargs={'qr_code': 'EQ-INT-001'})
    )

    self.assertEqual(response.status_code, 302)
    mock_mongo.update_equipment.assert_called_once()
    print(" Step 5 OK: Equipment logically deleted")

    print("=== Equipment Workflow Completed ===\n")


class StatisticsIntegrationTest(TestCase):

  def setUp(self):
    self.client = Client()

  @patch('equipment.views.db_manager.get_medication_statistics')
  def test_medication_statistics_api(self, mock_stats):

    mock_stats.return_value = {
      'total_items': 10,
      'critical_count': 2
    }

    response = self.client.get(reverse('api_medication_stats'))
    self.assertEqual(response.status_code, 200)
    self.assertIn('total_items', response.json())
    print(" Medication statistics API OK")

  @patch('equipment.views.db_manager.get_critical_medications')
  def test_critical_medications_api(self, mock_critical):

    mock_critical.return_value = [
      {'name': 'CriticalMed', '_id': '123'}
    ]

    response = self.client.get(reverse('api_critical_meds'))
    self.assertEqual(response.status_code, 200)
    self.assertTrue(isinstance(response.json(), list))
    print(" Critical medications API OK")
