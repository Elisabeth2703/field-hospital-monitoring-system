from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from datetime import date

class EquipmentViewsTest(TestCase):

  def setUp(self):
    self.client = Client()

  @patch('equipment.views.mongo.get_all_equipment')
  def test_equipment_list_view(self, mock_get_all):
    mock_get_all.return_value = [
      {'name': 'Microscope', 'qr_code': 'EQ-001', 'quantity': 2, 'is_deleted': False}
    ]
    response = self.client.get(reverse('equipment_list'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'equipment/equipment_list.html')
    self.assertIn('equipment', response.context)

  @patch('equipment.views.mongo.create_equipment')
  def test_equipment_create_view(self, mock_create):
    data = {
      'name': 'X-Ray',
      'qr_code': 'EQ-NEW-001',
      'quantity': 1,
      'status': 'working'
    }
    response = self.client.post(reverse('equipment_create'), data=data)
    self.assertEqual(response.status_code, 302)
    mock_create.assert_called_once()

  @patch('equipment.views.db_manager.get_equipment')
  def test_equipment_detail_view(self, mock_get):
    mock_get.return_value = {
      'name': 'Analyzer',
      'qr_code': 'EQ-DET-001',
      'quantity': 3
    }
    response = self.client.get(
      reverse('equipment_detail', kwargs={'qr_code': 'EQ-DET-001'})
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('equipment', response.context)

  @patch('equipment.views.db_manager.get_equipment')
  @patch('equipment.views.db_manager.update_equipment')
  def test_equipment_update_view(self, mock_update, mock_get):
    mock_get.return_value = {'qr_code': 'EQ-UPD-001'}
    data = {
      'name': 'Updated device',
      'quantity': 5,
      'status': 'maintenance'
    }
    response = self.client.post(
      reverse('equipment_update', kwargs={'qr_code': 'EQ-UPD-001'}),
      data=data
    )
    self.assertEqual(response.status_code, 302)
    mock_update.assert_called_once()

  @patch('equipment.views.mongo.get_equipment')
  @patch('equipment.views.mongo.update_equipment')
  def test_equipment_delete_view(self, mock_update, mock_get):
    mock_get.return_value = {'qr_code': 'EQ-DEL-001'}
    response = self.client.post(
      reverse('equipment_delete', kwargs={'qr_code': 'EQ-DEL-001'})
    )
    self.assertEqual(response.status_code, 302)
    mock_update.assert_called_once()


class MedicationViewsTest(TestCase):

  def setUp(self):
    self.client = Client()

  @patch('equipment.views.db_manager.get_all_medications')
  def test_medication_list_view(self, mock_get_all):
    mock_get_all.return_value = [
      {'name': 'Aspirin', 'barcode': 'MED-001', 'quantity': 50}
    ]
    response = self.client.get(reverse('medication_list'))
    self.assertEqual(response.status_code, 200)
    self.assertTemplateUsed(response, 'equipment/medication_list.html')

  @patch('equipment.views.db_manager.get_medication')
  @patch('equipment.views.db_manager.get_medication_logs')
  @patch('equipment.views.db_manager.get_medication_usage_trend')
  def test_medication_detail_view(self, mock_trend, mock_logs, mock_get):
    mock_get.return_value = {
      'name': 'Paracetamol',
      'barcode': 'MED-DET-001',
      '_id': '123'
    }
    mock_logs.return_value = []
    mock_trend.return_value = []
    response = self.client.get(
      reverse('medication_detail', kwargs={'barcode': 'MED-DET-001'})
    )
    self.assertEqual(response.status_code, 200)
    self.assertIn('medication', response.context)

  @patch('equipment.views.db_manager.get_medication')
  @patch('equipment.views.db_manager.create_medication')
  def test_medication_create_view(self, mock_create, mock_get):
    mock_get.return_value = None
    data = {
      'name': 'Ibuprofen',
      'barcode': 'MED-NEW-001',
      'quantity': 100,
      'critical_level': 20,
      'unit': 'tablets',
      'expiry_date': date.today().isoformat()
    }
    response = self.client.post(reverse('medication_create'), data=data)
    self.assertEqual(response.status_code, 302)
    mock_create.assert_called_once()

  @patch('equipment.views.db_manager.delete_medication')
  def test_medication_delete_view(self, mock_delete):
    mock_delete.return_value = 1
    response = self.client.post(
      reverse('medication_delete', kwargs={'barcode': 'MED-DEL-001'})
    )
    self.assertEqual(response.status_code, 302)


class APITest(TestCase):

  def setUp(self):
    self.client = Client()

  @patch('equipment.views.db_manager.get_medication_statistics')
  def test_api_medication_statistics(self, mock_stats):
    mock_stats.return_value = {'total': 10}
    response = self.client.get(reverse('api_medication_stats'))
    self.assertEqual(response.status_code, 200)
    self.assertIn('total', response.json())

  @patch('equipment.views.db_manager.get_critical_medications')
  def test_api_critical_medications(self, mock_critical):
    mock_critical.return_value = [
      {'name': 'CriticalMed', '_id': '123'}
    ]
    response = self.client.get(reverse('api_critical_meds'))
    self.assertEqual(response.status_code, 200)
    self.assertIsInstance(response.json(), list)

