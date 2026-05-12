"""
Serializadores para la aplicación de Interacciones.

Este módulo gestiona la transformación de los modelos de interacción (Favoritos)
a formatos JSON, manejando la lógica de validación y la representación 
anidada de datos de otras aplicaciones.
"""

from rest_framework import serializers
from .models import Favorite, Comment
from videos.serializers import VideoSerializer

class FavoriteSerializer(serializers.ModelSerializer):
    """
    Serializador para el modelo Favorite.

    Este serializador permite la creación de favoritos vinculando un usuario 
    autenticado con un video, y proporciona una representación detallada del 
    video en las respuestas de lectura.

    Atributos:
        video_details (VideoSerializer): Representación anidada de solo lectura 
            del video vinculado, útil para mostrar miniaturas y títulos en el frontend.
    
    Campos de Metadatos:
        video: Identificador (UUID) del video al realizar la creación (Escritura).
        video_details: Objeto completo del video (Lectura).
        user: El usuario se asigna automáticamente en el ViewSet desde la petición.
    """
    
    # Mostramos el detalle completo del video en los GET
    video_details = VideoSerializer(source='video', read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'video', 'video_details', 'created_at']
        read_only_fields = ['user']
        
class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.ReadOnlyField(source='user.username')
    user_avatar = serializers.SerializerMethodField()
    likes_count = serializers.ReadOnlyField(source='total_likes')
    replies_count = serializers.ReadOnlyField(source='total_replies')
    
    # Lógica para respuestas anidadas
    replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            'id', 'video', 'user', 'user_username', 'user_avatar', 
            'content', 'parent', 'likes_count', 'replies_count', 
            'replies', 'created_at'
        ]
        read_only_fields = ['user']

    def get_user_avatar(self, obj):
        request = self.context.get('request')
        # Buscamos la imagen en el modelo relacionado (ejemplo: Profile)
        if hasattr(obj.user, 'profile') and obj.user.profile.image:
            return request.build_absolute_uri(obj.user.profile.image.url)
        return None

    def get_replies(self, obj):
        # Solo mostramos respuestas si el comentario es un 'padre' (parent=None)
        # Esto evita hilos infinitos que rompen el JSON
        if obj.parent is None:
            return CommentSerializer(
                obj.replies.all(), 
                many=True, 
                context=self.context
            ).data
        return []