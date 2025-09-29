from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from .tokens import account_activation_token
from .serializers import *
from .permissions import IsOwner
from .utils import send_confirmation_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save(is_active=False)
        send_confirmation_email(self.request, user)

class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"error": "No se envió el refresh token."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Sesión cerrada correctamente."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"error": "Token inválido o ya fue usado."}, status=status.HTTP_400_BAD_REQUEST)

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOwner]

    def get_object(self):
        return self.request.user

class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return HttpResponse('El enlace de activación no es válido.', content_type='text/plain')

        if user is not None and account_activation_token.check_token(user, token):
            user.is_active = True
            user.save()
            return HttpResponse('¡Cuenta activada! Ya puedes iniciar sesión.', content_type='text/plain')

        return HttpResponse('El enlace de activación es inválido o ha expirado.', content_type='text/plain')

class ResendActivationEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'detail': 'Debes proporcionar un email.'}, status=400)

        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response({'detail': 'Esta cuenta ya está activada.'}, status=400)

            send_confirmation_email(request, user)
            return Response({'detail': 'Correo de activación reenviado.'}, status=200)

        except User.DoesNotExist:
            return Response({'detail': 'Usuario no encontrado.'}, status=404)

class CheckAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        email = request.query_params.get('email')
        username = request.query_params.get('username')
        rut = request.query_params.get('rut')

        if email and User.objects.filter(email=email).exists():
            return Response({'detail': 'Este email ya está registrado.'}, status=400)
        if username and User.objects.filter(username=username).exists():
            return Response({'detail': 'Este username ya está en uso.'}, status=400)
        if rut and User.objects.filter(rut=rut).exists():
            return Response({'detail': 'Este RUT ya está en uso.'}, status=400)

        return Response({'detail': 'Disponible.'}, status=200)

class RequestPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            send_password_reset_email(request, user)
            return Response({'detail': 'Se ha enviado un email para restablecer tu contraseña.'})
        except User.DoesNotExist:
            return Response({'detail': 'No existe cuenta asociada a este email.'}, status=404)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        password = request.data.get('password')
        password2 = request.data.get('password2')

        if password != password2:
            return Response({'detail': 'Las contraseñas no coinciden.'}, status=400)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({'detail': 'Enlace inválido.'}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({'detail': 'Token inválido o expirado.'}, status=400)

        user.set_password(password)
        user.save()
        return Response({'detail': 'Tu contraseña ha sido restablecida correctamente.'})