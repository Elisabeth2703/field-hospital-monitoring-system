from django.db import models
from datetime import datetime

class Medication(models.Model):
    """Модель для зберігання інформації про медикаменти"""
    name = models.CharField(max_length=200, verbose_name="Назва медикаменту")
    quantity = models.IntegerField(verbose_name="Кількість")
    unit = models.CharField(max_length=50, verbose_name="Одиниця виміру")
    critical_level = models.IntegerField(verbose_name="Критичний рівень")
    barcode = models.CharField(max_length=100, unique=True, verbose_name="Штрих-код")
    expiry_date = models.DateField(verbose_name="Термін придатності", null=True, blank=True)
    supplier = models.CharField(max_length=200, verbose_name="Постачальник", blank=True)
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Останнє оновлення")
    
    class Meta:
        verbose_name = "Медикамент"
        verbose_name_plural = "Медикаменти"
    
    def __str__(self):
        return f"{self.name} - {self.quantity} {self.unit}"
    
    def is_critical(self):
        """Перевірка, чи кількість нижче критичного рівня"""
        return self.quantity <= self.critical_level
    
    def to_mongo_dict(self):
        """Конвертація об'єкта в словник для MongoDB"""
        return {
            'name': self.name,
            'quantity': self.quantity,
            'unit': self.unit,
            'critical_level': self.critical_level,
            'barcode': self.barcode,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'supplier': self.supplier,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class Equipment(models.Model):
    """Модель для зберігання інформації про обладнання"""
    name = models.CharField(max_length=200, verbose_name="Назва обладнання")
    quantity = models.IntegerField(verbose_name="Кількість")
    qr_code = models.CharField(max_length=100, unique=True, verbose_name="QR-код")
    status = models.CharField(
        max_length=50, 
        verbose_name="Статус",
        choices=[
            ('working', 'Працює'),
            ('maintenance', 'На обслуговуванні'),
            ('broken', 'Зламано'),
            ('reserved', 'Зарезервовано')
        ],
        default='working'
    )
    last_maintenance = models.DateField(verbose_name="Останнє обслуговування")
    location = models.CharField(max_length=200, verbose_name="Розташування", blank=True)
    manufacturer = models.CharField(max_length=200, verbose_name="Виробник", blank=True)
    purchase_date = models.DateField(verbose_name="Дата придбання", null=True, blank=True)
    warranty_until = models.DateField(verbose_name="Гарантія до", null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True, verbose_name="Останнє оновлення")
    
    # Для зберігання історії обслуговування як текст (JSON string)
    maintenance_history = models.TextField(default='[]', blank=True, verbose_name="Історія обслуговування")
    
    class Meta:
        verbose_name = "Обладнання"
        verbose_name_plural = "Обладнання"
    
    def __str__(self):
        return f"{self.name} - {self.status}"
    
    def needs_maintenance(self):
        """Перевірка, чи потрібне обслуговування (більше 6 місяців)"""
        from datetime import timedelta
        return (datetime.now().date() - self.last_maintenance) > timedelta(days=180)
    
    def add_maintenance_record(self, date, description, technician):
        """Додавання запису про обслуговування"""
        import json
        try:
            history = json.loads(self.maintenance_history)
        except:
            history = []
        
        record = {
            'date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
            'description': description,
            'technician': technician
        }
        history.append(record)
        self.maintenance_history = json.dumps(history)
        self.last_maintenance = date
        self.save()
    
    def get_maintenance_history(self):
        """Отримання історії обслуговування як список"""
        import json
        try:
            return json.loads(self.maintenance_history)
        except:
            return []


class MedicationLog(models.Model):
    """Модель для логування змін у медикаментах (часові ряди)"""
    medication_barcode = models.CharField(max_length=100, verbose_name="Штрих-код медикаменту")
    action = models.CharField(
        max_length=50,
        choices=[
            ('added', 'Додано'),
            ('used', 'Використано'),
            ('expired', 'Прострочено'),
            ('restocked', 'Поповнено')
        ]
    )
    quantity_change = models.IntegerField(verbose_name="Зміна кількості")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Час операції")
    user = models.CharField(max_length=100, verbose_name="Користувач", blank=True)
    notes = models.TextField(verbose_name="Примітки", blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Лог медикаментів"
        verbose_name_plural = "Логи медикаментів"
    
    def __str__(self):
        return f"{self.medication_barcode} - {self.action} - {self.timestamp}"