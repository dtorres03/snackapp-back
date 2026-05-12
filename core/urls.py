"""
Módulo de Enrutamiento Central - SnackApp API.

Este archivo centraliza la definición de rutas para el backend de SnackApp. 
Utiliza una arquitectura híbrida que combina rutas manuales para servicios 
de infraestructura (Admin, Auth, Docs) y un `DefaultRouter` para la exposición 
automática de los ViewSets de la lógica de negocio.

Arquitectura de Rutas:
    1. Servicios de Infraestructura:
        - /admin/ : Punto de entrada al panel de administración de Django.
        - /api/login/ : Endpoint de autenticación (SimpleJWT).
        - /api/token/refresh/ : Renovación de tokens de acceso expirados.
        
    2. Documentación OpenAPI 3.0:
        - /api/schema/ : Generación dinámica del esquema técnico (YAML/JSON).
        - /api/docs/ : Interfaz interactiva de Swagger UI para pruebas.
        - /api/redoc/ : Documentación técnica estática vía Redoc.

    3. Endpoints de Negocio (Auto-generados vía Router):
        - /api/users/ : Gestión de perfiles de usuario.
        - /api/videos/ : Catálogo de contenido multimedia.
        - /api/categories/ : Clasificación de contenido.
        - /api/series/ : Agrupación de episodios y temporadas.
        - /api/favorites/ : Gestión de preferencias del usuario.

Configuración de Archivos Estáticos:
    En modo DEBUG, el servidor expone la ruta `media/` para el servicio directo 
    de archivos de video y miniaturas almacenados localmente.

Seguridad:
    Implementa validación de tokens Bearer JWT y filtrado de integridad 
    basado en UUIDs como claves primarias en todos los recursos.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet
from videos.views import VideoViewSet, CategoryViewSet, SeriesViewSet
from interactions.views import FavoriteViewSet, CommentViewSet, VideoInteractionViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# El router crea las URLs del CRUD automáticamente
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'videos', VideoViewSet, basename='video')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'series', SeriesViewSet, basename='serie')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'video-interactions', VideoInteractionViewSet, basename='video-interaction')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    
    # Genera el archivo del esquema (YAML/JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Interfaz de Swagger (La más popular para probar endpoints)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Interfaz de Redoc (Una alternativa más limpia y enfocada a lectura)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

from django.urls import re_path
from core.media_serve import ranged_file_response

# Esto permite que media/videos/video.mp4 sea accesible vía HTTP con soporte para iOS
if settings.DEBUG:
    # Removemos el slash inicial de MEDIA_URL si existe para la regex
    media_url = settings.MEDIA_URL.lstrip('/')
    urlpatterns += [
        re_path(rf'^{media_url}(?P<path>.*)$', ranged_file_response, {'document_root': settings.MEDIA_ROOT}),
    ]