from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny, IsAuthenticated
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
        """
        Asignación dinámica de permisos según la acción:
        - create: Cualquiera puede registrarse.
        - list: Solo usuarios autenticados.
        - retrieve, update, partial_update, destroy: Dueño o solo lectura.
        """
        if self.action == 'create':
            return [permissions.AllowAny()]
        
        # Para el resto de acciones, aplicamos Autenticación + Propiedad
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
    
    def perform_update(self, serializer):
        try:
            serializer.save()
        except Exception as e:
            # Útil para debuggear en tu terminal de Arch Linux
            print(f"--- ERROR EN UPDATE: {e} ---")
            raise e
