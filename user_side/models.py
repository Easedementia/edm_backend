from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin, Group, Permission



class CustomUserManager(BaseUserManager):
    def create_user(self, fullname, email, mobile, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(fullname=fullname, email=email, mobile=mobile, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)




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


    groups = models.ManyToManyField(Group, blank=True, related_name='custom_user_groups', related_query_name='custom_user')
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='custom_user_permissions',
        related_query_name='custom_user_permission'
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'fullname'
    REQUIRED_FIELDS = ['email', 'mobile', 'password']

    def __str__(self):
        return self.fullname