from datetime import datetime, timezone
import logging
from app.enums.chat import ChatSentiment
from app.gateway.chatbot.providers.chatbot_provider_factory import get_ia_provider
from app.configuration.settings import Configuration

Configuration()

async def generate_response(context: dict) -> dict:
    try:
        ia_response = await get_ia_provider().generate_response(context)
        useful_context = ia_response.get("useful_context", {})
        history = context.get("history", [])
        history.append({
            "user_message": useful_context["user_response"],
            "ia_response": useful_context["user_message"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intent": useful_context.get("intents", context.get("intents", []))
        })
        
        return {
            "useful_context": {
                "user_response": useful_context["user_response"],
                "user_message": useful_context["user_message"],
                "system_response": useful_context.get("system_response", {}),
                "intents": useful_context.get("intents", context.get("intents", [])),
                "main_intent": useful_context.get("main_intent", context.get("main_intent")),
                "sentiment": useful_context.get("sentiment", context.get("sentiment", ChatSentiment.NEUTRAL)),
                "history": history,
                "token_usage": useful_context.get("token_usage", {}),
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "status": 200
        }
    except Exception as e:
        logging.error(f"Erro ao processar resposta: {str(e)}")
        return {
            "useful_context": {
                "user_response": "Houve um problema. Pode repetir?",
                "system_response": {"function": "no_action"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "status": 200 
        }