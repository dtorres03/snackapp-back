from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Video, Category, Serie
from .serializers import VideoSerializer, CategorySerializer, SeriesSerializer
from .pagination import StandardResultsSetPagination

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination # Sobrescribe la global solo para este endpoint
    # Para que cualquiera pueda ver las categorías al navegar
    permission_classes = [permissions.AllowAny]

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()] # Cualquiera puede ver videos 
        return [permissions.IsAuthenticated()] # Solo logueados suben/editan/borran

    def list(self, request):
        queryset = self.get_queryset()

        # Filtrar por serie si se pasa el param ?serie=<id>
        serie_id = request.query_params.get('serie')
        if serie_id is not None:
            queryset = queryset.filter(serie__id=serie_id)

        # Paginar el queryset (5 videos por página)
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)

        # Devolver directamente el array, sin el envelope count/next/previous/results
        items = page if page is not None else queryset
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Guarda el video y se lo asigna al asuario que hace la petición
        #print("Datos de texto:", self.request.data)
        #print("Archivos recibidos:", self.request.FILES)
        serializer.save(user=self.request.user)


class SeriesViewSet(viewsets.ViewSet):
    """Endpoint de Series con paginación (5 series/página).
    Cada serie incluye id, title, category y los primeros 5 videos.
    """
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        queryset = Serie.objects.all().order_by('id')

        # Paginar el queryset (5 series por página)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(queryset, request)

        # Devolver directamente el array, sin el envelope count/next/previous/results
        items = page if page is not None else queryset
        serializer = SeriesSerializer(items, many=True)
        return Response(serializer.data)