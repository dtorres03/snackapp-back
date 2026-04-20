import uuid
from django.db import models
from django.conf import settings

class Favorite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Usamos settings.AUTH_USER_MODEL para que sea compatible con cualquier modelo de usuario
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Referencia al modelo Video de la otra app
    video = models.ForeignKey('videos.Video', on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'video')
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'

    def __str__(self):
        return f"{self.user.username} - {self.video.title}"