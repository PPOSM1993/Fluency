from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailUsernameRutBackend(ModelBackend):
    """
    Permite autenticación usando email, username o RUT.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(
                Q(email__iexact=username) |
                Q(username__iexact=username) |
                Q(rut__iexact=username)
            )
        except User.DoesNotExist:
            return None

        if user.check_password(password) and user.is_active:
            return user

        return None