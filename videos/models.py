from django.db import models
from django.contrib.auth import get_user_model # Para referenciar a tu CustomUser

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return self.name

class Video(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='videos')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='videos')
    title = models.CharField(max_length=200)
    description = models.TextField()
    video_url = models.URLField()
    thumbnail = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title