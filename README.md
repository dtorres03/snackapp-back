# 🚀 SnackApp Backend - API REST

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
   git clone https://github.com/tu-usuario/snackapp-back.git
   cd snackapp-back

2. **Configura variables de entorno:**
   #### Crea un archivo .env en la raíz del proyecto basándote en el siguiente esquema:
   ```bash
   DB_NAME=dbname
   DB_USER=usuario
   DB_PASSWORD=contraseña
   DB_HOST=localhost
   DB_PORT=5432
   SECRET_KEY=tu_django_secret_key
   DEBUG=True
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

| Método | Endpoint | Descripción | Auth Requerida |
| :--- | :--- | :--- | :--- |
| **POST** | `/api/users/` | Registro de nuevo usuario (Sign up) | No |
| **POST** | `/api/login/` | Obtener Tokens Access y Refresh (Login) | No |
| **POST** | `/api/token/refresh/` | Generar nuevo Access Token | Refresh Token |
| **GET** | `/api/users/` | Listar todos los usuarios registrados | Token Access |
| **GET** | `/api/users/{id}/` | Ver detalle de un usuario específico | Token Access |
| **PATCH** | `/api/users/{id}/` | Actualizar perfil (Solo Dueño o Admin) | Token Access |
| **DELETE** | `/api/users/{id}/` | Eliminar cuenta (Solo Dueño o Admin) | Token Access |
| **GET** | `/api/videos/` | Listar catálogo de videos | Token Access |
| **GET** | `/api/favorites/` | Listar videos favoritos | Token Access |
| **POST** | `/api/favorites/` | Guardar video en favoritos | Token Access |

> ⚠️ **IMPORTANTE:** Todas las URLs deben terminar en `/` (trailing slash). 
> De lo contrario, Django podría devolver un error 404 o 500 al realizar peticiones `PATCH` o `POST`.
>
> **Ejemplo correcto:** `http://127.0.0.1:8000/api/users/550e8400-e29b-4114-a432-444666540102/`

## 🧪 Pruebas en Postman

1. Login: Envía un POST a /api/login/ con email y password.

2. Autorización: Copia el valor de access.

3. Headers: En las peticiones protegidas, ve a la pestaña Auth, selecciona Bearer Token y pega el código.

4. Validación: Si intentas editar un ID ajeno con un token de usuario normal, recibirás un 403 Forbidden.

## 📂 Estructura del Repositorio

* requirements.txt: Lista de dependencias (Django 6.0.3, DRF, SimpleJWT).

* core/: Configuración principal del proyecto.

* users/: Aplicación de lógica de usuarios y autenticación.

* videos/: Modelos de Category, Serie y Video (Episodios).

* interactions/: Lógica de favoritos y feedback de usuario.
