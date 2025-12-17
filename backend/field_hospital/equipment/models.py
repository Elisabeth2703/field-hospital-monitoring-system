from django.db import models

# Create your models here.
class Medication(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    unit = models.CharField(max_length=50)
    critical_level = models.IntegerField()
    barcode = models.CharField(max_length=100, unique=True)
    
class Equipment(models.Model):
    name = models.CharField(max_length=200)
    quantity = models.IntegerField()
    qr_code = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=50)
    last_maintenance = models.DateField()