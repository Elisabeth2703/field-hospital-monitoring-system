from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from .models import Patient, VitalSigns, InjuryClassification, MedicalStaff
from .analytics import PatientAnalytics
from datetime import datetime
import json

from functools import wraps

def login_required(view_func):
  """Декоратор для перевірки авторизації"""
  @wraps(view_func)
  def wrapper(request, *args, **kwargs):
    if not request.session.get('staff_id'):
      messages.warning(request, 'Спочатку увійдіть в систему')
      return redirect('staff_login')
    return view_func(request, *args, **kwargs)
  return wrapper

@login_required
def patient_list(request):
  """Відображення списку всіх пацієнтів"""
  patients = Patient.objects.all().order_by('-admission_date')
  
  total_patients = patients.count()
  critical_count = patients.filter(severity='Критичний').count()
  
  injury_stats = {}
  for patient in patients:
    injury_type = patient.injury_type
    if injury_type in injury_stats:
        injury_stats[injury_type] += 1
    else:
        injury_stats[injury_type] = 1
  
  context = {
    'patients': patients,
    'total_patients': total_patients,
    'critical_count': critical_count,
    'injury_stats': injury_stats,
  }
  return render(request, 'patients/patient_list.html', context)

@login_required
def patient_detail(request, pk):
  """Детальна інформація про пацієнта"""
  try:
    patient = Patient.objects.get(bracelet_id=pk)
  except Patient.DoesNotExist:
    messages.error(request, 'Пацієнта не знайдено')
    return redirect('patient_list')
  
  vital_signs = VitalSigns.objects.filter(
    patient_bracelet_id=patient.bracelet_id
  ).order_by('-timestamp')[:20]
  
  classifications = InjuryClassification.objects.filter(
    patient_bracelet_id=patient.bracelet_id
  ).order_by('-classification_date')
  
  if vital_signs.exists():
    avg_heart_rate = sum(v.heart_rate for v in vital_signs) / len(vital_signs)
    avg_temperature = sum(v.temperature for v in vital_signs) / len(vital_signs)
    avg_oxygen = sum(v.oxygen_saturation for v in vital_signs) / len(vital_signs)
  else:
    avg_heart_rate = avg_temperature = avg_oxygen = None
  
  context = {
    'patient': patient,
    'vital_signs': vital_signs,
    'classifications': classifications,
    'avg_heart_rate': avg_heart_rate,
    'avg_temperature': avg_temperature,
    'avg_oxygen': avg_oxygen,
  }
  return render(request, 'patients/patient_detail.html', context)

@login_required
def add_vital_signs(request, bracelet_id):
  return HttpResponse("Введення показників (в розробці)")

@login_required
def register_patient(request):
  """Реєстрація нового пацієнта"""
  if request.method == 'POST':
    try:
      bracelet_id = request.POST.get('bracelet_id')
      if Patient.objects.filter(bracelet_id=bracelet_id).exists():
        messages.error(request, f'Пацієнт з ID браслету {bracelet_id} вже існує!')
        return render(request, 'patients/register.html', {
          'injury_types': Patient.INJURY_TYPES,
          'severity_choices': Patient.SEVERITY_CHOICES,
        })
    
      patient = Patient.objects.create(
        full_name=request.POST.get('full_name'),
        age=int(request.POST.get('age')),
        bracelet_id=bracelet_id,
        injury_type=request.POST.get('injury_type'),
        severity=request.POST.get('severity'),
        bed_number=request.POST.get('bed_number', ''),
        blood_type=request.POST.get('blood_type', ''),
        notes=request.POST.get('notes', '')
      )
      
      if request.POST.get('diagnosis'):
        InjuryClassification.objects.create(
          patient_bracelet_id=patient.bracelet_id,
          injury_type=patient.injury_type,
          severity=patient.severity,
          diagnosis=request.POST.get('diagnosis'),
          treatment_plan=request.POST.get('treatment_plan', '')
        )
    
      messages.success(request, f'Пацієнт {patient.full_name} успішно зареєстрований!')
      return redirect('patient_detail', pk=patient.bracelet_id)
      
    except Exception as e:
      messages.error(request, f'Помилка реєстрації: {str(e)}')

  context = {
    'injury_types': Patient.INJURY_TYPES,
    'severity_choices': Patient.SEVERITY_CHOICES,
  }

  return render(request, 'patients/register.html', context)

@login_required
def analytics_view(request):
  """Розширена аналітика з використанням numpy, pandas, sklearn"""
  analytics = PatientAnalytics()
  
  period = request.GET.get('period', 'week')
  
  period_analysis = analytics.analyze_by_period(period)
  
  injury_classification = analytics.classify_injury_severity()
  
  flow_prediction = analytics.predict_patient_flow(days_ahead=7)
  
  correlation = analytics.get_correlation_analysis()

  period_map = {'week': 7, 'three_months': 90, 'year': 365}
  days = period_map.get(period, 7)
  from datetime import datetime, timedelta
  start_date = datetime.now() - timedelta(days=days)
  patients = Patient.objects.filter(admission_date__gte=start_date)
  
  context = {
    'period': period,
    'period_analysis': period_analysis,
    'injury_classification': injury_classification,
    'flow_prediction': flow_prediction,
    'correlation': correlation,
    'patients': patients,
    'patient': None,
  }
  
  return render(request, 'patients/analytics.html', context)

