from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True) # Campo explícito
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'  # Se loguean con Email
    REQUIRED_FIELDS = ['username'] # Al crear por consola pedirá el username

    def __str__(self):
        return self.username