# Generated by Django 4.1.13 on 2024-07-10 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('mobile', models.CharField(max_length=15, unique=True)),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Others')], max_length=1)),
                ('password', models.CharField(max_length=255)),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='profile_pictures/')),
                ('is_blocked', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, related_name='custom_user_groups', related_query_name='custom_user', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='custom_user_permissions', related_query_name='custom_user_permission', to='auth.permission')),
            ],
        ),
    ]
