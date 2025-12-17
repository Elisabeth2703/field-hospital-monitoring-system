from django.urls import path
from . import views

urlpatterns = [
    path('medications/', views.medication_list, name='medication_list'),
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('scan-barcode/', views.scan_barcode, name='scan_barcode'),
]