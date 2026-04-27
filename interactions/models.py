"""
Modelos para la aplicación de Interacciones.

Este módulo define las estructuras de datos para las interacciones sociales 
entre usuarios y contenido, como el sistema de favoritos y feedback.
"""

import uuid
from django.db import models
from django.conf import settings

class Favorite(models.Model):
    """
    Representa la relación de "Me gusta" o "Favorito" entre un Usuario y un Video.

    Atributos:
        id (UUID): Identificador único universal para el registro del favorito.
        user (ForeignKey): Referencia al usuario que marca el video (CustomUser).
        video (ForeignKey): Referencia al video marcado como favorito.
        created_at (DateTimeField): Fecha y hora automática de creación.

    Restricciones:
        - Un usuario no puede marcar el mismo video como favorito más de una vez 
          (Definido en Meta.unique_together).
    """

    
    # Relación con el modelo de usuario personalizado
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    
    # Relación con el modelo Video de la app 'videos'
    video = models.ForeignKey(
        'videos.Video', 
        on_delete=models.CASCADE, 
        related_name='favorites'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Configuraciones adicionales del modelo."""
        unique_together = ('user', 'video')
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'

    def __str__(self):
        """Representación en cadena del objeto Favorito."""
        return f"{self.user.username} - {self.video.title}"