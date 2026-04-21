"""
Vistas para la aplicación de Interacciones.

Este módulo define la lógica de control para los favoritos, asegurando que 
cada usuario solo pueda interactuar con su propio catálogo personal de videos 
guardados.
"""

from rest_framework import viewsets, permissions
from .models import Favorite
from .serializers import FavoriteSerializer

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

    def get_queryset(self):
        """
        Personaliza el conjunto de datos para garantizar la privacidad.
        
        Filtra los registros de la base de datos para que el usuario 
        autenticado no pueda acceder a los favoritos de otros usuarios, 
        incluso si conoce el UUID del registro.
        """
        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Vincula automáticamente al usuario actual con el nuevo favorito.
        
        Al guardar, extrae el objeto User de la petición (request.user)
        y lo inyecta en el campo 'user' del modelo, ignorando cualquier 
        intento de suplantación desde el cuerpo del JSON.
        """
        serializer.save(user=self.request.user)