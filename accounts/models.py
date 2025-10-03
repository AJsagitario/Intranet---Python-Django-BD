from django.contrib.auth.models import AbstractUser
from django.db import models

class Area(models.Model):
    name = models.CharField(max_length=60, unique=True)
    def __str__(self): return self.name

class User(AbstractUser):
    area = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL)
    is_admin = models.BooleanField(default=False)  # tu “admin” manual

