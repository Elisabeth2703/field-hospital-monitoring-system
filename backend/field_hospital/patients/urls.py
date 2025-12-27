from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
  path('login/', views.staff_login, name='staff_login'),
  path('register/', views.staff_register, name='staff_register'),
  path('logout/', views.staff_logout, name='staff_logout'),
  path('profile/', views.staff_profile, name='staff_profile'),

  path('', views.staff_login, name='home'),

  path('patients/', views.patient_list, name='patient_list'),
  path('patients/register/', views.register_patient, name='register_patient'),
  path('patients/<str:pk>/', views.patient_detail, name='patient_detail'),
  path('patients/<str:bracelet_id>/add-vitals/', views.add_vital_signs, name='add_vital_signs'),

  path('analytics/', views.analytics_view, name='analytics'),
  path('analytics/time-series/<str:bracelet_id>/', views.patient_time_series, name='patient_time_series'),
  path('api/analytics-data/', views.api_analytics_data, name='api_analytics_data'),
]
