from django.urls import path
from . import views

urlpatterns = [
  path('patients/', views.patient_list, name='patient_list'),
  path('register/', views.register_patient, name='register_patient'),
  path('<int:pk>/', views.patient_detail, name='patient_detail'),
]
