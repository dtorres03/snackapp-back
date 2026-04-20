from rest_framework import serializers
from .models import Favorite
from videos.serializers import VideoSerializer # Importamos de la otra app

class FavoriteSerializer(serializers.ModelSerializer):
    # Mostramos el detalle completo del video en los GET
    video_details = VideoSerializer(source='video', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'video', 'video_details', 'created_at']
        read_only_fields = ['user']