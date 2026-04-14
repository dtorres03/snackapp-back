from django.db import models
from django.contrib.auth import get_user_model # Para referenciar a tu CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Serie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='series')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Video(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='videos')
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, null=True, blank=True, related_name='episodes')
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Campos de Temporada y Episodio
    season_number = models.PositiveIntegerField(default=1, verbose_name="Temporada")
    episode_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Número de Episodio")
    
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ordenamos por temporada y luego por episodio para que el catálogo tenga sentido
        ordering = ['season_number', 'episode_number', '-created_at']
        # Evita que existan dos episodios con el mismo número en la misma temporada de una serie
        unique_together = ['serie', 'season_number', 'episode_number']

    def __str__(self):
        if self.serie:
            return f"{self.serie.title} - T{self.season_number}E{self.episode_number}: {self.title}"
        return self.title