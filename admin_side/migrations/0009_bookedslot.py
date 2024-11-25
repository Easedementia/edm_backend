# Generated by Django 5.0.7 on 2024-11-22 06:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0008_alter_timeslot_doctor'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookedSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_booked', models.BooleanField(default=False)),
                ('timeslot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='booked_slots', to='admin_side.timeslot')),
            ],
        ),
    ]