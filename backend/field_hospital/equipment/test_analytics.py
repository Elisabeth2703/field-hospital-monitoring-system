from django.test import TestCase
from unittest.mock import patch
import pandas as pd
import numpy as np

from equipment.analytics import (
    equipment_status_analysis,
    low_quantity_equipment,
    equipment_forecast
)

from equipment.analytics_medications import (
    medication_basic_stats,
    medication_forecast
)


class EquipmentAnalyticsTest(TestCase):
    """Тести аналітики обладнання (pandas + numpy + sklearn)"""

    @patch('equipment.analytics.Equipment')
    def test_equipment_status_analysis(self, MockEquipment):
        """Тест аналізу статусів обладнання"""

        mock_data = [
            {'name': 'EQ1', 'status': 'working', 'quantity': 5},
            {'name': 'EQ2', 'status': 'working', 'quantity': 2},
            {'name': 'EQ3', 'status': 'broken', 'quantity': 1},
        ]

        MockEquipment.objects.all().values.return_value = mock_data

        result = equipment_status_analysis()

        self.assertEqual(result['working'], 2)
        self.assertEqual(result['broken'], 1)

    @patch('equipment.analytics.Equipment')
    def test_low_quantity_equipment(self, MockEquipment):
        """Тест виявлення обладнання з малою кількістю"""

        mock_data = [
            {'name': 'EQ1', 'quantity': 1},
            {'name': 'EQ2', 'quantity': 5},
            {'name': 'EQ3', 'quantity': 2},
        ]

        MockEquipment.objects.all().values.return_value = mock_data

        df = low_quantity_equipment(threshold=2)

        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
        self.assertIn('name', df.columns)
        self.assertIn('quantity', df.columns)

    @patch('equipment.analytics.Equipment')
    def test_equipment_forecast(self, MockEquipment):
        """Тест прогнозування обладнання"""

        mock_data = [
            {'purchase_date': '2024-01-01', 'quantity': 5},
            {'purchase_date': '2024-02-01', 'quantity': 7},
            {'purchase_date': '2024-03-01', 'quantity': 6},
        ]

        MockEquipment.objects.all().values.return_value = mock_data

        forecast = equipment_forecast(months_ahead=2)

        self.assertEqual(len(forecast), 2)
        self.assertTrue(all(isinstance(x, (float, np.floating)) for x in forecast))


class MedicationAnalyticsTest(TestCase):
    """Тести аналітики медикаментів"""

    @patch('equipment.analytics_medications.db')
    def test_medication_basic_stats(self, mock_db):
        """Тест базової статистики медикаментів"""

        mock_db.get_all_medications.return_value = [
            {
                'name': 'Med1',
                'quantity': 5,
                'critical_level': 3,
                'expiry_date': '2026-01-01'
            },
            {
                'name': 'Med2',
                'quantity': 2,
                'critical_level': 3,
                'expiry_date': '2023-01-01'
            }
        ]

        stats = medication_basic_stats()

        self.assertEqual(stats['total_items'], 2)
        self.assertEqual(stats['total_quantity'], 7)
        self.assertEqual(stats['critical_count'], 1)
        self.assertGreaterEqual(stats['expired_count'], 1)

        self.assertEqual(stats['sufficient_count'], 1)

    @patch('equipment.analytics_medications.db')
    def test_medication_forecast(self, mock_db):
        """Тест прогнозування кількості медикаментів"""

        mock_db.get_all_medications.return_value = [
    {
        'quantity': 10,
        'critical_level': 3,
        'last_update': pd.Timestamp('2024-01-01')
    },
    {
        'quantity': 8,
        'critical_level': 3,
        'last_update': pd.Timestamp('2024-02-01')
    },
    {
        'quantity': 6,
        'critical_level': 3,
        'last_update': pd.Timestamp('2024-03-01')
    }
]


        forecast = medication_forecast(months_ahead=2)

        self.assertEqual(len(forecast), 2)
        self.assertIn('month', forecast[0])
        self.assertIn('predicted_quantity', forecast[0])
