from pymongo import MongoClient
from datetime import datetime, timedelta

class MongoDBManager:
    def __init__(self, db_name="medical_system"):
        self.client = MongoClient('localhost', 27017)
        self.db = self.client[db_name]
        self.medications = self.db['medications']
        self.equipment = self.db['equipment']
        self.medication_logs = self.db['medication_logs']

    def create_medication(self, medication_data):
        medication_data['last_updated'] = datetime.now()
        result = self.medications.insert_one(medication_data)
        return result.inserted_id

    def get_medication(self, barcode):
        return self.medications.find_one({'barcode': barcode})

    def get_all_medications(self):
        return list(self.medications.find())

    def update_medication(self, barcode, update_data):
        update_data['last_updated'] = datetime.now()
        result = self.medications.update_one({'barcode': barcode}, {'$set': update_data})
        return result.modified_count

    def delete_medication(self, barcode):
        result = self.medications.delete_one({'barcode': barcode})
        return result.deleted_count

    def create_equipment(self, equipment_data):
        equipment_data['last_updated'] = datetime.now()
        equipment_data['maintenance_history'] = []
        result = self.equipment.insert_one(equipment_data)
        return result.inserted_id

    def get_equipment(self, qr_code):
        return self.equipment.find_one({'qr_code': qr_code})

    def get_all_equipment(self):
        return list(self.equipment.find())

    def update_equipment(self, qr_code, update_data):
        update_data['last_updated'] = datetime.now()
        result = self.equipment.update_one({'qr_code': qr_code}, {'$set': update_data})
        return result.modified_count

    def delete_equipment(self, qr_code):
        result = self.equipment.delete_one({'qr_code': str(qr_code)})
        return result.deleted_count

    def get_critical_medications(self):
        return list(self.medications.find({'$expr': {'$lte': ['$quantity', '$critical_level']}}))

    def get_expired_medications(self):
        today = datetime.now().date()
        return list(self.medications.find({'expiry_date': {'$lt': today.isoformat()}}))

    def get_equipment_by_status(self, status):
        return list(self.equipment.find({'status': status}))

    def get_equipment_needing_maintenance(self):
        six_months_ago = (datetime.now() - timedelta(days=180)).date()
        return list(self.equipment.find({'last_maintenance': {'$lt': six_months_ago.isoformat()}}))

    def get_medication_statistics(self):
        pipeline = [
            {'$group': {
                '_id': None,
                'total_medications': {'$sum': 1},
                'total_quantity': {'$sum': '$quantity'},
                'critical_count': {'$sum': {'$cond': [{'$lte': ['$quantity', '$critical_level']}, 1, 0]}}
            }}
        ]
        result = list(self.medications.aggregate(pipeline))
        return result[0] if result else {}

    def get_equipment_statistics(self):
        pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}, 'total_quantity': {'$sum': '$quantity'}}}]
        return list(self.equipment.aggregate(pipeline))

    def get_medication_usage_trend(self, barcode, days=30):
        start_date = datetime.now() - timedelta(days=days)
        pipeline = [
            {'$match': {'medication_barcode': barcode, 'timestamp': {'$gte': start_date}}},
            {'$group': {'_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}}, 'total_change': {'$sum': '$quantity_change'}, 'actions': {'$push': '$action'}}},
            {'$sort': {'_id': 1}}
        ]
        return list(self.medication_logs.aggregate(pipeline))

    def log_medication_action(self, barcode, action, quantity_change, user='', notes=''):
        log_entry = {'medication_barcode': barcode, 'action': action, 'quantity_change': quantity_change, 'timestamp': datetime.now(), 'user': user, 'notes': notes}
        result = self.medication_logs.insert_one(log_entry)
        return result.inserted_id

    def get_medication_logs(self, barcode=None, limit=50):
        query = {'medication_barcode': barcode} if barcode else {}
        return list(self.medication_logs.find(query).sort('timestamp', -1).limit(limit))

    def search_medications(self, search_term):
        return list(self.medications.find({'$or': [{'name': {'$regex': search_term, '$options': 'i'}}, {'barcode': {'$regex': search_term, '$options': 'i'}}, {'supplier': {'$regex': search_term, '$options': 'i'}}]}))

    def search_equipment(self, search_term):
        return list(self.equipment.find({'$or': [{'name': {'$regex': search_term, '$options': 'i'}}, {'qr_code': {'$regex': search_term, '$options': 'i'}}, {'location': {'$regex': search_term, '$options': 'i'}}, {'manufacturer': {'$regex': search_term, '$options': 'i'}}]}))

    def bulk_update_medication_quantity(self, updates):
        operations = [{'update_one': {'filter': {'barcode': u['barcode']}, 'update': {'$inc': {'quantity': u['quantity_change']}, '$set': {'last_updated': datetime.now()}}}} for u in updates]
        if operations:
            result = self.medications.bulk_write(operations)
            return result.modified_count
        return 0

    def close(self):
        self.client.close()
