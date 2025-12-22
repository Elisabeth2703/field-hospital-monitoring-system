from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Equipment, Medication

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'status', 'location', 'last_updated')
    search_fields = ('name', 'location', 'status')
    list_filter = ('status',)

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'quantity', 'unit', 'critical_level', 'expiry_date', 'last_updated')
    search_fields = ('name', 'barcode', 'supplier')
    list_filter = ('expiry_date',)
