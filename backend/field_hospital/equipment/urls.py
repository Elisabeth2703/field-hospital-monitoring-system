from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.equipment_home, name='equipment_home'),

    path('mqtt/', views.mqtt_dashboard, name='mqtt_dashboard'),
    path('api/mqtt/', views.api_mqtt_equipment, name='api_mqtt_equipment'),

    path('medications/', views.medication_list, name='medication_list'),
    path('medications/create/', views.medication_create, name='medication_create'),
    path('medications/analytics/', views.medication_statistics, name='medication_statistics'),
    path('medications/<str:barcode>/', views.medication_detail, name='medication_detail'),
    path('medications/<str:barcode>/update/', views.medication_update, name='medication_update'),
    path('medications/<str:barcode>/delete/', views.medication_delete, name='medication_delete'),

    path('', views.equipment_list, name='equipment_list'),
    path('create/', views.equipment_create, name='equipment_create'),
    path('statistics/', views.equipment_statistics, name='equipment_statistics'),

    path('<str:qr_code>/', views.equipment_detail, name='equipment_detail'),
    path('<str:qr_code>/update/', views.equipment_update, name='equipment_update'),
    path('<str:qr_code>/delete/', views.equipment_delete, name='equipment_delete'),

    path('api/medications/statistics/', views.api_medication_statistics, name='api_medication_stats'),
    path('api/medications/critical/', views.api_critical_medications, name='api_critical_meds'),
]
