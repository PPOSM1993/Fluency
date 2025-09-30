from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "conversation", "role", "content", "audio_file", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate(self, data):
        """
        Validaciones adicionales para los mensajes
        """
        content = data.get("content")
        audio_file = data.get("audio_file")

        # Al menos uno de los dos campos debe estar presente
        if not content and not audio_file:
            raise serializers.ValidationError(
                "Debes enviar al menos texto o un archivo de audio."
            )

        # Límite de caracteres (aunque ya está en el modelo, validamos aquí también)
        if content and len(content) > 1000:
            raise serializers.ValidationError(
                "El mensaje no puede superar los 1000 caracteres."
            )

        return data


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)

    class Meta:
        model = Conversation
        fields = ["id", "user", "created_at", "messages"]
        read_only_fields = ["id", "created_at"]

    def validate_user(self, value):
        """
        Evita que un usuario cree conversaciones para otro usuario.
        """
        request = self.context.get("request")
        if request and request.user != value:
            raise serializers.ValidationError(
                "No puedes crear conversaciones para otro usuario."
            )
        return value
