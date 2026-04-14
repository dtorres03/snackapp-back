from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Video, Category
from .serializers import VideoSerializer, CategorySerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # Para que cualquiera pueda ver las categorías al navegar
    permission_classes = [permissions.AllowAny]

class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()] # Cualquiera puede ver videos 
        return [permissions.IsAuthenticated()] # Solo logueados suben/editan/borran

    def perform_create(self, serializer):
        # Guarda el video y se lo asigna al asuario que hace la petición
        serializer.save(user=self.request.user)