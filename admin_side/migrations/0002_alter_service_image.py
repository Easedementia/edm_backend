# Generated by Django 5.0.7 on 2024-07-22 18:53

import admin_side.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='service',
            name='image',
            field=models.FileField(upload_to='services/', validators=[admin_side.validators.validate_svg]),
        ),
    ]