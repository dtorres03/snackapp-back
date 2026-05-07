"""
Serializadores de Contenido Multimedia - SnackApp.

Este módulo gestiona la transformación compleja de categorías, series y videos.
Implementa representaciones híbridas (ID para escritura, Nombres para lectura)
y optimiza la carga de episodios mediante serialización anidada limitada.
"""

from rest_framework import serializers
from .models import Video, Category, Serie

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializador para la gestión de categorías.
    
    Incluye validaciones personalizadas para asegurar que los nombres de 
    categoría sean únicos y obligatorios.
    """
    class Meta:
        model = Category
        fields = ['id', 'name']
        extra_kwargs = {
            'name': {
                'error_messages': {
                    'blank': 'El nombre de la categoría es obligatorio.',
                    'unique': 'Esta categoría ya existe en el sistema.'
                }
            }
        }

class VideoSerializer(serializers.ModelSerializer):
    """
    Serializador principal para el modelo Video (Episodios e Independientes).

    Implementa una lógica de 'Double Mapping':
        - Escritura: Utiliza campos `_id` para vincular relaciones (Category, Serie).
        - Lectura: Proporciona nombres (`_name`, `username`) y rutas de archivos
          limpias mediante SerializerMethodFields.

    Atributos:
        video_path (str): Ruta relativa del archivo de video en el storage.
        thumbnail_path (str): Ruta relativa de la miniatura en el storage.
        cost (int): Precio en tokens definido en el modelo.
        is_unlocked (bool): Indica si el usuario que realiza la petición tiene acceso al contenido.
    """
    serie_id = serializers.PrimaryKeyRelatedField(
        source='serie', 
        queryset=Serie.objects.all(),
        required=False
    )
    serie_name = serializers.ReadOnlyField(source='serie.title')
    username = serializers.ReadOnlyField(source='user.username')
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', 
        queryset=Category.objects.all()
    )
    category_name = serializers.ReadOnlyField(source='category.name')
    video_file = serializers.FileField(write_only=True)
    thumbnail = serializers.ImageField(write_only=True)
    video_path = serializers.SerializerMethodField()
    thumbnail_path = serializers.SerializerMethodField()
    
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description',
            'cost', 'is_unlocked',
            'serie_id', 'serie_name',
            'season_number', 'episode_number',
            'video_file', 'thumbnail',
            'video_path', 'thumbnail_path', 
            'category_id', 'category_name',
            'user_id' ,'username',
            'created_at'
        ]
        extra_kwargs = {'user': {'read_only': True}}
        
    def get_is_unlocked(self, obj):
        """
        Determina si el usuario actual ha desbloqueado este video.
        Si el usuario es el autor del video (uploader), el acceso es total.
        """
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
            
        if obj.user == request.user:
            return True
            
        return obj.users_with_access.filter(id=request.user.id).exists()
        
    def get_video_path(self, obj):
        """Extrae la ruta del archivo de video si existe."""
        return obj.video_file.name if obj.video_file else None

    def get_thumbnail_path(self, obj):
        """Extrae la ruta de la miniatura si existe."""
        return obj.thumbnail.name if obj.thumbnail else None


class SeriesVideoSerializer(serializers.ModelSerializer):
    """
    Versión actualizada de Video para visualización dentro de colecciones.
    
    Ahora incluye la información completa del episodio para mantener la consistencia
    con VideoSerializer en el frontend.
    """
    serie_id = serializers.PrimaryKeyRelatedField(
        source='serie', 
        queryset=Serie.objects.all(),
        required=False
    )
    serie_name = serializers.ReadOnlyField(source='serie.title')
    username = serializers.ReadOnlyField(source='user.username')
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', 
        queryset=Category.objects.all()
    )
    category_name = serializers.ReadOnlyField(source='category.name')
    video_file = serializers.FileField(write_only=True)
    thumbnail = serializers.ImageField(write_only=True)
    video_path = serializers.SerializerMethodField()
    thumbnail_path = serializers.SerializerMethodField()
    
    is_unlocked = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 
            'cost', 'is_unlocked',
            'serie_id', 'serie_name',
            'season_number', 'episode_number',
            'video_file', 'thumbnail',
            'video_path', 'thumbnail_path', 
            'category_id', 'category_name',
            'user_id' ,'username',
            'created_at'
        ]
        extra_kwargs = {'user': {'read_only': True}}
        
    def get_is_unlocked(self, obj):
        """Misma lógica: Autor o Comprador tienen acceso."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        if obj.user == request.user:
            return True
        return obj.users_with_access.filter(id=request.user.id).exists()

    def get_video_path(self, obj):
        return obj.video_file.name if obj.video_file else None

    def get_thumbnail_path(self, obj):
        return obj.thumbnail.name if obj.thumbnail else None


class SeriesSerializer(serializers.ModelSerializer):
    """
    Serializador para Series con previsualización de episodios.

    Incluye lógica de negocio para mostrar únicamente los primeros 5 
    episodios vinculados, facilitando la creación de vistas tipo 'Landing' 
    donde se muestran las series y sus videos iniciales.
    """
    category = serializers.PrimaryKeyRelatedField(read_only=True)
    poster = serializers.SerializerMethodField()
    videos = serializers.SerializerMethodField()

    class Meta:
        model = Serie
        fields = ['id', 'title', 'category', 'poster', 'videos']

    def get_poster(self, obj):
        """Retorna la ruta del póster promocional."""
        return obj.poster.name if obj.poster else None

    def get_videos(self, obj):
        """
        Obtiene los primeros 5 episodios siguiendo el orden definido 
        en el modelo (Temporada/Episodio).
        """
        episodes = obj.episodes.all()[:5]
        return SeriesVideoSerializer(episodes, many=True).data