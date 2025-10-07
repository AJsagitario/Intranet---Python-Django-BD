from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from unidecode import unidecode

def avatar_upload_to(instance, filename):
    return f"avatars/{instance.username}/{filename}"

class Area(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)  # ← ya no obligatorio

    class Meta:
        verbose_name = "Área"
        verbose_name_plural = "Áreas"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

class User(AbstractUser):
    area   = models.ForeignKey(Area, null=True, blank=True, on_delete=models.SET_NULL, related_name="users")
    avatar = models.ImageField(upload_to=avatar_upload_to, null=True, blank=True)
    # Nota: is_staff = acceso al admin; is_superuser = todos los permisos

