# Generated by Django 5.0.7 on 2025-02-01 05:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('admin_side', '0010_question'),
        ('user_side', '0016_remove_userresponse_assessment_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Question',
        ),
    ]
