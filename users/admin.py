from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Configuración del administrador para el usuario personalizado.
    
    Heredamos de UserAdmin para mantener las funcionalidades de gestión 
    de contraseñas y permisos de Django, pero adaptándolo a UUID y Email.
    """
    
    list_display = ('email', 'username', 'tokens', 'is_staff', 'created_at')
    
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    
    search_fields = ('email', 'username')
    
    ordering = ('-created_at',)

    # CONFIGURACIÓN DE FORMULARIOS (Para que aparezcan los Tokens al editar)
    # Reorganizamos los fieldsets originales de Django para incluir nuestro campo
    fieldsets = UserAdmin.fieldsets + (
        ('Información de Tokens', {'fields': ('tokens',)}),
    )
    
    # También para el formulario de creación de usuario
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información de Tokens', {'fields': ('tokens',)}),
    )