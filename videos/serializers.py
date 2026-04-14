from rest_framework import serializers
from .models import Video, Category, Serie

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        # 🔹 Definimos los campos exactos (Mejor que '__all__')
        fields = ['id', 'name']
        
        # 🔹 Configuraciones de validación y mensajes
        extra_kwargs = {
            'name': {
                'error_messages': {
                    'blank': 'El nombre de la categoría es obligatorio.',
                    'unique': 'Esta categoría ya existe en el sistema.'
                }
            }
        }

class VideoSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = Video
        fields = fields = [
            'id', 'title', 'description', 
            'serie_id', 'serie_name',
            'season_number', 'episode_number',
            'video_file', 'thumbnail',
            'video_path', 'thumbnail_path', 
            'category_id', 'category_name',
            'user_id' ,'username',
            'created_at'
        ]
        extra_kwargs = {'user': {'read_only': True}}
        
    def get_video_path(self, obj):
        # Retorna el string exacto guardado en la DB: 'videos/nombre.mp4'
        return obj.video_file.name if obj.video_file else None

    def get_thumbnail_path(self, obj):
        return obj.thumbnail.name if obj.thumbnail else None