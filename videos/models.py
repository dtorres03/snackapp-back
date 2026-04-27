"""
Modelos de Contenido Multimedia - SnackApp.

Este módulo define la estructura jerárquica del catálogo de videos, gestionando
categorías, series y episodios individuales. Utiliza UUIDs para todos los
recursos y soporta la organización por temporadas y números de episodio.
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model

class Category(models.Model):
    """
    Representa una clasificación temática para el contenido (ej. Acción, Comedia).

    Atributos:
        id (UUID): Identificador único universal.
        name (str): Nombre de la categoría.
    """

    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Serie(models.Model):
    """
    Agrupador de contenido que comparte una narrativa o temática común.

    Atributos:
        id (UUID): Identificador único universal.
        title (str): Título de la serie.
        description (str): Sinopsis o descripción general.
        poster (Image): Imagen promocional de la serie.
        category (ForeignKey): Referencia a la categoría principal.
        created_at (DateTimeField): Fecha de registro de la serie.
    """

    title = models.CharField(max_length=200)
    description = models.TextField()
    poster = models.ImageField(upload_to='posters/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='series')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Video(models.Model):
    """
    Unidad mínima de contenido multimedia (pueden ser episodios o videos independientes).

    Este modelo gestiona la lógica de reproducción y organización dentro de las series.
    Si un video está vinculado a una 'Serie', actúa como un episodio.

    Atributos:
        user (ForeignKey): Usuario (Uploader) que subió el contenido.
        serie (ForeignKey): Serie a la que pertenece el episodio (opcional).
        season_number (int): Número de temporada (por defecto 1).
        episode_number (int): Posición del video dentro de la temporada.
        video_file (File): Archivo de video almacenado en el servidor.
        thumbnail (Image): Imagen de previsualización del video.

    Restricciones de Integridad:
        - unique_together: Impide la duplicidad de números de episodio dentro de 
          una misma temporada para una serie específica.
    """

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='videos')
    serie = models.ForeignKey(Serie, on_delete=models.CASCADE, null=True, blank=True, related_name='episodes')
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    season_number = models.PositiveIntegerField(default=1, verbose_name="Temporada")
    episode_number = models.PositiveIntegerField(null=True, blank=True, verbose_name="Número de Episodio")
    
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Configuración de ordenamiento y restricciones de base de datos."""
        # El catálogo se presenta cronológicamente por estructura de serie
        ordering = ['season_number', 'episode_number', '-created_at']
        unique_together = ['serie', 'season_number', 'episode_number']

    def __str__(self):
        """Retorna una representación formateada para el catálogo (ej. Serie - T1E5)."""
        if self.serie:
            return f"{self.serie.title} - T{self.season_number}E{self.episode_number}: {self.title}"
        return self.title