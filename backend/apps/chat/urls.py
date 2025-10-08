from django.urls import path
from .views import ConversationListCreateView, MessageCreateView, ConversationDetailView
from .views import VoiceToTextView, TextToVoiceView

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name="conversation-list-create"),
    path("conversations/<int:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),
    path("messages/", MessageCreateView.as_view(), name="message-create"),
    
    path("voice-to-text/", VoiceToTextView.as_view(), name="voice_to_text"),
    path("text-to-voice/", TextToVoiceView.as_view(), name="text_to_voice"),
]
