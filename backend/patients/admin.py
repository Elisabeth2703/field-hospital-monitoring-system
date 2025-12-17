from django.contrib import admin
from .models import Patient, VitalSigns

admin.site.register(Patient)
admin.site.register(VitalSigns)
