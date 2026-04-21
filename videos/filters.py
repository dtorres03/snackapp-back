"""
Motores de Filtrado - SnackApp.

Este módulo define la lógica de búsqueda y segmentación para el catálogo 
de videos. Permite a los clientes filtrar contenido de forma precisa 
mediante parámetros en la URL (Query Parameters).
"""

from django_filters import rest_framework as filters
from .models import Video

class VideoFilter(filters.FilterSet):
    """
    Conjunto de filtros personalizados para el modelo Video.

    Permite segmentar el catálogo de videos basándose en su clasificación 
    jerárquica. Es compatible con la generación automática de esquemas 
    de OpenAPI (Swagger).

    Parámetros de Filtro:
        category (uuid): Filtra videos pertenecientes a una categoría específica.
        serie (uuid): Filtra videos que forman parte de una serie (episodios).
        season_number (int): Filtra por el número de temporada.

    Uso en API:
        GET /api/videos/?category=<uuid>&season_number=1
    """
     
    # 'lookup_expr=exact' asegura que la coincidencia sea idéntica.
    category = filters.UUIDFilter(field_name="category_id", lookup_expr='exact')
    serie = filters.UUIDFilter(field_name="serie_id", lookup_expr='exact')
    
    class Meta:
        model = Video
        fields = ['category', 'serie', 'season_number']