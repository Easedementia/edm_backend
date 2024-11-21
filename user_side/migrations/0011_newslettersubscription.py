# Generated by Django 5.0.7 on 2024-10-10 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_side', '0010_firstpersonclientdetails_user_email_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='NewsLetterSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('subscribed_on', models.DateField(auto_now_add=True)),
            ],
        ),
    ]