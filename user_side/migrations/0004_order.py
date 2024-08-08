# Generated by Django 5.0.7 on 2024-08-07 10:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0005_timeslot'),
        ('user_side', '0003_appointment'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=100, null=True)),
                ('user_email', models.CharField(max_length=100, null=True)),
                ('doctor_name', models.CharField(max_length=100, null=True)),
                ('order_amount', models.CharField(max_length=25)),
                ('order_payment_id', models.CharField(max_length=100)),
                ('isPaid', models.BooleanField(default=False)),
                ('order_date', models.DateTimeField(auto_now=True)),
                ('time_slot_date', models.DateField(null=True)),
                ('time_slot_day', models.CharField(max_length=100, null=True)),
                ('time_slot_start_time', models.TimeField(null=True)),
                ('time_slot_end_time', models.TimeField(null=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], default='Pending', max_length=20)),
                ('doctor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='admin_side.doctorprofile')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
