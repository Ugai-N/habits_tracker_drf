from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    username = None
    email = models.CharField(verbose_name='email', unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
