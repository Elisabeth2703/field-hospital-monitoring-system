from django.shortcuts import render
from django.http import HttpResponse
from .models import Patient

def patient_list(request):
  return HttpResponse("The patient list is currently empty")

def register_patient(request):
  return HttpResponse("Patient Registration Form")

def patient_detail(request, pk):
  return HttpResponse(f"Patient details with id={pk}")
