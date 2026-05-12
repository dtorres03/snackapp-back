"""
Modelos para la aplicación de Interacciones.

Este módulo define las estructuras de datos para las interacciones sociales 
entre usuarios y contenido, como el sistema de favoritos y feedback.
"""

import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from videos.models import Video

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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
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
    
class Comment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_likes', blank=True)

    # Lógica de Respuestas (Threads)
    # Si parent es null, es un comentario principal.
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    
    # Lógica de Likes
    # Permite que muchos usuarios den like a muchos comentarios.
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='comment_likes', blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.content[:20]}"
    
    @property
    def total_likes(self):
        """Devuelve el conteo de likes del comentario."""
        return self.likes.count()

    @property
    def total_replies(self):
        """Devuelve el conteo de respuestas a este comentario."""
        return self.replies.count()

    @property
    def is_reply(self):
        """Identifica si es una respuesta o un comentario raíz."""
        return self.parent is not None
    
class VideoLike(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='video_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Crucial: Un usuario solo puede dar UN like por video
        unique_together = ('user', 'video') 

    def __str__(self):
        return f"{self.user.username} likes {self.video.title}"
    