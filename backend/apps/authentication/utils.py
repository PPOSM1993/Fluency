from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .tokens import account_activation_token
from django.contrib.auth.tokens import default_token_generator


def send_confirmation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    activation_url = request.build_absolute_uri(
        reverse('confirm-email', kwargs={'uidb64': uid, 'token': token})
    )

    subject = 'Confirma tu cuenta en CineWave'
    message = f'''
    Hola {user.first_name},

    Gracias por registrarte en CineWave. Para activar tu cuenta, haz clic en el siguiente enlace:

    {activation_url}

    Si no realizaste este registro, puedes ignorar este mensaje.
    '''

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        print(f"[INFO] Email de activación enviado a {user.email}")
    except Exception as e:
        print(f"[ERROR] Error enviando email a {user.email}: {str(e)}")


def send_password_reset_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_url = request.build_absolute_uri(
        reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})
    )

    subject = 'Restablece tu contraseña'
    message = f'''
    Hola {user.first_name},

    Has solicitado restablecer tu contraseña. Haz clic en el siguiente enlace:

    {reset_url}

    Si no realizaste esta solicitud, ignora este mensaje.
    '''

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )