# Generated by Django 5.0.7 on 2024-09-28 08:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_side', '0009_remove_firstpersonclientdetails_message_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='firstpersonclientdetails',
            name='user_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='firstpersonclientdetails',
            name='user_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
