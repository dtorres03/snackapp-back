"""
Vistas de Catálogo y Multimedia - SnackApp.

Este módulo gestiona la exposición de categorías, series y videos. Implementa 
lógicas de búsqueda compleja, filtrado por temporadas y un sistema de 
paginación simplificado que entrega colecciones directas al cliente.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Video, Category, Serie
from .serializers import VideoSerializer, CategorySerializer, SeriesSerializer
from .pagination import StandardResultsSetPagination
from django.db.models import Q

class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la gestión de categorías de contenido.

    Permite a los administradores gestionar las etiquetas temáticas, mientras 
    que el acceso de lectura es público para permitir la navegación del catálogo.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        """
        Retorna la lista de categorías paginada pero estructurada como un 
        arreglo simple para facilitar su manejo en el frontend.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page_param = request.query_params.get('page')
        
        if page_param is not None and page_param.strip() == '':
            raise NotFound(detail="Invalid page.")
        
        try:
            page = self.paginate_queryset(queryset)
        except NotFound:
            try:
                if page_param is not None:
                    int(page_param)
                return Response([])
            except (ValueError, TypeError):
                raise NotFound(detail="Invalid page.")

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class VideoViewSet(viewsets.ModelViewSet):
    """
    Controlador principal para el catálogo de videos y episodios.

    Implementa búsqueda avanzada y filtrado dinámico. A diferencia de las vistas 
    estándar, el método `list` ha sido sobrescrito para retornar una lista 
    plana de objetos, optimizando el consumo para componentes de scroll infinito.

    Búsqueda y Filtrado:
        - search: Busca coincidencias en títulos, descripciones y nombres de series.
        - category: Filtro exacto por nombre de categoría (case-insensitive).
        - season: Filtro por número de temporada.
        - serie: Filtro por ID de serie para obtener episodios específicos.
    """
    serializer_class = VideoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['^title', 'description', 'category_name', 'serie_name']
    
    def get_queryset(self):
        """
        Construye el queryset aplicando filtros complejos mediante Q objects.
        
        Asegura que las búsquedas de texto abarquen tanto el contenido del 
        video como los metadatos de la serie vinculada.
        """
        queryset = Video.objects.all()
        category_name = self.request.query_params.get('category')
        search_query = self.request.query_params.get('search')
        season = self.request.query_params.get('season')
        
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
        if season:
            queryset = queryset.filter(season_number=season)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(serie__title__icontains=search_query)
            )
        return queryset

    def get_permissions(self):
        """
        Define políticas de acceso granulares.
        - Lectura: Público (AllowAny).
        - Escritura: Solo usuarios autenticados.
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def list(self, request):
        """
        Retorna la lista de videos paginada en formato de array simple.
        
        Gestiona excepciones de paginación para retornar listas vacías en 
        lugar de errores 404 cuando el índice de página excede el contenido, 
        mejorando la resiliencia del frontend.
        """
        queryset = self.get_queryset()
        page_param = request.query_params.get('page')
        
        if page_param is not None and page_param.strip() == '':
            raise NotFound(detail="Invalid page.")

        serie_id = request.query_params.get('serie')
        if serie_id is not None:
            queryset = queryset.filter(serie__id=serie_id)

        paginator = StandardResultsSetPagination()
        try:
            page = paginator.paginate_queryset(queryset, request)
        except NotFound:
            try:
                int(page_param)
                return Response([])
            except (ValueError, TypeError):
                raise NotFound(detail="Invalid page.")

        items = page if page is not None else queryset
        serializer = self.get_serializer(items, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Asigna la autoría del video al usuario autenticado durante el guardado."""
        serializer.save(user=self.request.user)


class SeriesViewSet(viewsets.ViewSet):
    """
    Endpoint especializado para la navegación por Series.

    Proporciona una vista de alto nivel que incluye metadatos de la serie 
    y una previsualización de sus episodios iniciales. Utiliza el mismo 
    sistema de respuesta simplificada (array plano) que VideoViewSet.
    """
    permission_classes = [permissions.AllowAny]
    pagination_class = StandardResultsSetPagination

    def list(self, request):
        """Lista todas las series con soporte para paginación manual."""
        queryset = Serie.objects.all().order_by('id')
        page_param = request.query_params.get('page')

        if page_param is not None and page_param.strip() == '':
            raise NotFound(detail="Invalid page.")

        paginator = self.pagination_class()
        try:
            page = paginator.paginate_queryset(queryset, request)
        except NotFound:
            try:
                int(page_param)
                return Response([])
            except (ValueError, TypeError):
                raise NotFound(detail="Invalid page.")

        items = page if page is not None else queryset
        serializer = SeriesSerializer(items, many=True)
        return Response(serializer.data)