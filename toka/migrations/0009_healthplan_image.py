# Generated by Django 5.0.6 on 2025-02-20 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('toka', '0008_workoutplan_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='healthplan',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='health_plans/'),
        ),
    ]
