from django.contrib.auth.models import AbstractUser
from django.db import models

NULLABLE = {'blank': True, 'null': True}


class User(AbstractUser):
    username = None
    email = models.CharField(verbose_name='email', unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    avatar = models.ImageField(verbose_name='аватар', upload_to='users/', **NULLABLE)
    telegram = models.CharField(verbose_name='telegram_id', unique=True)
