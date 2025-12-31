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
    # Типы упражнений
    EXERCISE_TYPE_CHOICES = [
        ('NORMAL', 'Обычное'),
        ('DROPSET', 'Дроп-сет'),
        ('SUPERSET', 'Суперсет'),
    ]

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

    # Новые поля для дроп-сетов и суперсетов
    exercise_type = models.CharField(
        max_length=10,
        choices=EXERCISE_TYPE_CHOICES,
        default='NORMAL',
        help_text='Тип упражнения'
    )
    superset_group = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text='Номер группы для суперсета (упражнения с одинаковым номером = один суперсет)'
    )
    # Для дроп-сетов: массив массивов весов
    # Пример: [[10, 5, 2.5], [12, 6, 3]] - первый подход: 10->5->2.5кг, второй: 12->6->3кг
    dropset_weights = models.JSONField(
        blank=True,
        null=True,
        help_text='Массив весов для дроп-сетов: каждый подход содержит массив весов'
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text='Порядок выполнения упражнения в тренировке'
    )

    def get_weights_display(self):
        """Возвращает список весов для отображения"""
        if self.weights:
            return self.weights
        else:
            # Старый формат - дублируем единый вес
            return [self.weight] * self.sets

    def get_weight_summary(self):
        """Краткое описание весов (например '20 кг' или '10-30 кг')"""
        if self.exercise_type == 'DROPSET' and self.dropset_weights:
            # Для дроп-сета показываем диапазон
            all_weights = [w for set_weights in self.dropset_weights for w in set_weights]
            return f"{min(all_weights):g}-{max(all_weights):g} кг (дроп-сет)"

        weights = self.get_weights_display()
        unique_weights = set(weights)
        if len(unique_weights) == 1:
            return f"{weights[0]:g} кг"
        else:
            return f"{min(weights):g}-{max(weights):g} кг"

    def get_dropset_display(self):
        """Возвращает красивое отображение дроп-сета"""
        if self.exercise_type == 'DROPSET' and self.dropset_weights:
            result = []
            for i, set_weights in enumerate(self.dropset_weights, 1):
                weights_str = ' → '.join([f"{w:g}кг" for w in set_weights])
                result.append(f"Подход {i}: {weights_str}")
            return result
        return []

    def is_dropset(self):
        """Проверка является ли упражнение дроп-сетом"""
        return self.exercise_type == 'DROPSET'

    def is_superset(self):
        """Проверка является ли упражнение частью суперсета"""
        return self.exercise_type == 'SUPERSET'

    def get_exercise_type_display_ru(self):
        """Русское название типа упражнения"""
        return dict(self.EXERCISE_TYPE_CHOICES).get(self.exercise_type, 'Обычное')

    def __str__(self):
        return f"{self.exercise.name}"

    class Meta:
        ordering = ['order', 'id']
