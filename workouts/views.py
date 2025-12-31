from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
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

    if request.method == 'POST':
        exercise_id = request.POST.get('exercise')
        sets = request.POST.get('sets')
        reps = request.POST.get('reps')

        # Получаем массив весов (weight_1, weight_2, ...)
        weights = []
        for i in range(1, int(sets) + 1):
            weight_value = request.POST.get(f'weight_{i}')
            if weight_value:
                weights.append(float(weight_value))

        if exercise_id and sets and reps and len(weights) == int(sets):
            exercise = get_object_or_404(Exercise, pk=exercise_id)

            # Среднее значение для поля weight (совместимость)
            avg_weight = sum(weights) / len(weights) if weights else 0

            WorkoutExercise.objects.create(
                workout_day=workout_day,
                exercise=exercise,
                sets=sets,
                reps=reps,
                weight=avg_weight,
                weights=weights  # Новый массив
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
        'exercises_by_category': exercises_by_category
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
