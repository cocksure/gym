from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import models
from exercises.models import ExerciseCategory, Exercise
from .models import WorkoutDay, WorkoutExercise


class ExerciseCategoryListView(ListView):
    model = ExerciseCategory
    template_name = 'workouts/category_list.html'
    context_object_name = 'categories'


class ExerciseListView(ListView):
    model = Exercise
    template_name = 'workouts/exercise_list.html'
    context_object_name = 'exercises'

    def get_queryset(self):
        queryset = super().get_queryset()
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            context['category'] = get_object_or_404(ExerciseCategory, slug=category_slug)
        return context


class WorkoutDayListView(LoginRequiredMixin, ListView):
    model = WorkoutDay
    template_name = 'workouts/workout_list.html'
    context_object_name = 'workouts'
    ordering = ['-date']

    def get_queryset(self):
        return WorkoutDay.objects.filter(user=self.request.user).order_by('-date')


class WorkoutDayDetailView(LoginRequiredMixin, DetailView):
    model = WorkoutDay
    template_name = 'workouts/workout_detail.html'
    context_object_name = 'workout'

    def get_queryset(self):
        return WorkoutDay.objects.filter(user=self.request.user)


@login_required
def add_workout_exercise(request, pk):
    workout_day = get_object_or_404(WorkoutDay, pk=pk, user=request.user)

    # Проверяем, добавляем ли в существующий суперсет
    superset_group_param = request.GET.get('superset_group') or request.POST.get('superset_group')

    if request.method == 'POST':
        exercise_id = request.POST.get('exercise')
        sets = request.POST.get('sets')
        reps = request.POST.get('reps')
        exercise_type = request.POST.get('exercise_type', 'NORMAL')

        exercise = get_object_or_404(Exercise, pk=exercise_id)

        # Определяем порядок упражнения
        last_order = workout_day.workout_exercises.aggregate(
            max_order=models.Max('order')
        )['max_order'] or 0
        new_order = last_order + 1

        # Обработка в зависимости от типа упражнения
        if exercise_type == 'DROPSET':
            # Дроп-сет: парсим веса через запятую
            dropset_weights = []
            for i in range(1, int(sets) + 1):
                dropset_input = request.POST.get(f'dropset_{i}')
                if dropset_input:
                    # Парсим строку "10, 5, 2.5" -> [10.0, 5.0, 2.5]
                    set_weights = [float(w.strip()) for w in dropset_input.split(',')]
                    dropset_weights.append(set_weights)

            if dropset_weights and len(dropset_weights) == int(sets):
                # Среднее значение всех весов для совместимости
                all_weights = [w for set_w in dropset_weights for w in set_w]
                avg_weight = sum(all_weights) / len(all_weights) if all_weights else 0

                WorkoutExercise.objects.create(
                    workout_day=workout_day,
                    exercise=exercise,
                    sets=sets,
                    reps=reps,
                    weight=avg_weight,
                    weights=None,
                    exercise_type='DROPSET',
                    dropset_weights=dropset_weights,
                    order=new_order
                )

        elif exercise_type == 'SUPERSET':
            # Суперсет: получаем или создаем номер группы
            if superset_group_param:
                # Добавляем к существующему суперсету
                superset_group = int(superset_group_param)
            else:
                # Создаем новый суперсет
                last_superset = workout_day.workout_exercises.filter(
                    exercise_type='SUPERSET'
                ).aggregate(max_group=models.Max('superset_group'))['max_group']
                superset_group = (last_superset or 0) + 1

            # Получаем обычные веса
            weights = []
            for i in range(1, int(sets) + 1):
                weight_value = request.POST.get(f'weight_{i}')
                if weight_value:
                    weights.append(float(weight_value))

            if len(weights) == int(sets):
                avg_weight = sum(weights) / len(weights) if weights else 0

                WorkoutExercise.objects.create(
                    workout_day=workout_day,
                    exercise=exercise,
                    sets=sets,
                    reps=reps,
                    weight=avg_weight,
                    weights=weights,
                    exercise_type='SUPERSET',
                    superset_group=superset_group,
                    order=new_order
                )

        else:
            # Обычное упражнение
            weights = []
            for i in range(1, int(sets) + 1):
                weight_value = request.POST.get(f'weight_{i}')
                if weight_value:
                    weights.append(float(weight_value))

            if len(weights) == int(sets):
                avg_weight = sum(weights) / len(weights) if weights else 0

                WorkoutExercise.objects.create(
                    workout_day=workout_day,
                    exercise=exercise,
                    sets=sets,
                    reps=reps,
                    weight=avg_weight,
                    weights=weights,
                    exercise_type='NORMAL',
                    order=new_order
                )

        return redirect('workout-detail', pk=pk)

    # Фильтруем упражнения по выбранным категориям тренировки
    if workout_day.categories.exists():
        categories = workout_day.categories.all()
    else:
        # Если категории не выбраны, показываем все
        categories = ExerciseCategory.objects.all()

    exercises_by_category = {}
    for category in categories:
        exercises_by_category[category] = category.exercises.all()

    return render(request, 'workouts/add_exercise.html', {
        'workout_day': workout_day,
        'exercises_by_category': exercises_by_category,
        'superset_group': superset_group_param
    })


