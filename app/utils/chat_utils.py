from datetime import datetime, timedelta, timezone
import logging
from typing import Any, Dict, Optional
import uuid

from fastapi import HTTPException
from sqlmodel import Session, select

from app.configuration.settings import Configuration
from app.gateway.chatbot.handlers.handlers import call_fallback
from app.models.chat.chat import Chat
from app.models.chat.interaction import Interaction
from app.models.chat.assistant import Assistant
from app.models.chat.sentiment import Sentiment
from app.enums.chat import ChatIntent, ChatSentiment, ChatbotStatus

Configuration()
# Construtor de contexto para o chatbot
async def build_chat_context(data, assistant_data, chatbot, intents, selected_intent, sentiment_str, company_data, service_data=None, schedule_data=None, schedule_slots_data=None) -> Dict[str, Any]:
    context = {
        "user_message": data.message,
        "intents": [i for i in intents],
        "main_intent": selected_intent,
        "history": chatbot.context_json.get("history", []) if chatbot.context_json else [],
        "step": chatbot.step,
        "sentiment": sentiment_str if sentiment_str else ChatSentiment.NEUTRAL,
        "data": {
            "company": company_data,
            "assistant": assistant_data,
        }
    }

    if service_data:
        context["data"]["services"] = service_data

    if schedule_data:
        context["data"]["schedule"] = schedule_data
        
    if schedule_slots_data:
        context["data"]["schedule_slots"] = schedule_slots_data

    return context

# ================ #

