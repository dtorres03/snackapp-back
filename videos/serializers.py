from rest_framework import serializers
from .models import Video, Category

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
    username = serializers.ReadOnlyField(source='user.username')
    category_name = serializers.ReadOnlyField(source='category.name')

    class Meta:
        model = Video
        fields = [
            'id', 'title', 'description', 'video_url', 'thumbnail',
            'user', 'username', 'category', 'category_name', 'created_at'
        ]
        
        # 🔹 Aquí aplicamos los extra_kwargs
        extra_kwargs = {
            'user': {'read_only': True},  # muestra quien es el dueño del video, pero impide que alguien lo cambie atraves de API
            'video_url': {
                'help_text': 'Ingresa un enlace válido',
                'error_messages': {
                    'invalid': 'La URL ingresada no es válida. Por favor verifica el formato.'
                }
            },
            'title': {
                'error_messages': {
                    'blank': 'El título es obligatorio para poder subir el video.'
                }
            },
            'category': {
            'required': True,          
            'allow_null': False,
        },
        }