class CreateWorkoutView(LoginRequiredMixin, CreateView):
    model = WorkoutDay
    template_name = 'workouts/create_workout.html'
    fields = ['date', 'categories', 'notes']  # Убрали 'name' - будет генерироваться автоматически
    success_url = reverse_lazy('workout-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = ExerciseCategory.objects.all()
        return context

    def form_valid(self, form):
        # Сохраняем без коммита для доступа к объекту
        self.object = form.save(commit=False)

        # Устанавливаем пользователя
        self.object.user = self.request.user

        # Генерируем название из категорий
        categories = form.cleaned_data.get('categories')
        if categories:
            category_names = [cat.name for cat in categories]
            self.object.name = ' + '.join(category_names)

        # Сохраняем объект и ManyToMany связи
        self.object.save()
        form.save_m2m()

        return HttpResponseRedirect(self.get_success_url())


@login_required
def delete_workout_exercise(request, pk):
    """Удаление упражнения из тренировки"""
    exercise = get_object_or_404(WorkoutExercise, pk=pk)
    workout_day = exercise.workout_day

    # Проверка прав доступа
    if workout_day.user != request.user:
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        exercise.delete()
        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid method'}, status=405)


@login_required
def edit_workout_exercise(request, pk):
    """Редактирование упражнения из тренировки"""
    workout_exercise = get_object_or_404(WorkoutExercise, pk=pk)
    workout_day = workout_exercise.workout_day

    # Проверка прав доступа
    if workout_day.user != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        sets = request.POST.get('sets')
        reps = request.POST.get('reps')

        # Обновляем базовые поля
        workout_exercise.sets = sets
        workout_exercise.reps = reps

        # Обновляем веса в зависимости от типа упражнения
        if workout_exercise.exercise_type == 'DROPSET':
            # Дроп-сет: парсим веса через запятую
            dropset_weights = []
            for i in range(1, int(sets) + 1):
                dropset_input = request.POST.get(f'dropset_{i}')
                if dropset_input:
                    set_weights = [float(w.strip()) for w in dropset_input.split(',')]
                    dropset_weights.append(set_weights)

            if dropset_weights and len(dropset_weights) == int(sets):
                all_weights = [w for set_w in dropset_weights for w in set_w]
                avg_weight = sum(all_weights) / len(all_weights) if all_weights else 0
                workout_exercise.weight = avg_weight
                workout_exercise.dropset_weights = dropset_weights
        else:
            # Обычное упражнение или суперсет
            weights = []
            for i in range(1, int(sets) + 1):
                weight_value = request.POST.get(f'weight_{i}')
                if weight_value:
                    weights.append(float(weight_value))

            if len(weights) == int(sets):
                avg_weight = sum(weights) / len(weights) if weights else 0
                workout_exercise.weight = avg_weight
                workout_exercise.weights = weights

        workout_exercise.save()
        return redirect('workout-detail', pk=workout_day.pk)

    # Используем тот же шаблон что и для добавления, но в режиме редактирования
    return render(request, 'workouts/add_exercise.html', {
        'workout_day': workout_day,
        'editing_exercise': workout_exercise,  # Флаг режима редактирования
        'exercises_by_category': {},  # Пустой список упражнений
        'superset_group': None
    })