@login_required
def patient_time_series(request, bracelet_id):
  """Аналіз часових рядів для конкретного пацієнта"""
  analytics = PatientAnalytics()
  
  try:
    patient = Patient.objects.get(bracelet_id=bracelet_id)
  except Patient.DoesNotExist:
    messages.error(request, 'Пацієнта не знайдено')
    return redirect('patient_list')
  
  time_series_analysis = analytics.analyze_time_series(bracelet_id)
  
  vital_signs = VitalSigns.objects.filter(
    patient_bracelet_id=bracelet_id
  ).order_by('timestamp')
  
  context = {
    'patient': patient,
    'time_series_analysis': time_series_analysis,
    'vital_signs': vital_signs,
  }
  
  return render(request, 'patients/time_series.html', context)

def api_analytics_data(request):
  """API endpoint для отримання даних аналітики (для графіків)"""
  analytics = PatientAnalytics()
  period = request.GET.get('period', 'week')
  
  data = analytics.analyze_by_period(period)
  
  return JsonResponse(data, safe=False)

def staff_login(request):
  """Вхід медперсоналу"""
  if request.session.get('staff_id'):
    return redirect('patient_list')
  
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')
      
    try:
      staff = MedicalStaff.objects.get(username=username)
        
      if staff.check_password(password) and staff.is_active:
        request.session['staff_id'] = str(staff._id)
        print("STAFF LOGIN OK, SESSION:", request.session.items())
        request.session['staff_username'] = staff.username
        request.session['staff_name'] = staff.full_name
        request.session['staff_role'] = staff.role
        request.session['staff_avatar'] = staff.avatar
          
        staff.last_login = datetime.now()
        staff.save(update_fields=['last_login'])
            
        messages.success(request, f'Вітаємо, {staff.full_name}!')
        return redirect('patient_list')
      else:
        messages.error(request, 'Невірний логін або пароль')
    except MedicalStaff.DoesNotExist:
      messages.error(request, 'Невірний логін або пароль')
  
  return render(request, 'patients/staff_login.html')


def staff_register(request):
  """Реєстрація нового медперсоналу"""
  if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')
    password_confirm = request.POST.get('password_confirm')
    full_name = request.POST.get('full_name')
    role = request.POST.get('role')
    email = request.POST.get('email', '')
    phone = request.POST.get('phone', '')
    specialization = request.POST.get('specialization', '')
    
    if password != password_confirm:
        messages.error(request, 'Паролі не співпадають!')
        return render(request, 'patients/staff_register.html', {
            'role_choices': MedicalStaff.ROLE_CHOICES
        })
    
    if len(password) < 6:
        messages.error(request, 'Пароль повинен містити мінімум 6 символів!')
        return render(request, 'patients/staff_register.html', {
            'role_choices': MedicalStaff.ROLE_CHOICES
        })
    
    if MedicalStaff.objects.filter(username=username).exists():
        messages.error(request, f'Користувач {username} вже існує!')
        return render(request, 'patients/staff_register.html', {
            'role_choices': MedicalStaff.ROLE_CHOICES
        })
    
    avatar_map = {
        'Лікар': '👨‍⚕️',
        'Медсестра': '👩‍⚕️',
        'Адміністратор': '👔',
        'Парамедик': '🚑'
    }
    
    staff = MedicalStaff(
        username=username,
        full_name=full_name,
        role=role,
        email=email,
        phone=phone,
        specialization=specialization,
        avatar=avatar_map.get(role, '👤')
    )
    staff.set_password(password)
    staff.save()
    
    messages.success(request, f'Реєстрацію завершено! Тепер ви можете увійти.')
    return redirect('staff_login')
  
  context = {
    'role_choices': MedicalStaff.ROLE_CHOICES
  }
  return render(request, 'patients/staff_register.html', context)


def staff_logout(request):
    """Вихід з системи"""
    request.session.flush()
    messages.info(request, 'Ви вийшли з системи')
    return redirect('staff_login')


def staff_profile(request):
  """Особистий кабінет медперсоналу"""
  if not request.session.get('staff_id'):
    messages.warning(request, 'Спочатку увійдіть в систему')
    return redirect('staff_login')

  from bson import ObjectId
  try:
    staff = MedicalStaff.objects.get(_id=ObjectId(request.session['staff_id']))
  except MedicalStaff.DoesNotExist:
    request.session.flush()
    messages.error(request, 'Користувача не знайдено')
    return redirect('staff_login')
    
  total_patients = Patient.objects.count()
  critical_patients = Patient.objects.filter(severity='Критичний').count()
  
  recent_patients = Patient.objects.all().order_by('-admission_date')[:5]
  
  context = {
    'staff': staff,
    'total_patients': total_patients,
    'critical_patients': critical_patients,
    'recent_patients': recent_patients,
  }
    
  if request.method == 'POST':
    staff.full_name = request.POST.get('full_name', staff.full_name)
    staff.email = request.POST.get('email', staff.email)
    staff.phone = request.POST.get('phone', staff.phone)
    staff.specialization = request.POST.get('specialization', staff.specialization)
      
    new_password = request.POST.get('new_password')
    if new_password and len(new_password) >= 6:
      staff.set_password(new_password)
      messages.success(request, 'Пароль успішно змінено!')
      
    staff.save()
    
    request.session['staff_name'] = staff.full_name
      
    messages.success(request, 'Профіль оновлено!')
    return redirect('staff_profile')

  return render(request, 'patients/staff_profile.html', context)
