from django.db import models
from django.conf import settings
class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id} - {self.user.username}"
class Message(models.Model):
    ROLE_CHOICES = [
        ("user", "Usuario"),
        ("assistant", "Asistente"),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField(max_length=1000, blank=True, null=True)
    audio_file = models.FileField( upload_to="chat/audio/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        text_preview = self.content[:50] if self.content else "[AUDIO]"
        return f"{self.role}: {text_preview}"
