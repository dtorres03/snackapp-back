"""
Vistas para la aplicación de Interacciones.

Este módulo define la lógica de control para los favoritos, asegurando que 
cada usuario solo pueda interactuar con su propio catálogo personal de videos 
guardados.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from .models import Favorite, Comment, VideoLike
from .serializers import FavoriteSerializer, CommentSerializer

class FavoriteViewSet(viewsets.ModelViewSet):
    """
    Punto de entrada (ViewSet) para gestionar los favoritos del usuario.

    Proporciona operaciones CRUD completas con las siguientes restricciones:
        - Acceso: Solo usuarios autenticados (JWT).
        - Visibilidad: Un usuario solo puede ver y editar sus propios favoritos.
        - Integridad: El usuario se vincula automáticamente mediante el token.

    Acciones permitidas:
        - GET /api/favorites/ : Lista los favoritos del usuario autenticado.
        - POST /api/favorites/ : Crea un nuevo favorito (requiere ID del video).
        - DELETE /api/favorites/{id}/ : Elimina un favorito específico.
    """
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """
        Sobrescribimos el método 'create' para que funcione como un Toggle.
        """
        video_id = request.data.get('video')
        
        if not video_id:
            return Response(
                {"detail": "El campo 'video' es requerido."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscamos si el favorito ya existe para el usuario actual
        favorito_existente = Favorite.objects.filter(
            user=request.user, 
            video_id=video_id
        ).first()

        if favorito_existente:
            # Si ya existe, lo eliminamos (Toggle OFF)
            favorito_existente.delete()
            return Response(
                {"message": "Eliminado de favoritos", "is_favorite": False},
                status=status.HTTP_200_OK
            )
        
        # Si no existe, procedemos a crearlo (Toggle ON)
        # Reutilizamos la lógica estándar de DRF
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return Response(
            {"message": "Agregado a favoritos", "is_favorite": True, "data": serializer.data},
            status=status.HTTP_201_CREATED
        )

    def get_queryset(self):
        """
        Personaliza el conjunto de datos para garantizar la privacidad.
        
        Filtra los registros de la base de datos para que el usuario 
        autenticado no pueda acceder a los favoritos de otros usuarios, 
        incluso si conoce el UUID del registro.
        """
        return Favorite.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        Retorna la lista de favoritos paginada pero estructurada como un 
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
                int(page_param)
                return Response([])
            except (ValueError, TypeError):
                raise NotFound(detail="Invalid page.")

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return Response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """
        Vincula automáticamente al usuario actual con el nuevo favorito.
        
        Al guardar, extrae el objeto User de la petición (request.user)
        y lo inyecta en el campo 'user' del modelo, ignorando cualquier 
        intento de suplantación desde el cuerpo del JSON.
        """
        serializer.save(user=self.request.user)
        
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Así el comentario queda ligado automáticamente al usuario logueado
        serializer.save(user=self.request.user)

    def get_queryset(self):
        # Permite filtrar comentarios por video: /api/interactions/comments/?video_id=#uuid
        video_id = self.request.query_params.get('video_id')
        if video_id:
            return self.queryset.filter(video_id=video_id)
        return self.queryset
    
    # Endpoint para dar/quitar like: POST /api/comments/{id}/like/
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        comment = self.get_object()
        user = request.user

        if user in comment.likes.all():
            comment.likes.remove(user)
            return Response({'status': 'unliked', 'likes_count': comment.total_likes}, status=status.HTTP_200_OK)
        else:
            comment.likes.add(user)
            return Response({'status': 'liked', 'likes_count': comment.total_likes}, status=status.HTTP_200_OK)
               
class VideoInteractionViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='toggle-like')
    def toggle_like(self, request):
        video_id = request.data.get('video_id')
        user = request.user
        
        try:
            like = VideoLike.objects.get(user=user, video_id=video_id)
            like.delete()
            return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
        except VideoLike.DoesNotExist:
            VideoLike.objects.create(user=user, video_id=video_id)
            return Response({'status': 'liked'}, status=status.HTTP_201_CREATED)