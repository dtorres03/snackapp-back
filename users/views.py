"""
Vistas de Gestión de Usuarios - SnackApp.

Este módulo implementa la lógica de control para el ciclo de vida de los usuarios,
incluyendo registro público, edición de perfiles con restricciones de propiedad
y un sistema de eliminación jerárquico y seguro.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework.decorators import action
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import EmailOrUsernameTokenObtainPairSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso personalizado para restringir la edición de perfiles.

    Reglas:
        - Lectura (GET, HEAD, OPTIONS): Permitido para cualquier usuario autenticado.
        - Escritura (PUT, PATCH, DELETE): Solo permitido para el dueño del perfil
          o usuarios con rango de Staff/Superusuario.
    """
    def has_object_permission(self, request, view, obj):
        # 1. Las lecturas siempre se permiten (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 2. Si es superusuario o staff, tiene permiso total
        if request.user.is_superuser or request.user.is_staff:
            return True

        # 3. Si no es admin, solo puede editar/borrar si es el dueño
        return obj == request.user

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD sobre el modelo CustomUser.

    Proporciona endpoints para el registro de nuevos usuarios, consulta de perfiles
    y actualización de datos, con una estructura de respuesta estandarizada
    para facilitar la integración con el frontend.

    Políticas de Acceso:
        - Crear: Abierto al público (AllowAny).
        - Eliminar: Solo usuarios autenticados con validación de jerarquía.
        - Otros: Requiere autenticación y validación de propiedad (IsOwnerOrReadOnly).
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """Asigna dinámicamente permisos según la acción solicitada."""
        if self.action == 'create':
            return [permissions.AllowAny()]
        
        if self.action == 'destroy':
            return [permissions.IsAuthenticated()]
        
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def create(self, request, *args, **kwargs):
        """
        Registra un nuevo usuario en la plataforma.
        
        Retorna una respuesta estructurada con los datos del nuevo usuario
        o un desglose de errores de validación.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response({
                "status": "success",
                "message": "Usuario registrado con éxito",
                "code":status.HTTP_201_CREATED,
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            "status": "error",
            "message": "Error en el registro",
            "code":status.HTTP_400_BAD_REQUEST,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        """
        Actualiza la información del perfil de un usuario.
        
        Soporta actualizaciones totales (PUT) y parciales (PATCH).
        Solo el dueño o administradores pueden ejecutar esta acción.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "status": "success",
                "message": "Perfil actualizado correctamente",
                "code":status.HTTP_200_OK,
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "No se pudo actualizar el perfil",
            "code":status.HTTP_400_BAD_REQUEST,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Elimina un usuario del sistema bajo reglas de jerarquía.
        
        Reglas de eliminación:
            1. Un usuario no-superusuario no puede borrar a un staff.
            2. Un usuario común solo puede borrarse a sí mismo.
            3. Superusuarios tienen control total.
        """
        instance = self.get_object()
        
        # 1. Protegemos a los Admins primero
        # Si el objetivo es un admin y quien pide borrar NO es superusuario
        if instance.is_staff and not request.user.is_superuser:
            return Response({
                "status": "error",
                "message": "No tienes permisos para eliminar a un administrador.",
                "code": status.HTTP_403_FORBIDDEN
            }, status=status.HTTP_403_FORBIDDEN)

        # 2. REGLA DE PROPIEDAD: ¿Es el dueño o un staff autorizado?
        is_owner = instance == request.user
        is_staff_user = request.user.is_staff or request.user.is_superuser

        if not is_owner and not is_staff_user:
            return Response({
                "status": "error",
                "message": "No tienes permiso para borrar este perfil.",
                "code": status.HTTP_403_FORBIDDEN
            }, status=status.HTTP_403_FORBIDDEN)

        # 3. Si pasó ambos filtros, procedemos
        self.perform_destroy(instance)
        return Response({
            "status": "success",
            "message": "Usuario eliminado correctamente",
            "code": status.HTTP_200_OK
        }, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        """Persiste los cambios del perfil en la base de datos."""
        try:
            serializer.save()
        except Exception as e:
            # Log de error para depuración en entorno de desarrollo
            print(f"--- ERROR CRÍTICO: {e} ---")
            raise
        
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Retorna la información del usuario autenticado.
        URL: GET /api/users/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
class LoginView(TokenObtainPairView):
    # Le decimos a la vista de Simple JWT que use nuestra lógica flexible
    serializer_class = EmailOrUsernameTokenObtainPairSerializer