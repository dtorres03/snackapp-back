from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # Añadimos 'username' a la lista
        fields = ['id', 'username', 'email', 'password', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'created_at': {'read_only': True}
        }

    def create(self, validated_data):
        # Django usará automáticamente el username que venga en validated_data
        return CustomUser.objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        # 1. Sacamos la contraseña de los datos para que no se guarde como texto plano
        password = validated_data.pop('password', None)
        
        # 2. Actualizamos el resto de los campos (email, username, etc.)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        # 3. Si había contraseña, usamos set_password para encriptarla
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance