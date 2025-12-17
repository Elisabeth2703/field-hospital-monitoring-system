from django.db import models

class Patient(models.Model):
  full_name = models.CharField(max_length=200)
  age = models.IntegerField()
  bracelet_id = models.CharField(max_length=50, unique=True)
  injury_type = models.CharField(max_length=100)
  severity = models.CharField(max_length=50)
  admission_date = models.DateTimeField(auto_now_add=True)
    
class VitalSigns(models.Model):
  patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
  timestamp = models.DateTimeField(auto_now_add=True)
  heart_rate = models.IntegerField()
  temperature = models.FloatField()
  oxygen_saturation = models.IntegerField()
