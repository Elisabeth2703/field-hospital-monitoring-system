from django.urls import path
from . import views

urlpatterns = [
    # Головна сторінка модуля
    path('', views.equipment_home, name='equipment_home'),
    
    # Medications URLs
    path('medications/', views.medication_list, name='medication_list'),
    path('medications/create/', views.medication_create, name='medication_create'),
    path('medications/<str:barcode>/', views.medication_detail, name='medication_detail'),
    path('medications/<str:barcode>/update/', views.medication_update, name='medication_update'),
    path('medications/<str:barcode>/delete/', views.medication_delete, name='medication_delete'),
    
    # Equipment URLs
    path('equipment/', views.equipment_list, name='equipment_list'),
    path('equipment/create/', views.equipment_create, name='equipment_create'),
    path('equipment/<str:qr_code>/', views.equipment_detail, name='equipment_detail'),
    path('equipment/<str:qr_code>/update/', views.equipment_update, name='equipment_update'),
    path('equipment/<str:qr_code>/delete/', views.equipment_delete, name='equipment_delete'),
    
    # API endpoints
    path('api/medications/statistics/', views.api_medication_statistics, name='api_medication_stats'),
    path('api/medications/critical/', views.api_critical_medications, name='api_critical_meds'),
]