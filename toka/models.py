from django.db import models
from django.contrib.auth.models import User
import datetime

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
    description = models.TextField(blank=True)  # A short summary or teaser
    content = models.TextField(blank=True)      # Full details shown only after purchase
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='workout_plans/', blank=True, null=True)  # New field for image upload
    created_at = models.DateTimeField(auto_now_add=True)
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
    

class HealthPlan(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)  # A short teaser
    content = models.TextField(blank=True)      # Full plan details, visible only after purchase
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='health_plans/', blank=True, null=True)  # <-- New field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class HealthPlanPurchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='healthplan_purchases')
    health_plan = models.ForeignKey(HealthPlan, on_delete=models.CASCADE, related_name='purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'health_plan')  # One‑time purchase per user

    def __str__(self):
        return f"{self.user.username} purchased {self.health_plan.title}"
    

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    company = models.CharField(max_length=200)
    message = models.TextField(blank=True, null=True)  # Optional message field
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
    



class FacilityBooking(models.Model):
    FACILITY_CHOICES = [
        ('gym', 'Gym'),
        ('pool', 'Pool'),
    ]

    LOCATION_CHOICES = [
        ('north', 'North Branch'),
        ('south', 'South Branch'),
        ('east', 'East Branch'),
        ('west', 'West Branch'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, help_text="Your full name")
    facility_type = models.CharField(
        max_length=10, 
        choices=FACILITY_CHOICES, 
        help_text="Select the facility you want to use"
    )
    location = models.CharField(
        max_length=10, 
        choices=LOCATION_CHOICES, 
        help_text="Choose the branch location"
    )
    date = models.DateField(help_text="Date of your session")
    time = models.TimeField(help_text="Time of your session (9:00-17:00)")
    additional_info = models.TextField(blank=True, help_text="Any additional details (optional)")
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Optional: Validate that time is between 9:00 and 17:00
        if self.time < datetime.time(9, 0) or self.time > datetime.time(17, 0):
            from django.core.exceptions import ValidationError
            raise ValidationError("Time must be between 9:00 AM and 5:00 PM.")

    def __str__(self):
        return f"{self.name} - {self.facility_type} at {self.location} on {self.date} {self.time}"
