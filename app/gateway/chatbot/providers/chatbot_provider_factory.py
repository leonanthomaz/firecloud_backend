# app/gateway/provider_factory.py

from app.configuration.settings import Configuration
from app.gateway.chatbot.providers.chatbot_provider import IAProvider

from app.gateway.chatbot.providers.IA.deepseek import DeepSeekProvider
from app.gateway.chatbot.providers.IA.gemini import GeminiProvider
from app.gateway.chatbot.providers.IA.openai import OpenaiProvider

import logging

config = Configuration()

def get_ia_provider() -> IAProvider:
    """Retorna a instância do provedor de IA configurado."""
    
    provider = config.ia_provider
    logging.info(f"Inteligência Artificial escolhida: {provider}")
    
    if provider == "gemini":
        return GeminiProvider()
    elif provider == "openai":
        return OpenaiProvider()
    else:
        return DeepSeekProvider()

