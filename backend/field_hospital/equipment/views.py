from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .mongodb_utils import MongoDBManager
from datetime import datetime, date
import json
from .models import Equipment
import uuid
# Ініціалізація менеджера MongoDB
db_manager = MongoDBManager()
mongo = MongoDBManager()
from .analytics import (
    equipment_status_analysis,
    low_quantity_equipment,
    equipment_forecast
)

# ============ Головна сторінка ============

def equipment_home(request):
    """Головна сторінка модуля обладнання"""
    try:
        # Отримання статистики
        med_stats = db_manager.get_medication_statistics()
        eq_stats = db_manager.get_equipment_statistics()
        critical_meds = db_manager.get_critical_medications()
        maintenance_needed = db_manager.get_equipment_needing_maintenance()
        
        context = {
            'medication_stats': med_stats,
            'equipment_stats': eq_stats,
            'critical_medications': critical_meds,
            'maintenance_needed': maintenance_needed,
        }
        return render(request, 'equipment/home.html', context)
    except Exception as e:
        messages.error(request, f'Помилка завантаження даних: {str(e)}')
        return render(request, 'equipment/home.html', {})


# ============ Medications Views ============

def medication_list(request):
    """Список всіх медикаментів"""
    try:
        search_query = request.GET.get('search', '')
        
        if search_query:
            medications = db_manager.search_medications(search_query)
        else:
            medications = db_manager.get_all_medications()
        
        # Конвертація ObjectId в string для шаблону
        for med in medications:
            med['_id'] = str(med['_id'])
        
        context = {
            'medications': medications,
            'search_query': search_query,
        }
        return render(request, 'equipment/medication_list.html', context)
    except Exception as e:
        messages.error(request, f'Помилка отримання медикаментів: {str(e)}')
        return render(request, 'equipment/medication_list.html', {'medications': []})


def medication_detail(request, barcode):
    """Детальна інформація про медикамент"""
    try:
        medication = db_manager.get_medication(barcode)
        
        if not medication:
            messages.error(request, 'Медикамент не знайдено')
            return redirect('medication_list')
        
        # Отримання логів
        logs = db_manager.get_medication_logs(barcode, limit=20)
        
        # Отримання тренду використання
        usage_trend = db_manager.get_medication_usage_trend(barcode, days=30)
        
        medication['_id'] = str(medication['_id'])
        for log in logs:
            log['_id'] = str(log['_id'])
        
        context = {
            'medication': medication,
            'logs': logs,
            'usage_trend': json.dumps(usage_trend),
        }
        return render(request, 'equipment/medication_detail.html', context)
    except Exception as e:
        messages.error(request, f'Помилка: {str(e)}')
        return redirect('medication_list')


def medication_create(request):
    """Створення нового медикаменту"""
    if request.method == 'POST':
        try:
            medication_data = {
                'name': request.POST.get('name'),
                'quantity': int(request.POST.get('quantity')),
                'unit': request.POST.get('unit'),
                'critical_level': int(request.POST.get('critical_level')),
                'barcode': request.POST.get('barcode'),
                'expiry_date': request.POST.get('expiry_date'),
                'supplier': request.POST.get('supplier', ''),
            }
            
            # Перевірка унікальності штрих-коду
            existing = db_manager.get_medication(medication_data['barcode'])
            if existing:
                messages.error(request, 'Медикамент з таким штрих-кодом вже існує')
                return render(request, 'equipment/medication_form.html', {'medication': medication_data})
            
            med_id = db_manager.create_medication(medication_data)
            
            # Логування створення
            db_manager.log_medication_action(
                medication_data['barcode'],
                'added',
                medication_data['quantity'],
                user=request.user.username if request.user.is_authenticated else 'anonymous',
                notes='Початкове додавання'
            )
            
            messages.success(request, 'Медикамент успішно створено')
            return redirect('medication_detail', barcode=medication_data['barcode'])
        except Exception as e:
            messages.error(request, f'Помилка створення: {str(e)}')
    
    return render(request, 'equipment/medication_form.html', {})


def medication_update(request, barcode):
    """Оновлення медикаменту"""
    medication = db_manager.get_medication(barcode)
    
    if not medication:
        messages.error(request, 'Медикамент не знайдено')
        return redirect('medication_list')
    
    if request.method == 'POST':
        try:
            old_quantity = medication['quantity']
            update_data = {
                'name': request.POST.get('name'),
                'quantity': int(request.POST.get('quantity')),
                'unit': request.POST.get('unit'),
                'critical_level': int(request.POST.get('critical_level')),
                'expiry_date': request.POST.get('expiry_date'),
                'supplier': request.POST.get('supplier', ''),
            }
            
            db_manager.update_medication(barcode, update_data)
            
            # Логування зміни кількості
            quantity_change = update_data['quantity'] - old_quantity
            if quantity_change != 0:
                action = 'restocked' if quantity_change > 0 else 'used'
                db_manager.log_medication_action(
                    barcode,
                    action,
                    quantity_change,
                    user=request.user.username if request.user.is_authenticated else 'anonymous',
                    notes='Оновлення кількості'
                )
            
            messages.success(request, 'Медикамент успішно оновлено')
            return redirect('medication_detail', barcode=barcode)
        except Exception as e:
            messages.error(request, f'Помилка оновлення: {str(e)}')
    
    medication['_id'] = str(medication['_id'])
    return render(request, 'equipment/medication_form.html', {'medication': medication})


