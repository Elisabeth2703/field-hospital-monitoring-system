from django.contrib import admin
from .models import Equipment, Medication


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        'name',           
        'qr_code',       
        'quantity',       
        'status',         
        'last_maintenance',  
        'purchase_date',     
        'warranty_until',    
        'location',          
        'manufacturer',      
        'last_updated',      
    )
    search_fields = ('name', 'qr_code', 'location', 'manufacturer')
    list_filter = ('status',)
    ordering = ('name',)


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = (
        'name',       
        'barcode',     
        'quantity',    
        'critical_level', 
        'unit',       
        'last_updated' 
    )
    search_fields = ('name', 'barcode', 'supplier')
    list_filter = ('supplier',)
    ordering = ('name',)
