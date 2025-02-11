from django.db import models
from admin_side.models import *
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, Permission
from datetime import datetime




class CustomUserManager(BaseUserManager):
    def create_user(self, fullname, email, mobile, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(fullname=fullname, email=email, mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, fullname, email, mobile, password=None, **extra_fields):
        # Create and return a superuser with an email and password.
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(fullname, email, mobile, password, **extra_fields)





class CustomUser(AbstractBaseUser, PermissionsMixin):
    fullname = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15)
    password = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, blank=True, related_name='custom_user_groups', related_query_name='custom_user')
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='custom_user_permissions',
        related_query_name='custom_user_permission'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['fullname', 'mobile']

    def __str__(self):
        return self.fullname
    

class Enquiries(models.Model):
    fullname = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    message = models.TextField(blank=False)

    def __str__(self):
        return self.fullname



class Appointment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user_name = models.CharField(max_length=100, null=True)
    user_email = models.CharField(max_length=100, null=True)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, null=True)
    doctor_name = models.CharField(max_length=100, null=True)
    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_booked = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.user} - {self.doctor} - {self.date}"
    



class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    user_name = models.CharField(max_length=100, null=True)
    user_email = models.CharField(max_length=100, null=True)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, null=True)
    doctor_name = models.CharField(max_length=100, null=True)
    order_amount = models.CharField(max_length=25)
    order_payment_id = models.CharField(max_length=100)
    isPaid = models.BooleanField(default=False)
    order_date = models.DateTimeField(auto_now=True)
    time_slot_date = models.DateField(null=True)
    time_slot_day = models.CharField(max_length=100, null=True)  
    time_slot_start_time = models.TimeField(null=True) 
    time_slot_end_time = models.TimeField(null=True)
    meet_link = models.URLField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')


    def __str__(self):
        return f"Order {self.id} by {self.user_name} for {self.doctor_name}"
    



class FirstPersonClientDetails(models.Model):
    fullname = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    user_name = models.CharField(max_length=255, null=True, blank=True)
    user_email = models.EmailField(null=True, blank=True)
    age = models.CharField(max_length=50, null=True, blank=True)
    assessment_score = models.IntegerField(null=True, blank=True)
    interpretation = models.CharField(max_length=255, null=True, blank=True)
    assessment_date = models.DateField(default=datetime.now, blank=True)

    def __str__(self):
        return self.fullname
    



class NewsLetterSubscription(models.Model):
    email = models.EmailField(unique=True)
    subscribed_on = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.email
    



class SelfAssessment(models.Model):
    fullname = models.CharField(max_length=255)
    email = models.EmailField()
    mobile = models.CharField(max_length=20, null=True, blank=True)
    user_id = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)
    score = models.IntegerField()


    def __str__(self):
        return f"{self.fullname} - Score: {self.score}"