from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    pass


class Theme(models.Model):
    name = models.CharField(max_length=200, unique=True)
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.name
