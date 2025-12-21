from django.urls import path
from . import views

urlpatterns = [
  path('', views.patient_list, name='patient_list'),
  path('register/', views.register_patient, name='register_patient'),
  path('<str:pk>/', views.patient_detail, name='patient_detail'),
  path('<str:bracelet_id>/add-vitals/', views.add_vital_signs, name='add_vital_signs'),
]
