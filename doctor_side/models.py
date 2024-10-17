from django.db import models

# Create your models here.

class DoctorProfile(models.Model):
    CATEGORY_CHOICES = [
        ('doctor', 'Doctor'),
        ('geriatric_counselor', 'Geriatric Counselor'),
    ]
    doctor_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, default='example@example.com')
    mobile = models.CharField(max_length=15, default='0000000000')
    specialization = models.CharField(max_length=150)
    schedule = models.CharField(max_length=150)
    details = models.TextField()
    consulting_fee = models.DecimalField(max_digits=10, decimal_places=2)
    profile_picture = models.ImageField(upload_to='doctor_profile_picture/')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='doctor')

    def __str__(self):
        return self.doctor_name