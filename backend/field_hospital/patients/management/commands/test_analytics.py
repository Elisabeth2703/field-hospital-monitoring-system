from django.core.management.base import BaseCommand
from patients.analytics import PatientAnalytics
import json

class Command(BaseCommand):
  help = 'Демонстрація можливостей аналітики з NumPy, Pandas, Scikit-learn'

  def handle(self, *args, **options):
    analytics = PatientAnalytics()
    
    self.stdout.write(self.style.SUCCESS('\n' + '='*60))
    self.stdout.write(self.style.SUCCESS('ДЕМОНСТРАЦІЯ АНАЛІТИКИ ДАНИХ'))
    self.stdout.write(self.style.SUCCESS('='*60 + '\n'))
    
    self.stdout.write(self.style.HTTP_INFO('1. Аналіз надходжень за тиждень (Pandas):'))
    week_analysis = analytics.analyze_by_period('week')
    self.stdout.write(f"   Всього пацієнтів: {week_analysis['total_patients']}")
    self.stdout.write(f"   Критичних: {week_analysis['by_severity'].get('Критичний', 0)}")
    self.stdout.write(f"   Середній вік: {week_analysis['age_statistics']['mean']:.1f} років\n")
    
    self.stdout.write(self.style.HTTP_INFO('2. ML Класифікація поранень (Scikit-learn):'))
    classification = analytics.classify_injury_severity()
    if classification:
      for injury, stats in classification.items():
        self.stdout.write(f"   {injury}: середня важкість {stats['average_severity']:.2f}/4.0")
    self.stdout.write('')
    
    self.stdout.write(self.style.HTTP_INFO('3. Прогноз потоку пацієнтів (Linear Regression):'))
    prediction = analytics.predict_patient_flow(7)
    if prediction:
      self.stdout.write(f"   Прогноз на 7 днів: {prediction['predicted_total']:.0f} пацієнтів")
      self.stdout.write(f"   Тренд: {prediction['trend']}")
      self.stdout.write(f"   Точність моделі: {prediction['confidence']:.2f}\n")
    
    self.stdout.write(self.style.HTTP_INFO('4. Кореляційний аналіз (NumPy + Pandas):'))
    correlation = analytics.get_correlation_analysis()
    if correlation:
      self.stdout.write(f"   Кореляція вік-важкість: {correlation['correlation_age_severity']:.3f}\n")
    
    self.stdout.write(self.style.HTTP_INFO('5. Аналіз часових рядів (NumPy):'))
    time_series = analytics.analyze_time_series('BR-001')
    if time_series:
      hr_stats = time_series['statistics']['heart_rate']
      self.stdout.write(f"   Пульс: {hr_stats['mean']:.1f} ± {hr_stats['std']:.1f} bpm")
      self.stdout.write(f"   Тренд: {hr_stats['trend']}")
      self.stdout.write(f"   Аномалій виявлено: {len(time_series['anomalies'])}\n")
    
    self.stdout.write('\n' + self.style.SUCCESS('='*60))
    self.stdout.write(self.style.SUCCESS('ДЕМОНСТРАЦІЮ ЗАВЕРШЕНО УСПІШНО'))
    self.stdout.write(self.style.SUCCESS('='*60 + '\n'))