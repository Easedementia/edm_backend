# Generated by Django 5.0.7 on 2024-09-18 10:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_side', '0007_firstpersonclientdetails'),
    ]

    operations = [
        migrations.AddField(
            model_name='firstpersonclientdetails',
            name='assessment_score',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
