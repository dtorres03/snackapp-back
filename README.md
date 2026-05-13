# 🚀 SnakApp Backend - API REST

Este es el núcleo de servicios para la plataforma de streaming y gestión de contenido. Construido con las últimas versiones de Python y Django, implementa un sistema de autenticación robusta mediante **JWT** y un CRUD completo de usuarios con permisos granulares de propiedad.

## 🛠️ Tecnologías utilizadas

* **Lenguaje:** Python 3.14
* **Framework:** **Django 6.0.3**
* **API:** Django REST Framework (DRF)
* **Autenticación:** SimpleJWT (JSON Web Tokens)
* **Base de Datos:** **PostgreSQL** (Producción/Desarrollo)
* **Identificadores:** **UUID4** (Universally Unique Identifiers)
* **Entorno:** Virtualenv + Variables de entorno (.env)

## 🔐 Seguridad y Permisos

* **Permisos de Propiedad:** Implementa `IsOwnerOrReadOnly` para proteger perfiles de usuario.
* **UUIDs:** Todos los modelos (`User`, `Video`, `Category`, `Serie`, `Favorite`) utilizan UUIDs en lugar de IDs incrementales para mejorar la seguridad y evitar la enumeración de recursos en la API.
* **Variables de Entorno:** Gestión segura de credenciales de base de datos y llaves secretas.

---

## ⚙️ Instalación para Desarrolladores

Si vas a clonar este proyecto por primera vez, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/dtorres03/snackapp-back.git
   cd snackapp-back

2. **Configura variables de entorno:**
   #### Crea un archivo .env en la raíz del proyecto basándote en el siguiente esquema:
   ```bash
   DB_NAME=<DB_NAME>
   DB_USER=<DB_USER>
   DB_PASSWORD=<DB_PASSWORD>
   DB_HOST=<DB_HOST>
   DB_PORT=<DB_PORT>
   SECRET_KEY=<DJANGO_SECRET_KEY>
3. **Crear y activar el entorno virtual:**
   ```bash
   python -m venv venv
   # En Linux/macOS:
   source venv/bin/activate
   # En Windows:
   .\venv\Scripts\activate
4. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
5. **Configurar la Base de Datos:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
6. **Iniciar el servidor:**
   ```bash
   python manage.py runserver

## 📡 Endpoints Principales (API)

| Recurso | Endpoint | Descripción |
| :--- | :--- | :--- |
| **Usuarios** | `/api/users/` | Perfiles y cuentas de usuario. |
| **Videos** | `/api/videos/` | Catálogo de contenido multimedia. |
| **Categorías** | `/api/categories/` | Filtros por género y etiquetas. |
| **Series** | `/api/series/` | Agrupación de episodios y temporadas. |
| **Favoritos** | `/api/favorites/` | Marcadores de contenido personal. |
| **Comentarios** | `/api/comments/` | Comentarios y respuestas anidadas. |
| **Interacciones** | `/api/video-interactions/` | Lógica de likes y reacciones. |

> ⚠️ **IMPORTANTE:** Todas las URLs deben terminar en `/` (trailing slash). 
> De lo contrario, Django podría devolver un error 404 o 500 al realizar peticiones `PATCH` o `POST`.
>
> **Ejemplo correcto:** `https://snakapp.co/api/users/550e8400-e29b-4114-a432-444666540102/`

## 🧪 Pruebas en Postman

### 🔑 Autenticación (JWT)
- **Login**: `POST /api/login/` -> `{ "username": "tu_usuario", "password": "tu_password" }`
- **Refresh**: `POST /api/token/refresh/` -> `{ "refresh": "<REFRESH_TOKEN>" }`
- **Nota**: Para el resto de peticiones, añade el Header: `Authorization: Bearer <ACCESS_TOKEN>`.

### 📺 Catálogo y Contenido
- **Listar Videos**: `GET /api/videos/`
- **Buscar Video**: `GET /api/videos/?search=nombre_o_categoría`
- **Filtrar por Serie**: `GET /api/videos/?serie=<ID_SERIE>`
- **Detalle de Video**: `GET /api/videos/<ID_VIDEO>/` (Incluye contadores y si el usuario actual dio like).

### 💬 Comentarios y Respuestas
- **Comentario Principal**: `POST /api/comments/` -> `{ "video": <ID>, "content": "Texto" }`
- **Responder a Comentario**: `POST /api/comments/` -> `{ "video": <ID>, "content": "Respuesta", "parent": <ID_PADRE> }`
- **Like a un Comentario**: `POST /api/comments/<ID_COMENTARIO>/like/`

### 🌐 Interacciones y Social
- **Like/Unlike Video**: `POST /api/video-interactions/toggle-like/` -> `{ "video_id": <ID_VIDEO> }`
- **Agregar a Favoritos**: `POST /api/favorites/` -> `{ "video": <ID_VIDEO> }`
- **Listar mis Favoritos**: `GET /api/favorites/`
- **Eliminar de Favoritos**: `DELETE /api/favorites/<ID_FAVORITO>/`

### 🎬 Series y Categorías
- **Listar Series**: `GET /api/series/`
- **Detalle de Serie**: `GET /api/series/<ID_SERIE>/` (Muestra la lista de episodios vinculados).
- **Listar Categorías**: `GET /api/categories/`

## 📂 Estructura del Repositorio

* **requirements.txt**: Lista de dependencias del proyecto, incluyendo Django 6.0.3, Django REST Framework, SimpleJWT para autenticación y drf-spectacular para documentación.

* **core/**: Corazón del proyecto. Contiene la configuración global (`settings.py`), el enrutamiento central (`urls.py`) y utilitarios transversales como `media_serve.py` para el manejo de video en desarrollo.

* **users/**: Gestión de perfiles y seguridad. Contiene la lógica de autenticación, el modelo de usuario personalizado, y los ViewSets para el registro y actualización de perfiles.

* **videos/**: Núcleo del catálogo multimedia. Define la estructura de contenidos mediante los modelos de `Category` (géneros), `Series` (agrupaciones de temporadas) y `Video` (episodios individuales con soporte de streaming).

* **interactions/**: Módulo de engagement social. Gestiona la lógica de `Favorites` para el guardado de contenido y `Comments` con soporte para respuestas anidadas y likes individuales por comentario.

* **media/**: Directorio local (excluido en producción) que almacena los archivos físicos de video y miniaturas para pruebas de streaming y ranged requests.

* **manage.py**: Herramienta de línea de comandos de Django para tareas administrativas, migraciones y ejecución del servidor de desarrollo.
