from djongo import models

class Patient(models.Model):
    """Модель пацієнта"""
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
        ("М'які тканини", "М'які тканини"),
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
    """Життєві показники з браслетів"""
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
    _id = models.ObjectIdField(primary_key=True)
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
