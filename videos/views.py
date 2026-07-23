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
from django.db import transaction
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from django.conf import settings
from django.http import HttpResponse, FileResponse, Http404
import os

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
    
    @action(detail=True, methods=['post'], url_path='unlock', permission_classes=[permissions.IsAuthenticated])
    def unlock(self, request, pk=None):
        """
        Gestiona el canje de tokens por acceso al contenido.
        
        Aplica una transacción atómica para garantizar que el descuento de tokens
        y la concesión de acceso ocurran como una única operación indivisible,
        previniendo errores de saldo negativo por clicks duplicados en la App.
        """
        video = self.get_object()
        user = request.user
        
        if video.user == user:
            return Response(
            {"detail": "Eres el autor de este video, ya tienes acceso total sin costo."},
            status=status.HTTP_200_OK
        )

        if video.users_with_access.filter(id=user.id).exists():
            return Response(
                {"detail": "Ya has desbloqueado este video anteriormente."},
                status=status.HTTP_200_OK
            )

        try:
            with transaction.atomic():
                user_record = get_user_model().objects.select_for_update().get(id=user.id)

                if user_record.tokens < video.cost:
                    return Response(
                        {"detail": "Saldo de tokens insuficiente.", "required": video.cost, "current": user_record.tokens},
                        status=status.HTTP_402_PAYMENT_REQUIRED
                    )

                user_record.tokens -= video.cost
                user_record.save()
                video.users_with_access.add(user_record)

                return Response({
                    "detail": f"Video '{video.title}' desbloqueado correctamente.",
                    "remaining_tokens": user_record.tokens
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"detail": "Ocurrió un error inesperado al procesar el canje."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='my-purchases')
    def purchased_videos(self, request):
        """
        Retorna la lista de videos que el usuario actual ha comprado.
        URL: GET /api/videos/my-purchases/
        """
        # Filtramos los videos donde el usuario está en la lista de acceso
        # pero EXCLUIMOS los videos que él mismo subió (para ver solo compras)
        queryset = Video.objects.filter(
            users_with_access=request.user
        ).exclude(user=request.user)
        
        # Reutilizamos tu lógica de paginación simplificada
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='play', permission_classes=[permissions.IsAuthenticated])
    def stream(self, request, pk=None):
        """
        Endpoint seguro para la reproducción de video.
        
        URL: GET /api/videos/<pk>/play/
        
        Valida la autenticación mediante JWT y confirma que el usuario sea el autor 
        o que tenga el video desbloqueado en 'users_with_access'.
        
        En entorno de desarrollo (DEBUG=True), entrega el binario vía FileResponse.
        En entorno de producción (DEBUG=False), delega la entrega a Nginx usando X-Accel-Redirect.
        """
        video = self.get_object()
        user = request.user
        has_access = (
            video.user == user or 
            video.cost == 0 or 
            video.users_with_access.filter(id=user.id).exists()
        )

        if not has_access:
            return Response(
                {"detail": "No tienes acceso a este video. Debes desbloquearlo primero."},
                status=status.HTTP_403_FORBIDDEN
            )

        file_name = os.path.basename(video.video_file.name) if hasattr(video, 'video_file') and video.video_file else str(video.file_name)
        
        file_path = os.path.join(settings.PROTECTED_MEDIA_ROOT, 'videos', file_name)

        if not os.path.exists(file_path):
            raise Http404("El archivo de video no se encuentra registrado en el almacenamiento.")

        if settings.DEBUG:
            # En local puedes retornar la ruta relativa o absoluta local
            relative_path = f"/media/protected_media/videos/{file_name}"
        else:
            # En producción retornas la ruta protegida que Nginx o tu reproductor usará
            relative_path = f"/protected_media/videos/{file_name}"

        return Response(
            {
                "id": str(video.id),
                "title": video.title,
                "video_path": relative_path
            },
            status=status.HTTP_200_OK
        )

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
        serializer = SeriesSerializer(items, many=True, context={'request': request})
        return Response(serializer.data)