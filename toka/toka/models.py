from django.db import models
from django.contrib.auth.models import User

class WorkoutClass(models.Model):
    name = models.CharField(max_length=255)
    difficulty = models.CharField(
        max_length=50,
        choices=[
            ('Beginner', 'Beginner'),
            ('Intermediate', 'Intermediate'),
            ('Advanced', 'Advanced')
        ]
    )
    length = models.IntegerField()  # Length in minutes
    price = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(upload_to='workouts/')
    description = models.TextField(blank=True)
    members_only = models.BooleanField(default=False)  # Restrict access

    def __str__(self):
        return self.name

MEMBERSHIP_CHOICES = (
    ('free', 'Free'),
    ('student', 'Student'),
    ('premium', 'Premium'),
)

class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership_type = models.CharField(max_length=20, choices=MEMBERSHIP_CHOICES, default='free')
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.membership_type}"
    

class WorkoutPlan(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class WorkoutPlanPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plan_purchases')
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'workout_plan')  # Ensure one‑time purchase per user

    def __str__(self):
        return f"{self.user.username} purchased {self.workout_plan.title}"