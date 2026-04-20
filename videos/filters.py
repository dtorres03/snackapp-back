from django_filters import rest_framework as filters
from .models import Video

class VideoFilter(filters.FilterSet):
    # 'allow_empty=True' o simplemente dejar que NumberFilter maneje el null
    category = filters.NumberFilter(field_name="category_id", lookup_expr='exact')
    serie = filters.NumberFilter(field_name="serie_id", lookup_expr='exact')
    
    class Meta:
        model = Video
        fields = ['category', 'serie', 'season_number']