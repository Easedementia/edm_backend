from django.db import models
from .validators import validate_svg
from django.core.exceptions import ValidationError


# Create your models here.


class Service(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.FileField(upload_to='services/', validators=[validate_svg])

    def __str__(self):
        return self.title
    


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


    def clean(self):
        """
        Custom validation to ensure that time slots do not overlap for the same doctor.
        """
        # Check if start_time is before end_time
        if self.start_time >= self.end_time:
            raise ValidationError("Start time must be before end time.")
        
        # Check for overlapping time slots for the same doctor on the same day
        overlapping_slots = TimeSlot.objects.filter(
            doctor=self.doctor,
            day=self.day
        ).exclude(id=self.id)  # Exclude the current instance in case it's an update

        for slot in overlapping_slots:
            # Check for time overlap
            if (self.start_time < slot.end_time and self.end_time > slot.start_time):
                raise ValidationError(f"Time slot {self.start_time} to {self.end_time} overlaps with another time slot.")


    def __str__(self):
        return f"{self.doctor.doctor_name} - {self.day} {self.start_time} to {self.end_time}"
    





class BookedSlot(models.Model):
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name="booked_slots")
    date = models.DateField()
    is_booked = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.timeslot} - {self.date} - {'Booked' if self.is_booked else 'Available'}"