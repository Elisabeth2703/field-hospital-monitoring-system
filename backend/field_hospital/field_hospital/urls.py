from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.shortcuts import redirect

urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  
    path('admin/', admin.site.urls),
    path('equipment/', include('equipment.urls')),  
    path('patients/', include('patients.urls')),    
    path('patients-redirect/', lambda request: redirect('patient_list')),  
    path('staff-login/', lambda request: redirect('staff_login')),       
]
