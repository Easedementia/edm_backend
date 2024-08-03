from django.db import models
from .validators import validate_svg

# Create your models here.


class Service(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.FileField(upload_to='services/', validators=[validate_svg])

    def __str__(self):
        return self.title
    


class DoctorProfile(models.Model):
    doctor_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, default='example@example.com')
    mobile = models.CharField(max_length=15, default='0000000000')
    specialization = models.CharField(max_length=150)
    schedule = models.CharField(max_length=150)
    details = models.TextField()
    consulting_fee = models.DecimalField(max_digits=10, decimal_places=2)
    profile_picture = models.ImageField(upload_to='doctor_profile_picture/')

    def __str__(self):
        return self.doctor_name
    


class TimeSlot(models.Model):
    day_choices = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    day = models.CharField(max_length=15, choices=day_choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, null=True)
    is_booked = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.doctor.doctor_name} - {self.day} {self.start_time} to {self.end_time}"