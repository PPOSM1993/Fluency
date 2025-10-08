import os
import openai
from django.conf import settings

# 🔹 Configurar clave API
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_ai_response(messages, model="gpt-4", temperature=0.7, max_tokens=500):
    """
    Envía la conversación al modelo de IA y recibe respuesta.

    :param messages: lista de mensajes en formato [{"role": "user", "content": "..."}]
    :param model: modelo de OpenAI
    :param temperature: creatividad/respuesta
    :param max_tokens: cantidad máxima de tokens a generar
    :return: texto generado por la IA
    """

    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        answer = response.choices[0].message.content
        return answer

    except Exception as e:
        print(f"[ERROR] AI service failed: {e}")
        return "Lo siento, no pude procesar tu solicitud. Intenta nuevamente."
