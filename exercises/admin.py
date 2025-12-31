from django.contrib import admin
from .models import ExerciseCategory, Exercise


@admin.register(ExerciseCategory)
class ExerciseCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('category', 'name',  'equipment', 'has_gif_file', 'has_gif_url')
    list_filter = ('category', 'equipment')
    search_fields = ('name',)
    list_per_page = 20
    fields = ('name', 'category', 'equipment', 'gif_file', 'gif_url')
    list_editable = ['name',]

    def has_gif_file(self, obj):
        return bool(obj.gif_file)
    has_gif_file.boolean = True
    has_gif_file.short_description = 'Файл'

    def has_gif_url(self, obj):
        return bool(obj.gif_url)
    has_gif_url.boolean = True
    has_gif_url.short_description = 'URL'
