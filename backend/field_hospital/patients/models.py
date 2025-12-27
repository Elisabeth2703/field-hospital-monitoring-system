from djongo import models
from django.contrib.auth.hashers import make_password, check_password

class Patient(models.Model):
  SEVERITY_CHOICES = [
    ('Легкий', 'Легкий'),
    ('Середній', 'Середній'),
    ('Важкий', 'Важкий'),
    ('Критичний', 'Критичний'),
  ]
    
  INJURY_TYPES = [
    ('Вогнепальне поранення', 'Вогнепальне поранення'),
    ('Осколкове поранення', 'Осколкове поранення'),
    ('Контузія', 'Контузія'),
    ('Опіки', 'Опіки'),
    ('Переломи', 'Переломи'),
    ('М\'які тканини', 'М\'які тканини'),
    ('Внутрішні травми', 'Внутрішні травми'),
    ('Інше', 'Інше'),
  ]

  _id = models.ObjectIdField(primary_key=True)
  full_name = models.CharField(max_length=200, verbose_name="ПІБ")
  age = models.IntegerField(verbose_name="Вік")
  bracelet_id = models.CharField(max_length=50, unique=True, verbose_name="ID браслету")
  injury_type = models.CharField(max_length=100, choices=INJURY_TYPES, verbose_name="Тип поранення")
  severity = models.CharField(max_length=50, choices=SEVERITY_CHOICES, verbose_name="Важкість стану")
  admission_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата прийому")
  bed_number = models.CharField(max_length=10, blank=True, verbose_name="Номер ліжка")
  blood_type = models.CharField(max_length=5, blank=True, verbose_name="Група крові")
  status = models.CharField(max_length=50, default='На лікуванні', verbose_name="Статус")
  notes = models.TextField(blank=True, verbose_name="Примітки")

  class Meta:
    db_table = 'patients'
    verbose_name = "Пацієнт"
    verbose_name_plural = "Пацієнти"
    
  def __str__(self):
    return f"{self.full_name} - {self.bracelet_id}"
    
class VitalSigns(models.Model):
  """Життєві показники з MQTT браслетів"""
  _id = models.ObjectIdField(primary_key=True)
  patient_bracelet_id = models.CharField(max_length=50, verbose_name="ID браслету пацієнта")
  timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Час вимірювання")
  heart_rate = models.IntegerField(verbose_name="Пульс (уд/хв)")
  temperature = models.FloatField(verbose_name="Температура (°C)")
  blood_pressure_sys = models.IntegerField(default=120, verbose_name="Тиск систолічний")
  blood_pressure_dia = models.IntegerField(default=80, verbose_name="Тиск діастолічний")
  oxygen_saturation = models.IntegerField(verbose_name="Сатурація O₂ (%)")

  class Meta:
    db_table = 'vital_signs'
    verbose_name = "Життєві показники"
    verbose_name_plural = "Життєві показники"
    
  def __str__(self):
    return f"Показники для {self.patient_bracelet_id} - {self.timestamp}"

class InjuryClassification(models.Model):
  """Класифікація поранень для аналітики"""
  _id = models.ObjectIdField()
  patient_bracelet_id = models.CharField(max_length=50, verbose_name="ID браслету пацієнта")
  injury_type = models.CharField(max_length=100, verbose_name="Тип поранення")
  severity = models.CharField(max_length=50, verbose_name="Важкість")
  diagnosis = models.TextField(verbose_name="Діагноз")
  treatment_plan = models.TextField(blank=True, verbose_name="План лікування")
  classification_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата класифікації")
  
  class Meta:
    db_table = 'injury_classifications'
    verbose_name = "Класифікація поранення"
    verbose_name_plural = "Класифікації поранень"
  
  def __str__(self):
    return f"{self.injury_type} - {self.severity}"
  

class MedicalStaff(models.Model):
  """Модель медичного персоналу"""
  
  ROLE_CHOICES = [
    ('Лікар', 'Лікар'),
    ('Медсестра', 'Медсестра'),
    ('Адміністратор', 'Адміністратор'),
    ('Парамедик', 'Парамедик'),
  ]
  
  _id = models.ObjectIdField()
  username = models.CharField(max_length=50, unique=True, verbose_name="Логін")
  password = models.CharField(max_length=255, verbose_name="Пароль (хеш)")
  full_name = models.CharField(max_length=200, verbose_name="ПІБ")
  role = models.CharField(max_length=50, choices=ROLE_CHOICES, verbose_name="Роль")
  email = models.EmailField(blank=True, verbose_name="Email")
  phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
  specialization = models.CharField(max_length=100, blank=True, verbose_name="Спеціалізація")
  registration_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата реєстрації")
  last_login = models.DateTimeField(null=True, blank=True, verbose_name="Останній вхід")
  is_active = models.BooleanField(default=True, verbose_name="Активний")
  avatar = models.CharField(max_length=10, default='👤', verbose_name="Аватар (emoji)")
  
  class Meta:
    db_table = 'medical_staff'
    verbose_name = "Медичний працівник"
    verbose_name_plural = "Медичні працівники"
  
  def __str__(self):
    return f"{self.full_name} ({self.role})"
  
  def set_password(self, raw_password):
    """Зашифрувати пароль"""
    self.password = make_password(raw_password)
  
  def check_password(self, raw_password):
    """Перевірити пароль"""
    return check_password(raw_password, self.password)