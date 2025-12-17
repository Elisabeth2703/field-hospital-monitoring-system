from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def medication_list(request):
    return HttpResponse("Список медикаментів")

def equipment_list(request):
    return HttpResponse("Список обладнання")

def scan_barcode(request):
    return HttpResponse("Сканування штрих-коду")