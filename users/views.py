from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # 1. Las lecturas siempre se permiten (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 2. El "Pase VIP": Si es superusuario o staff, tiene permiso total
        if request.user.is_superuser or request.user.is_staff:
            return True

        # 3. Si no es admin, solo puede editar/borrar si es el dueño
        return obj == request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        
        if self.action == 'destroy':
            return [permissions.IsAuthenticated()]
        
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    # --- MEJORA EN CREACIÓN (POST /api/users/) ---
    def create(self, request, *args, **kwargs):
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

    # --- MEJORA EN ACTUALIZACIÓN (PUT/PATCH /api/users/{id}/) ---
    def update(self, request, *args, **kwargs):
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

    # --- MEJORA EN ELIMINACIÓN (DELETE /api/users/{id}/) ---
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # 1. REGLA DE ORO: Protegemos a los Admins primero
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
        # Mantenemos tu try/except para debuggear en Arch
        try:
            serializer.save()
        except Exception as e:
            print(f"--- ERROR CRÍTICO: {e} ---")
            raise