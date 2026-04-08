from rest_framework import serializers
from .models import CustomUser
from rest_framework.exceptions import ValidationError
import re

class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True, allow_blank=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'password', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': True},
            'created_at': {'read_only': True},
            #'email': {'required': True}
        }

    # --- VALIDACIONES DE CAMPO (Para el Front) ---

    def validate_email(self, value):
        """Verifica si el email ya existe antes de intentar guardarlo."""
        # Convertimos a minúsculas para evitar duplicados por capitalización
        email = value.lower()
        if self.instance: # Si estamos editando (update)
            if CustomUser.objects.filter(email=email).exclude(id=self.instance.id).exists():
                raise ValidationError("Este correo ya está registrado por otro usuario.")
        else: # Si estamos creando
            if CustomUser.objects.filter(email=email).exists():
                raise ValidationError("Ya existe una cuenta con este correo electrónico.")
        return email

    def validate_username(self, value):
        # 1. Eliminar espacios en blanco accidentales a los lados
        username = value.strip() if value else ""

        # 2. Validar si está vacío (strip() dejará "" si solo enviaron espacios)
        if not username:
            raise ValidationError("El nombre de usuario no puede estar vacío.")

        # 3. Validar longitud mínima
        if len(username) < 5:
            raise ValidationError("El nombre de usuario es muy corto (mínimo 5 caracteres).")

        # 4. Validar longitud máxima (importante para tu DB en Arch)
        if len(username) > 10:
            raise ValidationError("El nombre de usuario es muy largo (máximo 10 caracteres).")

        # 5. Validar caracteres permitidos (Solo letras, números y guiones bajos)
        # Esto evita que inyecten scripts o caracteres raros que rompan el front
        if not re.match(r'^[\w]+$', username):
            raise ValidationError("El nombre de usuario solo puede contener letras, números y guiones bajos (_).")

        # 6. Verificar si ya existe (aunque Django lo hace, aquí controlamos el mensaje)
        if self.instance is None or self.instance.username != username:
            if CustomUser.objects.filter(username=username).exists():
                raise ValidationError("Este nombre de usuario ya está en uso.")

        return username

    def validate_password(self, value):
        # 1. Validar si está vacío
        if not value or value.strip() == "":
            raise ValidationError("La contraseña es obligatoria y no puede estar vacía.")

        # 2. Longitud mínima
        if len(value) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

        # 3. Validar que contenga al menos un número
        if not re.search(r'\d', value):
            raise ValidationError("La contraseña debe incluir al menos un número.")

        # 4. Validar que contenga al menos una mayúscula
        if not re.search(r'[A-Z]', value):
            raise ValidationError("La contraseña debe incluir al menos una letra mayúscula.")

        # 5. Validar caracteres especiales (Opcional, pero recomendado para streaming)
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            raise ValidationError("La contraseña debe incluir al menos un carácter especial (!@#$%^&*, etc.).")

        return value

    # --- LÓGICA DE GUARDADO ---

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        
        # Actualizamos campos normales
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance