from django.contrib import admin
from .models import Equipment, Medication

# ================= EquipmentAdmin =================
@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        'name',           # назва обладнання
        'qr_code',        # QR-код
        'quantity',       # кількість
        'status',         # статус (working / maintenance / broken)
        'last_maintenance',  # останнє обслуговування
        'purchase_date',     # дата придбання
        'warranty_until',    # гарантія до
        'location',          # розташування
        'manufacturer',      # виробник
        'last_updated',      # автоматично оновлюється
    )
    search_fields = ('name', 'qr_code', 'location', 'manufacturer')
    list_filter = ('status',)
    ordering = ('name',)

# ================= MedicationAdmin =================
@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = (
        'name',        # назва медикаменту
        'barcode',     # штрих-код
        'quantity',    # кількість
        'critical_level',  # критичний рівень
        'unit',        # одиниця виміру
        'last_updated' # автоматично оновлюється
    )
    search_fields = ('name', 'barcode', 'supplier')
    list_filter = ('supplier',)
    ordering = ('name',)
