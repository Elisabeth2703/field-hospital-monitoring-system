from django.contrib import admin
from .models import Patient, VitalSigns, InjuryClassification

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
  list_display = ['bracelet_id', 'full_name', 'age', 'severity', 'injury_type', 'admission_date']
  list_filter = ['severity', 'injury_type', 'admission_date', 'status']
  search_fields = ['full_name', 'bracelet_id', 'bed_number']
  list_per_page = 25
  date_hierarchy = 'admission_date'
  
  fieldsets = (
    ('Основна інформація', {
      'fields': ('full_name', 'age', 'blood_type', 'bracelet_id')
    }),
    ('Медична інформація', {
      'fields': ('injury_type', 'severity', 'status', 'notes')
    }),
    ('Розміщення', {
      'fields': ('bed_number',)
    }),
  )

@admin.register(VitalSigns)
class VitalSignsAdmin(admin.ModelAdmin):
  list_display = ['patient_bracelet_id', 'timestamp', 'heart_rate', 'temperature', 
  'blood_pressure_sys', 'blood_pressure_dia', 'oxygen_saturation']
  list_filter = ['timestamp']
  search_fields = ['patient_bracelet_id']
  list_per_page = 50
  date_hierarchy = 'timestamp'
  
  readonly_fields = ['timestamp']

@admin.register(InjuryClassification)
class InjuryClassificationAdmin(admin.ModelAdmin):
  list_display = ['patient_bracelet_id', 'injury_type', 'severity', 'classification_date']
  list_filter = ['injury_type', 'severity', 'classification_date']
  search_fields = ['patient_bracelet_id', 'diagnosis']
  date_hierarchy = 'classification_date'
  
  readonly_fields = ['classification_date']