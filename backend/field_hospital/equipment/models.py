from djongo import models

class Equipment(models.Model):
    STATUS_CHOICES = [
        ('working', 'Працює'),
        ('maintenance', 'На обслуговуванні'),
        ('broken', 'Зламано'),
        ('reserved', 'Зарезервовано'),
    ]

    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='Назва обладнання')
    quantity = models.IntegerField(verbose_name='Кількість')
    qr_code = models.CharField(max_length=100, unique=True, verbose_name='QR-код')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='working', verbose_name='Статус')
    last_maintenance = models.DateField(verbose_name='Останнє обслуговування')
    location = models.CharField(max_length=200, blank=True, verbose_name='Розташування')
    manufacturer = models.CharField(max_length=200, blank=True, verbose_name='Виробник')
    purchase_date = models.DateField(blank=True, null=True, verbose_name='Дата придбання')
    warranty_until = models.DateField(blank=True, null=True, verbose_name='Гарантія до')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='Останнє оновлення')
    maintenance_history = models.TextField(default='[]', blank=True, verbose_name='Історія обслуговування')

    class Meta:
        verbose_name = 'Обладнання'
        verbose_name_plural = 'Обладнання'

    def __str__(self):
        return f"{self.name} ({self.quantity})"


class Medication(models.Model):
    _id = models.ObjectIdField(primary_key=True)
    name = models.CharField(max_length=200, verbose_name='Назва медикаменту')
    quantity = models.IntegerField(verbose_name='Кількість')
    unit = models.CharField(max_length=50, verbose_name='Одиниця виміру')
    critical_level = models.IntegerField(verbose_name='Критичний рівень')
    barcode = models.CharField(max_length=100, unique=True, verbose_name='Штрих-код')
    expiry_date = models.DateField(blank=True, null=True, verbose_name='Термін придатності')
    supplier = models.CharField(max_length=200, blank=True, verbose_name='Постачальник')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='Останнє оновлення')

    class Meta:
        verbose_name = 'Медикамент'
        verbose_name_plural = 'Медикаменти'

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"



