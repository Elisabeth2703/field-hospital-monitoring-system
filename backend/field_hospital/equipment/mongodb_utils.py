from pymongo import MongoClient
from datetime import datetime, timedelta
import json

class MongoDBManager:
    """Клас для управління MongoDB операціями"""
    
    def __init__(self):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client['medical_system']
        self.medications = self.db['medications']
        self.equipment = self.db['equipment']
        self.medication_logs = self.db['medication_logs']
    
    # ============ CRUD операції для медикаментів ============
    
    def create_medication(self, medication_data):
        """Створення нового медикаменту"""
        medication_data['last_updated'] = datetime.now()
        result = self.medications.insert_one(medication_data)
        return result.inserted_id
    
    def get_medication(self, barcode):
        """Отримання медикаменту за штрих-кодом"""
        return self.medications.find_one({'barcode': barcode})
    
    def get_all_medications(self):
        """Отримання всіх медикаментів"""
        return list(self.medications.find())
    
    def update_medication(self, barcode, update_data):
        """Оновлення медикаменту"""
        update_data['last_updated'] = datetime.now()
        result = self.medications.update_one(
            {'barcode': barcode},
            {'$set': update_data}
        )
        return result.modified_count
    
    def delete_medication(self, barcode):
        """Видалення медикаменту"""
        result = self.medications.delete_one({'barcode': barcode})
        return result.deleted_count
    
    # ============ CRUD операції для обладнання ============
    
    def create_equipment(self, equipment_data):
        """Створення нового обладнання"""
        equipment_data['last_updated'] = datetime.now()
        equipment_data['maintenance_history'] = []
        result = self.equipment.insert_one(equipment_data)
        return result.inserted_id
    
    def get_equipment(self, qr_code):
        """Отримання обладнання за QR-кодом"""
        return self.equipment.find_one({'qr_code': qr_code})
    
    def get_all_equipment(self):
        """Отримання всього обладнання"""
        return list(self.equipment.find())
    
    def update_equipment(self, qr_code, update_data):
        """Оновлення обладнання"""
        update_data['last_updated'] = datetime.now()
        result = self.equipment.update_one(
            {'qr_code': qr_code},
            {'$set': update_data}
        )
        return result.modified_count
    
    def delete_equipment(self, qr_code):
        """Видалення обладнання"""
        result = self.equipment.delete_one({'qr_code': qr_code})
        return result.deleted_count
    
    # ============ Розширені запити ============
    
    def get_critical_medications(self):
        """Отримання медикаментів з критично низьким запасом"""
        return list(self.medications.find({
            '$expr': {'$lte': ['$quantity', '$critical_level']}
        }))
    
    def get_expired_medications(self):
        """Отримання прострочених медикаментів"""
        today = datetime.now().date()
        return list(self.medications.find({
            'expiry_date': {'$lt': today.isoformat()}
        }))
    
    def get_equipment_by_status(self, status):
        """Отримання обладнання за статусом"""
        return list(self.equipment.find({'status': status}))
    
    def get_equipment_needing_maintenance(self):
        """Обладнання, що потребує обслуговування (> 6 місяців)"""
        six_months_ago = (datetime.now() - timedelta(days=180)).date()
        return list(self.equipment.find({
            'last_maintenance': {'$lt': six_months_ago.isoformat()}
        }))
    
    # ============ Агрегація та аналіз ============
    
    def get_medication_statistics(self):
        """Статистика по медикаментах"""
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_medications': {'$sum': 1},
                    'total_quantity': {'$sum': '$quantity'},
                    'critical_count': {
                        '$sum': {
                            '$cond': [
                                {'$lte': ['$quantity', '$critical_level']},
                                1,
                                0
                            ]
                        }
                    }
                }
            }
        ]
        result = list(self.medications.aggregate(pipeline))
        return result[0] if result else {}
    
    def get_equipment_statistics(self):
        """Статистика по обладнанню"""
        pipeline = [
            {
                '$group': {
                    '_id': '$status',
                    'count': {'$sum': 1},
                    'total_quantity': {'$sum': '$quantity'}
                }
            }
        ]
        return list(self.equipment.aggregate(pipeline))
    
    def get_medication_usage_trend(self, barcode, days=30):
        """Тренд використання медикаменту за останні N днів"""
        start_date = datetime.now() - timedelta(days=days)
        pipeline = [
            {
                '$match': {
                    'medication_barcode': barcode,
                    'timestamp': {'$gte': start_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        '$dateToString': {
                            'format': '%Y-%m-%d',
                            'date': '$timestamp'
                        }
                    },
                    'total_change': {'$sum': '$quantity_change'},
                    'actions': {'$push': '$action'}
                }
            },
            {
                '$sort': {'_id': 1}
            }
        ]
        return list(self.medication_logs.aggregate(pipeline))
    
    # ============ Логування ============
    
    def log_medication_action(self, barcode, action, quantity_change, user='', notes=''):
        """Логування дій з медикаментами"""
        log_entry = {
            'medication_barcode': barcode,
            'action': action,
            'quantity_change': quantity_change,
            'timestamp': datetime.now(),
            'user': user,
            'notes': notes
        }
        result = self.medication_logs.insert_one(log_entry)
        return result.inserted_id
    
    def get_medication_logs(self, barcode=None, limit=50):
        """Отримання логів медикаментів"""
        query = {'medication_barcode': barcode} if barcode else {}
        return list(self.medication_logs.find(query).sort('timestamp', -1).limit(limit))
    
    # ============ Пошук та фільтрація ============
    
    def search_medications(self, search_term):
        """Пошук медикаментів за назвою або штрих-кодом"""
        return list(self.medications.find({
            '$or': [
                {'name': {'$regex': search_term, '$options': 'i'}},
                {'barcode': {'$regex': search_term, '$options': 'i'}},
                {'supplier': {'$regex': search_term, '$options': 'i'}}
            ]
        }))
    
    def search_equipment(self, search_term):
        """Пошук обладнання за назвою або QR-кодом"""
        return list(self.equipment.find({
            '$or': [
                {'name': {'$regex': search_term, '$options': 'i'}},
                {'qr_code': {'$regex': search_term, '$options': 'i'}},
                {'location': {'$regex': search_term, '$options': 'i'}},
                {'manufacturer': {'$regex': search_term, '$options': 'i'}}
            ]
        }))
    
    # ============ Масові операції ============
    
    def bulk_update_medication_quantity(self, updates):
        """Масове оновлення кількості медикаментів
        updates = [{'barcode': 'xxx', 'quantity_change': -5}, ...]
        """
        operations = []
        for update in updates:
            operations.append({
                'update_one': {
                    'filter': {'barcode': update['barcode']},
                    'update': {
                        '$inc': {'quantity': update['quantity_change']},
                        '$set': {'last_updated': datetime.now()}
                    }
                }
            })
        if operations:
            result = self.medications.bulk_write(operations)
            return result.modified_count
        return 0
    
    def close(self):
        """Закриття з'єднання"""
        self.client.close()