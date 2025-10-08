from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsConversationOwner
from django.conf import settings
from openai import OpenAI  # 👈 ESTE IMPORT FALTABA

from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated

from gtts import gTTS
from django.http import FileResponse
import io

class ConversationListCreateView(generics.ListCreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class MessageCreateView(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        conversation = serializer.validated_data["conversation"]
        if conversation.user != self.request.user:
            raise PermissionError("No tienes permiso para enviar mensajes a esta conversación.")

        # Guardar el mensaje del usuario
        user_message = serializer.save(sender="user")

        # Llamar a OpenAI para obtener la respuesta
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente útil que responde en español."},
                {"role": "user", "content": user_message.content},
            ],
        )

        assistant_reply = response.choices[0].message.content

        # Guardar respuesta del asistente en la misma conversación
        Message.objects.create(
            conversation=conversation,
            sender="assistant",
            content=assistant_reply
        )
class ConversationDetailView(generics.RetrieveAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationOwner]
    queryset = Conversation.objects.all()

class VoiceToTextView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        audio_file = request.FILES.get("audio")

        if not audio_file:
            return Response({"error": "No se envió archivo de audio."}, status=400)

        client = OpenAI(api_key=settings.OPENAI_API_KEY)

        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )

        return Response({"text": transcript.text})



class TextToVoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        text = request.data.get("text", "")
        if not text:
            return Response({"error": "Texto vacío"}, status=400)

        tts = gTTS(text=text, lang="en")  # o "es" según lo que necesites
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)

        return FileResponse(audio_bytes, content_type="audio/mpeg")