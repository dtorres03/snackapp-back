from django.contrib import admin
from .models import Category, Video, Serie

# Esta clase permite ver y agregar episodios directamente dentro de una Serie
class VideoInline(admin.TabularInline):
    model = Video
    extra = 1 # Muestra un espacio vacío para agregar un nuevo episodio
    fields = ('title', 'season_number', 'episode_number', 'video_file')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Serie)
class SerieAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('title', 'description')
    # Aquí conectamos los videos con la serie en la misma vista
    inlines = [VideoInline]

@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    # Columnas que verás en la tabla de videos
    list_display = ('id', 'title', 'serie', 'season_number', 'episode_number', 'user', 'created_at')
    # Filtros laterales para encontrar videos rápido
    list_filter = ('serie', 'category', 'user')
    # Buscador por título y descripción
    search_fields = ('title', 'description')