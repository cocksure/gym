from django.contrib import admin
from .models import WorkoutDay, WorkoutExercise


class WorkoutExerciseInline(admin.TabularInline):
    model = WorkoutExercise
    extra = 1
    fields = ('exercise', 'sets', 'reps', 'weight')


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ('date', 'name', 'get_exercises_count')
    list_filter = ('date',)
    search_fields = ('name', 'notes')
    inlines = [WorkoutExerciseInline]
    date_hierarchy = 'date'

    def get_exercises_count(self, obj):
        return obj.workout_exercises.count()
    get_exercises_count.short_description = 'Упражнений'


@admin.register(WorkoutExercise)
class WorkoutExerciseAdmin(admin.ModelAdmin):
    list_display = ('workout_day', 'exercise', 'sets', 'reps', 'weight')
    list_filter = ('workout_day__date', 'exercise__category')
    search_fields = ('exercise__name',)
