from django.contrib import admin
from .models import WorkoutClass, WorkoutPlan, WorkoutPlanPurchase

@admin.register(WorkoutClass)
class WorkoutClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'length', 'price')
    search_fields = ('name',)
    list_filter = ('difficulty',)


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'created_at')
    search_fields = ('title',)

@admin.register(WorkoutPlanPurchase)
class WorkoutPlanPurchaseAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout_plan', 'purchased_at')
    search_fields = ('user__username', 'workout_plan__title')
