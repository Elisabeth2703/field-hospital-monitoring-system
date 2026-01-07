import uuid
from djongo import models

from django.db import models

STATUS_CHOICES = [
    ('working', 'Working'),      
    ('maintenance', 'Maintenance'),  
    ('broken', 'Broken'),        
]

class Equipment(models.Model):
    
    name = models.CharField(max_length=255)
    qr_code = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='working')
    last_maintenance = models.DateField(null=True, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_until = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    manufacturer = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)  
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name





class Medication(models.Model):
   
    name = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField(default=0)
    critical_level = models.IntegerField(default=0)
    supplier = models.CharField(max_length=255, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    unit = models.CharField(max_length=50, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.name
