from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

User = get_user_model()

class EmailOrUsernameModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Si por alguna razón no llega el parámetro, intentamos buscar en kwargs
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        try:
            # Busca si el valor ingresado coincide con el campo 'username' O con 'email'
            user = User.objects.get(Q(username__iexact=username) | Q(email__iexact=username))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Si por algún error de base de datos hubiera duplicados, tomamos el primero
            user = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()

        # Si encontramos al usuario, verificamos la contraseña con el método nativo
        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None