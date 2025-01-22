from django.contrib import admin
from .models import WorkoutClass

@admin.register(WorkoutClass)
class WorkoutClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'length', 'price')
    search_fields = ('name',)
    list_filter = ('difficulty',)
