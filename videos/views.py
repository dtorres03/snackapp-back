from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Video, Category, Serie
from .serializers import VideoSerializer, CategorySerializer, SeriesSerializer
from .pagination import StandardResultsSetPagination
from .filters import VideoFilter
from django.db.models import Q

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination # Sobrescribe la global solo para este endpoint
    # Para que cualquiera pueda ver las categorías al navegar
    permission_classes = [permissions.AllowAny]

class VideoViewSet(viewsets.ModelViewSet):
    serializer_class = VideoSerializer
    
    # Configuramos los backends de filtro específicamente para esta vista
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    
    # Campos por los que se puede buscar con texto (Buscador)
    search_fields = ['^title', 'description', 'category_name', 'serie_name']
    
    def get_queryset(self):
        queryset = Video.objects.all()
        category_name = self.request.query_params.get('category')
        search_query = self.request.query_params.get('search')
        season = self.request.query_params.get('season')
        
        if category_name:
            # Esto obliga a Django a filtrar, sí o sí
            queryset = queryset.filter(category__name__iexact=category_name)
            
        if season:
            queryset = queryset.filter(season_number=season)
        
        if search_query:
            # Buscamos en título del video O nombre de la serie
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(serie__title__icontains=search_query)
            )
            
        return queryset

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()] # Cualquiera puede ver videos 
        return [permissions.IsAuthenticated()] # Solo logueados suben/editan/borran

    def list(self, request):
        queryset = self.get_queryset()

        # Rechazar ?page= (string vacío) antes de llegar al paginador
        page_param = request.query_params.get('page')
        if page_param is not None and page_param.strip() == '':
            raise NotFound(detail="Invalid page.")

        # Filtrar por serie si se pasa el param ?serie=<id>
        serie_id = request.query_params.get('serie')
        if serie_id is not None:
            queryset = queryset.filter(serie__id=serie_id)

        # Paginar el queryset (5 videos por página)
        paginator = StandardResultsSetPagination()
        try:
            page = paginator.paginate_queryset(queryset, request)
        except NotFound:
            # DRF convierte InvalidPage en NotFound internamente.
            # Si el param ?page es un entero fuera de rango → array vacío
            # Si no es un entero (letras, símbolos) → re-lanzar el error
            try:
                int(page_param)
                return Response([])
            except (ValueError, TypeError):
                raise NotFound(detail="Invalid page.")

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

        # Rechazar ?page= (string vacío) antes de llegar al paginador
        page_param = request.query_params.get('page')
        if page_param is not None and page_param.strip() == '':
            raise NotFound(detail="Invalid page.")

        # Paginar el queryset (5 series por página)
        paginator = self.pagination_class()
        try:
            page = paginator.paginate_queryset(queryset, request)
        except NotFound:
            # DRF convierte InvalidPage en NotFound internamente.
            # Si el param ?page es un entero fuera de rango → array vacío
            # Si no es un entero (letras, símbolos) → re-lanzar el error
            try:
                int(page_param)
                # Es un entero válido pero fuera de rango: devolver array vacío
                return Response([])
            except (ValueError, TypeError):
                # No es un entero (letras, símbolos): error estándar
                raise NotFound(detail="Invalid page.")

        # Devolver directamente el array, sin el envelope count/next/previous/results
        items = page if page is not None else queryset
        serializer = SeriesSerializer(items, many=True)
        return Response(serializer.data)