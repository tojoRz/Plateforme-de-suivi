from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class Utilisateurs(AbstractUser):
    photo = models.ImageField(upload_to="users", blank=True, null=True, default="users/default.png")
    is_active = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    