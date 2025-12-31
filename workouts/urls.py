from django.urls import path
from . import views

urlpatterns = [
    path('', views.ExerciseCategoryListView.as_view(), name='home'),
    path('categories/', views.ExerciseCategoryListView.as_view(), name='category-list'),
    path('exercises/<slug:category_slug>/', views.ExerciseListView.as_view(), name='exercise-list'),
    path('workouts/', views.WorkoutDayListView.as_view(), name='workout-list'),
    path('workouts/<int:pk>/', views.WorkoutDayDetailView.as_view(), name='workout-detail'),
    path('workouts/<int:pk>/add-exercise/', views.add_workout_exercise, name='add-exercise'),
    path('workouts/create/', views.CreateWorkoutView.as_view(), name='create-workout'),
]