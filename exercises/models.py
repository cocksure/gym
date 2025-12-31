from django.db import models


class ExerciseCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Exercise(models.Model):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(
        ExerciseCategory,
        on_delete=models.CASCADE,
        related_name='exercises'
    )
    gif_file = models.FileField(upload_to='exercises/', blank=True, null=True, help_text='Загрузи свой GIF файл')
    gif_url = models.URLField(blank=True, help_text='Или укажи ссылку на GIF')
    equipment = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

    def get_gif(self):
        """Возвращает URL: сначала проверяет загруженный файл, потом ссылку"""
        if self.gif_file:
            return self.gif_file.url
        return self.gif_url