def medication_delete(request, barcode):
    """Видалення медикаменту"""
    if request.method == 'POST':
        try:
            count = db_manager.delete_medication(barcode)
            if count > 0:
                messages.success(request, 'Медикамент успішно видалено')
            else:
                messages.warning(request, 'Медикамент не знайдено')
        except Exception as e:
            messages.error(request, f'Помилка видалення: {str(e)}')
    
    return redirect('medication_list')


# ============ Equipment Views ============

from .models import Equipment  # імпортуй модель зверху

def equipment_list(request):
    try:
        equipments = [e for e in mongo.get_all_equipment() if not e.get('is_deleted', False)]
        return render(request, 'equipment/equipment_list.html', {'equipment': equipments})
    except Exception as e:
        messages.error(request, f'Помилка: {str(e)}')
        return render(request, 'equipment/equipment_list.html', {'equipment': []})



def equipment_create(request):
    if request.method == 'POST':
        data = {
            'name': request.POST.get('name'),
            'qr_code': request.POST.get('qr_code'),
            'quantity': int(request.POST.get('quantity', 1)),
            'status': request.POST.get('status'),
            'is_deleted': False,
        }
        mongo.create_equipment(data)
        messages.success(request, 'Обладнання додано!')
        return redirect('equipment_list')
    return render(request, 'equipment/equipment_form.html')


  

from datetime import datetime

def equipment_detail(request, qr_code):
    equipment = db_manager.get_equipment(qr_code)
    if not equipment:
        messages.error(request, 'Обладнання не знайдено')
        return redirect('equipment_list')

    #
    for field in ['last_maintenance', 'purchase_date', 'warranty_until']:
        if equipment.get(field):
            try:
                # Конвертуємо ISO рядок у datetime
                dt = datetime.fromisoformat(equipment[field])
                equipment[field] = dt.strftime('%b %d, %Y')  
            except Exception:
                
                pass

    return render(request, 'equipment/equipment_detail.html', {'equipment': equipment})



def equipment_update(request, qr_code):
    equipment = db_manager.get_equipment(qr_code)

    if not equipment:
        messages.error(request, 'Обладнання не знайдено')
        return redirect('equipment_list')

    if request.method == 'POST':
        try:
            update_data = {
                'name': request.POST.get('name'),
                'quantity': int(request.POST.get('quantity')),
                'status': request.POST.get('status'),
                'last_maintenance': request.POST.get('last_maintenance'),
                'purchase_date': request.POST.get('purchase_date') or None,
                'warranty_until': request.POST.get('warranty_until') or None,
                'location': request.POST.get('location'),
                'manufacturer': request.POST.get('manufacturer'),
            }

            db_manager.update_equipment(qr_code, update_data)
            messages.success(request, 'Обладнання успішно оновлено')
            return redirect('equipment_detail', qr_code=qr_code)
        except Exception as e:
            messages.error(request, f'Помилка оновлення: {str(e)}')

    return render(request, 'equipment/equipment_form.html', {'equipment': equipment})




def equipment_delete(request, qr_code):
    if request.method == 'POST':
        eq = mongo.get_equipment(qr_code)
        if eq:
            mongo.update_equipment(qr_code, {'is_deleted': True})
            messages.success(request, 'Обладнання видалено.')
        else:
            messages.warning(request, 'Обладнання не знайдено.')
    return redirect('equipment_list')



# ============ API Views (JSON) ============

@require_http_methods(["GET"])
def api_medication_statistics(request):
    """API для отримання статистики медикаментів"""
    try:
        stats = db_manager.get_medication_statistics()
        return JsonResponse(stats, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET"])
def api_critical_medications(request):
    """API для критичних медикаментів"""
    try:
        critical = db_manager.get_critical_medications()
        for med in critical:
            med['_id'] = str(med['_id'])
        return JsonResponse(critical, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    


from django.shortcuts import render
from .mongodb_utils import MongoDBManager

# Мапа статусів для відображення
STATUS_DISPLAY = {
    'working': 'Працює',
    'maintenance': 'На обслуговуванні',
    'broken': 'Зламане',
}



def equipment_statistics(request):
    db = MongoDBManager()
    
    # Усі обладнання
    all_equipment = db.get_all_equipment()
    
    # Загальна кількість об’єктів
    total_objects = len(all_equipment)
    
    # Загальна сума quantity
    total_quantity = sum(eq.get('quantity', 0) for eq in all_equipment)
    
    # Статистика по статусу
    status_dict = {}
    for eq in all_equipment:
        st = eq.get('status', 'unknown')
        status_dict[st] = status_dict.get(st, 0) + eq.get('quantity', 0)
    
    status_list = [{'status': k, 'count': v} for k, v in status_dict.items()]
    
    # Критично мала кількість (якщо quantity <= critical_level)
    low_quantity = [eq for eq in all_equipment if eq.get('quantity', 0) <= eq.get('critical_level', 0)]
    
    context = {
        'status': status_list,
        'low_quantity': low_quantity,
        'forecast': [],  # поки немає прогнозу
        'total_objects': total_objects,
        'total_quantity': total_quantity
    }
    
    return render(request, 'equipment/statistics.html', context)

from .analytics_medications import medication_basic_stats



def medication_statistics(request):
    stats = medication_basic_stats()

    context = {
        'total_objects': stats['total_items'],
        'total_quantity': stats['total_quantity'],
        'critical_count': stats['critical_count'],
        'expired_count': stats['expired_count'],
        'sufficient_count': stats['sufficient_count'],
        'critical_medications': stats['critical'],
        'expired_medications': stats['expired'],
        'forecast': [],  # на майбутнє
    }

    return render(request, 'equipment/medication_statistics.html', context)

