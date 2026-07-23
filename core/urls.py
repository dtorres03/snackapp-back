"""
Módulo de Enrutamiento Central - SnakApp API.

Este archivo centraliza la definición de rutas para el backend de SnakApp. 
Utiliza una arquitectura híbrida que combina rutas manuales para servicios 
de infraestructura (Admin, Auth, Docs) y un `DefaultRouter` para la exposición 
automática de los ViewSets de la lógica de negocio.

Arquitectura de Rutas:
    1. Servicios de Infraestructura: Admin, Auth (JWT).
    2. Documentación OpenAPI 3.0: Swagger, Redoc y Esquema técnico.
    3. Endpoints de Negocio: Gestión de usuarios, contenido y social.

Seguridad:
    - Validación de tokens Bearer JWT.
    - Filtrado de integridad basado en UUIDs.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from core.media_serve import ranged_file_response
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, LoginView
from videos.views import VideoViewSet, CategoryViewSet, SeriesViewSet
from interactions.views import FavoriteViewSet, CommentViewSet, VideoInteractionViewSet
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


"""
Instanciación del DefaultRouter de Django REST Framework.
El router se encarga de generar automáticamente las URLs para las operaciones 
estándar CRUD (List, Create, Retrieve, Update, Delete) y acciones personalizadas 
(@action) definidas en los ViewSets.
"""

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
    path('api/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/', include(router.urls)),
    
    # Genera el archivo del esquema (YAML/JSON)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Interfaz de Swagger (La más popular para probar endpoints)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Interfaz de Redoc (Una alternativa más limpia y enfocada a lectura)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

]

if settings.DEBUG:
    """
    Servicio de archivos estáticos y media en entorno de desarrollo.
    Se utiliza 'ranged_file_response' en lugar del servidor estático estándar 
    de Django para soportar peticiones por rangos de bytes (HTTP Range Requests).
    Esto es crítico para la reproducción de video fluida y compatibilidad con 
    el reproductor nativo de iOS.
    """
    media_url = settings.MEDIA_URL.lstrip('/')
    urlpatterns += [
        re_path(rf'^{media_url}(?P<path>.*)$', ranged_file_response, {'document_root': settings.MEDIA_ROOT}),
    ]