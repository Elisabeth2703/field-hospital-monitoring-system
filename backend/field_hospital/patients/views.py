from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from .models import Patient, VitalSigns, InjuryClassification
from datetime import datetime, timedelta
from bson import ObjectId

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


def add_vital_signs(request, bracelet_id):
  return HttpResponse("Введення показників (в розробці)")

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