from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import redirect

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # Головна сторінка
    path('admin/', admin.site.urls),
    path('equipment/', include('equipment.urls')),  # URL-и для обладнання
    path('patients/', include('patients.urls')),    # URL-и для пацієнтів
    path('patients-redirect/', lambda request: redirect('patient_list')),  # Якщо потрібен redirect
    path('staff-login/', lambda request: redirect('staff_login')),        # Якщо потрібен redirect
]