# Função para construir um contexto bloqueado
async def build_blocked_context(selected_intent: ChatIntent, chatbot: Chat, context: Dict[str, Any], session: Session) -> Optional[Dict[str, Any]]:
    if selected_intent == ChatIntent.CLOSE_CHAT:
        reset_chatbot_count(chatbot)
        logging.info(f"CHAT >>> Encerrando chat...")
        context = {
            "useful_context": {
                "user_response": "Obrigado pelo contato, conversa encerrada.",
                "system_response": {"function": "close_chat"},
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "status": 200,
            "chat_code": chatbot.chat_code
        }
        return context
            
    if selected_intent == ChatIntent.ABUSIVE:
        logging.info(f"AI MEU PAU INCHADO: {context}")
        logging.warning(f"CHAT >>> BLOQUEADO por abuso: Mensagem: '{context.get('original_message')}'")
        fallback = await call_fallback(
            context=context,
            reason="abusive_interaction",
            origin="router_precheck"
        )
        return fallback["useful_context"]
            
    if context.get("main_intent") == ChatIntent.TRANSFER_HUMAN:
        fallback = await call_fallback(
                context=context,
                reason="human_unavailable",
                origin="router_precheck"
            )
        logging.info(f"CHAT >>> Transferindo para atendendimento humano: {fallback}")
        return fallback["useful_context"]
    
    if chatbot:
        assistant = None
        if not assistant:
            # fallback: buscar no banco
            assistant = session.exec(
                select(Assistant).where(Assistant.company_id == chatbot.company_id)
            ).first()

        if assistant and assistant.status in [ChatbotStatus.OFFLINE, ChatbotStatus.MAINTENANCE]:
            logging.warning(f"CHAT >>> Indisponível: {assistant.status}")
            fallback = await call_fallback(
                context=context,
                reason="chatbot_unavailable",
                origin="router_precheck"
            )
            return fallback["useful_context"]

# ================ #

# Zerador de contagem do chatbot - se passou 24h da última interação
def reset_chatbot_count(chatbot) -> str:
    now = datetime.now(timezone.utc)
    if chatbot.last_interaction_at.replace(tzinfo=timezone.utc) < now - timedelta(hours=24):
        chatbot.interaction_count = 0
        return f"Contagem de interações zerada para {chatbot.company_id}"
    return f"Contagem de interações não zerada para {chatbot.company_id}, última interação foi há menos de 24 horas"

# ================ #

# Verifica se o número de interações do chatbot foi atingido    
async def check_chatbot_count(chatbot: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    if chatbot.max_interaction is not None and chatbot.interaction_count >= chatbot.max_interaction:
        fallback = await call_fallback(
            context=context,
            reason="limit_reached",
            origin="router_precheck"
        )
        return {
            "blocked": True,
            "data": fallback["useful_context"]
        }
    
    return {
        "blocked": False,
        "message": "Número de interações dentro do limite."
    }

# ================ #

# Atualiza a interação e os dados do assistente
def update_interaction_and_assistant(
    session,
    chatbot,
    company_id: int,
    sentiment_str: str,
    useful_context: dict
):
    """Atualiza a Interaction, Sentiment agregador e dados do Assistant."""
    now = datetime.now(timezone.utc)

    # Busca ou cria interação
    interaction = chatbot.interaction
    if not interaction:
        interaction = Interaction(
            company_id=company_id,
            chat_id=chatbot.id,
            created_at=now,
        )
        session.add(interaction)

    # Atualiza campos padrão da interação
    interaction.updated_at = now
    sentiment_enum = ChatSentiment[sentiment_str.upper()] if sentiment_str else ChatSentiment.NEUTRAL
    interaction.sentiment = sentiment_enum

    # Popula campos do contexto
    interaction.client_name = useful_context.get("client_name")
    interaction.client_contact = useful_context.get("client_contact")
    interaction.interaction_type = useful_context.get("interaction_type", "standard")
    interaction.interaction_summary = useful_context.get("summary")
    interaction.ai_generated_insights = useful_context.get("insights")

    token_usage = useful_context.get("token_usage", {})
    interaction.prompt_tokens = token_usage.get("prompt_tokens", 0)
    interaction.completion_tokens = token_usage.get("completion_tokens", 0)
    interaction.total_tokens = token_usage.get("total_tokens", 0)

    session.add(interaction)

    # === Atualiza sentimento agregado ===
    sentiment = chatbot.sentiment
    if not sentiment:
        sentiment = Sentiment(chat_id=chatbot.id)
        session.add(sentiment)

    if sentiment_enum == ChatSentiment.POSITIVE:
        sentiment.sentiment_positive_count += 1
    elif sentiment_enum == ChatSentiment.NEGATIVE:
        sentiment.sentiment_negative_count += 1
    else:
        sentiment.sentiment_neutral_count += 1

    # Recalcula sentimento predominante
    counts = {
        ChatSentiment.POSITIVE: sentiment.sentiment_positive_count,
        ChatSentiment.NEGATIVE: sentiment.sentiment_negative_count,
        ChatSentiment.NEUTRAL: sentiment.sentiment_neutral_count
    }
    sentiment.final_sentiment = max(counts, key=counts.get)
    sentiment.updated_at = now

    session.add(sentiment)

    # === Atualiza tokens do assistente ===
    if token_usage:
        assistant = session.exec(
            select(Assistant).where(Assistant.company_id == company_id)
        ).first()

        if assistant:
            # Reset mensal se necessário
            if (
                assistant.assistant_token_reset_date is None or
                assistant.assistant_token_reset_date.month != now.month
            ):
                assistant.assistant_token_usage = 0
                assistant.assistant_token_reset_date = now.replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )

            total = token_usage.get("total_tokens", 0)
            limit = assistant.assistant_token_limit or 0

            if limit > 0 and (assistant.assistant_token_usage + total) > limit:
                raise HTTPException(
                    status_code=403,
                    detail="Limite de tokens atingido para este plano."
                )

            assistant.assistant_token_usage += total
            assistant.updated_at = now
            session.add(assistant)

    # Commit geral
    session.commit()

    # Refresh final
    session.refresh(chatbot)
    session.refresh(interaction)
    session.refresh(sentiment)


# ================ #

# Retorna um chat existente ou cria um novo
def get_or_create_chat(
    session: Session,
    company_id: int,
    whatsapp_id: Optional[str] = None,
    chat_code: Optional[str] = None
) -> Chat:
    # Tenta buscar por whatsapp_id primeiro
    if whatsapp_id:
        chatbot = session.exec(
            select(Chat)
            .where(Chat.company_id == company_id)
            .where(Chat.whatsapp_id == whatsapp_id)
        ).first()
        if chatbot:
            return chatbot

    # Tenta buscar por chat_code
    if chat_code:
        chatbot = session.exec(
            select(Chat)
            .where(Chat.company_id == company_id)
            .where(Chat.chat_code == chat_code)
        ).first()
        if chatbot:
            return chatbot
        else:
            logging.warning(f"CHAT >>> chat_code inválido ou não encontrado para company_id={company_id}: {chat_code}")

    # Cria um novo chat se nenhum for encontrado
    short_hash = str(uuid.uuid4()).split('-')[0]
    new_chat_code = f"chat_{company_id}_{short_hash}"
    
    chatbot = Chat(
        company_id=company_id,
        whatsapp_id=whatsapp_id,
        chat_code=new_chat_code,
        last_interaction_at=datetime.now(timezone.utc)
    )
    session.add(chatbot)
    session.commit()
    session.refresh(chatbot)
    return chatbot

# ================ #

# Verifica se o contexto contém os campos obrigatórios          
async def check_context_integrity(
    context: Dict[str, Any], 
    schedule_data: Dict[str, Any],
    schedule_slots_data: Dict[str, Any],
    ) -> Dict[str, Any]:
    
    if not context.get("data", {}).get("assistant") or not context.get("data", {}).get("company"):
        fallback = await call_fallback(
            context=context,
            reason="incomplete_data",
            origin="router_precheck"
        )
        logging.info(f"CHAT >>> CONTEXT INTEGRITY >>> Dados obrigatórios ausentes: {fallback}")
        return fallback["useful_context"]
    
    if context.get("main_intent") == ChatIntent.SCHEDULE_INFO:
        if not schedule_data or len(schedule_data) == 0:
            fallback = await call_fallback(
                context=context,
                reason="no_schedule",
                origin="router_precheck"
            )
            logging.info(f"CHAT >>> CONTEXT INTEGRITY >>> Sem dados de agendamento de agendamento: {fallback}")
            return fallback["useful_context"]
        
    if context.get("main_intent") == ChatIntent.SCHEDULE_SLOT_INFO:
        if not schedule_slots_data or len(schedule_slots_data) == 0:
            fallback = await call_fallback(
                context=context,
                reason="no_schedule_slots",
                origin="router_precheck"
            )
            logging.info(f"CHAT >>> CONTEXT INTEGRITY >>> Sem dados de agendamento de agendamento: {fallback}")
            return fallback["useful_context"]
    
    return context

# ================ #

# Carrega todos os dados do cache       
async def load_all_cached_data(cache_manager, session, company_id: int) -> dict:
    """Carrega todos os dados relacionados ao company_id de uma vez."""
    
    data_map = {
        "company_data": cache_manager.get_company_data,
        "assistant_data": cache_manager.get_assistant_data,
        "service_data": cache_manager.get_service_data,
        "schedule_slots_data": cache_manager.get_schedule_slots_data,
        "schedule_data": cache_manager.get_schedule_data,
    }

    result = {}
    for key, method in data_map.items():
        result[key] = await method(session, company_id)
        if result[key] is None:
            log_func = logging.error if "company" in key or "assistant" in key else logging.warning
            log_func(f"CACHE >>> {key} é None")

    return result

# ================ #
