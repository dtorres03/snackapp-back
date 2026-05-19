"""
Configuración central para el proyecto SnackApp.

Este módulo contiene la configuración de Django para el backend de la plataforma
de streaming, incluyendo la integración con PostgreSQL, autenticación JWT
y documentación automatizada con Swagger/OpenAPI.

Variables de Entorno Requeridas:
    DB_NAME (str): Nombre de la base de datos PostgreSQL.
    DB_USER (str): Usuario de la base de datos.
    DB_PASSWORD (str): Contraseña del usuario.
    SECRET_KEY (str): Llave secreta de Django para operaciones criptográficas.
    DEBUG (bool): Modo de depuración (True/False).

Apps Principales:
    - users: Gestión de usuarios personalizados (UUID).
    - videos: Catálogo de contenido y streaming.
    - interactions: Favoritos y feedback de usuarios.
    
Arquitectura de Autenticación:
    - Sistema: JSON Web Token (JWT) vía `django-rest-framework-simplejwt`.
    - Endpoints: 
        * /api/login/: Intercambio de credenciales por tokens de acceso/refresco.
        * /api/token/refresh/: Renovación de sesiones activas.
    - Persistencia: Los tokens deben ser manejados por el cliente (Frontend/Mobile).
    - Seguridad: IDs de usuario expuestos en el payload del token utilizan formato UUID.

Para más información sobre este archivo, consulta:
https://docs.djangoproject.com/en/6.0/topics/settings/
https://docs.djangoproject.com/en/6.0/ref/settings/
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Esta es la ruta absoluta en tu disco duro (donde se guardan los archivos)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Esta es la URL pública para acceder a ellos desde el navegador/Postman
MEDIA_URL = 'https://snakapp.co/media/'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
USE_X_FORWARDED_PORT = True

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['93.188.164.97', 'localhost', '127.0.0.1', 'snakapp.co']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_spectacular',
    'drf_spectacular_sidecar',
    'users',
    'videos',
    'interactions',
    'corsheaders'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "https://snakapp.co",
    "https://www.snakapp.co",
    "http://localhost:3000",  
    "http://localhost:8081",  
]

# Muy importante para que el Login funcione (si usan cookies o tokens)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    "https://snakapp.co",
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Carga las variables del archivo .env
load_dotenv()

# Sustituye tus configuraciones estáticas
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = os.getenv('DEBUG') == 'True'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Bogota'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = '/static/'

# La carpeta física donde Django reunirá todos los archivos del proyecto
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# 1. Agregar DRF y SimpleJWT a los frames
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', # Nadie entra si no tiene Token
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 5,  # Aquí defines el límite de 5 videos por página
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter', # Esto también activará el buscador
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# 2. Configurar el tiempo de vida del Token
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

AUTH_USER_MODEL = 'users.CustomUser'

AUTHENTICATION_BACKENDS = [
    'users.authentication.EmailOrUsernameModelBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Configuración básica de la documentación
SPECTACULAR_SETTINGS = {
    'TITLE': 'SnackApp API',
    'DESCRIPTION': 'Documentación de los endpoints utilizados para SnackApp.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # Esto asegura que se documente el esquema de autenticación JWT
    'COMPONENT_SPLIT_PATCH': True,
    'COMPONENT_SPLIT_COMMAND': True,
    'SERVE_AUTHENTICATION_KEEP_ALIVE': True,
    'APPEND_COMPONENTS': {
        "securitySchemes": {
            "Bearer": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT",
            }
        }
    },
    'SECURITY': [
        {'Bearer': []},
    ],
}
