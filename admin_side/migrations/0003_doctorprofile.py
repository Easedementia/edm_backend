# Generated by Django 5.0.7 on 2024-07-25 09:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0002_alter_service_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('doctor_name', models.CharField(max_length=255)),
                ('specialization', models.CharField(max_length=150)),
                ('schedule', models.CharField(max_length=150)),
                ('details', models.TextField()),
                ('consulting_fee', models.DecimalField(decimal_places=2, max_digits=10)),
                ('profile_picture', models.ImageField(upload_to='doctor_profile_picture/')),
            ],
        ),
    ]
