from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager
import random


def get_expiry_time():
    return timezone.now() + timedelta(minutes=15)


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    class RoleChoices(models.TextChoices):
        ADMIN = 'AD', 'Admin'
        BAYER = 'BY', 'Bayer'
        SELLER = 'SL', 'Seller'
    avatar = models.ImageField(upload_to='users_avatars/', default='users_avatars/placeholder.png')



    username = None
    email = models.EmailField(unique=True)
    telegram_id = models.BigIntegerField(null=True, blank=True)
    telegram_token = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(upload_to='users_avatars/', default='users_avatars/placeholder.png')
    role = models.CharField(
        max_length=2,
        choices=RoleChoices.choices,
        default=RoleChoices.BAYER
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()


    def __str__(self):
        return self.email


class VerificationCode(models.Model):
    email = models.EmailField()
    code = models.CharField(max_length=6)
    expires_at = models.DateTimeField(default=get_expiry_time)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def refresh_code(self):
        self.code = str(random.randint(100000, 999999))
        self.expires_at = get_expiry_time()
        self.save()
    
    