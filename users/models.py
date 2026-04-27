"""
Modelos de Identidad y Acceso - SnackApp.

Este módulo define la estructura de datos para los usuarios del sistema,
utilizando UUIDs como identificadores y el correo electrónico como credencial principal.
"""

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    """
    Modelo de Usuario personalizado con autenticación basada en Email.

    Hereda de `AbstractUser` para integrar el sistema de permisos de Django.
    Sustituye la PK por defecto por un UUID y configura el correo electrónico 
    como el campo de identidad principal para el inicio de sesión.

    Atributos:
        id (UUID): Clave primaria única generada automáticamente.
        email (EmailField): Correo electrónico único para autenticación.
        username (CharField): Nombre de visualización único.
        created_at (DateTimeField): Fecha de registro en el sistema.
    """

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Configuración de credenciales
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        """Retorna el nombre de usuario para representación en consola y Admin."""
        return self.username