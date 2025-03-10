# Generated by Django 5.0.7 on 2024-08-06 10:42

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0005_timeslot'),
        ('user_side', '0002_enquiries'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=100, null=True)),
                ('user_email', models.CharField(max_length=100, null=True)),
                ('doctor_name', models.CharField(max_length=100, null=True)),
                ('date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_booked', models.BooleanField(default=False)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='admin_side.doctorprofile')),
                ('time_slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_side.timeslot')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
