from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

from exercises.models import Exercise, ExerciseCategory


class WorkoutDay(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts', help_text='Пользователь', null=True, blank=True)
    date = models.DateField(default=timezone.now, help_text='Дата тренировки')
    name = models.CharField(max_length=200, blank=True, help_text='Опциональное название')
    categories = models.ManyToManyField(ExerciseCategory, blank=True, related_name='workouts', help_text='Выберите категории упражнений')
    notes = models.TextField(blank=True, help_text='Заметки о тренировке')

    def __str__(self):
        if self.name:
            return f"{self.date} – {self.name}"
        return f"Тренировка {self.date}"

    class Meta:
        ordering = ['-date']


class WorkoutExercise(models.Model):
    workout_day = models.ForeignKey(
        WorkoutDay,
        on_delete=models.CASCADE,
        related_name='workout_exercises'
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveIntegerField()
    reps = models.PositiveIntegerField()
    weight = models.FloatField()  # Оставить для совместимости

    # Массив весов для каждого подхода
    weights = models.JSONField(blank=True, null=True, help_text='Массив весов для каждого подхода')

    def get_weights_display(self):
        """Возвращает список весов для отображения"""
        if self.weights:
            return self.weights
        else:
            # Старый формат - дублируем единый вес
            return [self.weight] * self.sets

    def get_weight_summary(self):
        """Краткое описание весов (например '20 кг' или '10-30 кг')"""
        weights = self.get_weights_display()
        unique_weights = set(weights)
        if len(unique_weights) == 1:
            return f"{weights[0]} кг"
        else:
            return f"{min(weights)}-{max(weights)} кг"

    def __str__(self):
        return f"{self.exercise.name}"
