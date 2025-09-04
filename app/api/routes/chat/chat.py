import logging
from fastapi import APIRouter, HTTPException, Response, Depends
from sqlmodel import Session
from app.database.connection import get_session
from datetime import datetime, timezone

from app.configuration.settings import Configuration

from app.enums.chat import ChatIntent

from app.gateway.chatbot.nlp.context_classifier import ContextClassifier
from app.schemas.chat.chat import ChatRequest

from app.cache.cache import Cache
from app.cache.cache_manager import CacheManager

from app.gateway.chatbot.engine.generate_response import generate_response
from app.gateway.chatbot.engine.generate_response_fake import generate_response_fake
from app.gateway.chatbot.nlp.context_filter import ContextFilter
from app.gateway.chatbot.nlp.intent_classifier import IntentClassifier
from app.gateway.chatbot.nlp.sentiment_classifier import SentimentClassifier

from app.utils.spacy_utils import SpacyProcessor
from app.utils.chat_utils import build_blocked_context, build_chat_context, check_chatbot_count, check_context_integrity, get_or_create_chat, load_all_cached_data, reset_chatbot_count, update_interaction_and_assistant

db_session = get_session
Configuration()
cache = Cache()

class ChatRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.intent_classifier = IntentClassifier()
        self.sentiment_classifier = SentimentClassifier()
        self.filter_context = ContextFilter()
        self.context_classifier = ContextClassifier()
        self.spacy_processor = SpacyProcessor()
        self.cache_manager = CacheManager()
        self.add_api_route("/chat/company/{company_id}", self.chat, methods=["POST"])

    async def chat(self, company_id: int, data: ChatRequest, session: Session = Depends(db_session)) -> Response:
        logging.info(f"DADOS DA REQUISIÇÃO: >>> {data}")
        try:
            try:
                chatbot = get_or_create_chat(
                    session=session,
                    company_id=company_id,
                    whatsapp_id=data.whatsapp_id,
                    chat_code=data.chat_code
                )
            except Exception as e:
                logging.exception(f"Erro ao criar ou buscar chat: {e}")
                raise
            context = chatbot.context_json
            logging.info(f"CHAT >>> Chat carregado/criado: {context}")
                               
            # Zera a contagem se passou 24h da última interação
            reset_chatbot = reset_chatbot_count(chatbot)
            logging.info(f"CHAT >>> {reset_chatbot}")
            
            # Verifica se o numero de interações foi atingido
            check_chatbot = await check_chatbot_count(chatbot, context)
            if check_chatbot["blocked"]:
                return check_chatbot["data"]
            logging.info(f"CHAT >>> {check_chatbot['message']}")

            keywords = self.spacy_processor.process_message(data.message)
            chatbot.step = chatbot.step.IN_PROGRESS
            logging.info(f"CHAT >>> PALAVRAS CHAVE >>> Palavras chave extraídas: {keywords}")
            
            intents = self.intent_classifier.classify_intent(keywords, data.message)
            logging.info(f"CHAT >>> INTENÇÕES >>> Intenções classificadas: {[i.name for i in intents]}")
                       
            selected_intent = self.intent_classifier.get_priority_intent(intents)
            logging.info(f"CHAT >>> INTENÇÕES >>> Priorizando Intenções >>> {selected_intent}")
            
            context_blocked = await build_blocked_context(selected_intent, chatbot, context, session)
            if context_blocked:
                chatbot.step = chatbot.step.BLOCKED_ABUSE if selected_intent == ChatIntent.ABUSIVE else chatbot.step.CLOSING
                return context_blocked

            sentiment_str = self.sentiment_classifier.detect_sentiment(data.message)
            logging.info(f"CHAT >>> SENTIMENTO >>> {sentiment_str}")
            
            if selected_intent not in [ChatIntent.CLOSE_CHAT, ChatIntent.ABUSIVE]:
                cached_data = await load_all_cached_data(self.cache_manager, session, company_id)
                company_data = cached_data["company_data"]
                assistant_data = cached_data["assistant_data"]
                service_data = cached_data["service_data"]
                schedule_slots_data = cached_data["schedule_slots_data"]
                schedule_data = cached_data["schedule_data"]
                logging.info(f"CHAT >>> Dados do cache carregados.")

                context = await build_chat_context(
                    data=data,
                    chatbot=chatbot,
                    intents=intents,
                    sentiment_str=sentiment_str,
                    selected_intent=selected_intent,
                    company_data=company_data,
                    assistant_data=assistant_data,
                    service_data=service_data,
                    schedule_data=schedule_data,
                    schedule_slots_data=schedule_slots_data,
                )
                logging.info(f"CHAT >>> Contexto montado >>> {context}")
                                
                context = self.context_classifier.filter_context(context)
                logging.info(f"CHAT >>> Contexto filtrado: {context}")
                            
                context = await check_context_integrity(context, schedule_data, schedule_slots_data)
                logging.info(f"CHAT >>> Integridade do contexto validado: {context}")
            
            logging.info(f"CHAT >>> Dados ANTES de enviar para IA: {context}")
            # response_data = await generate_response(context)
            response_data = await generate_response_fake(context)
            logging.info(f"CHAT >>> Dados DEPOIS de enviar para IA: {response_data}")
            
            useful_context = response_data.get("useful_context", {})
            
            chatbot.context_json = useful_context
            chatbot.interaction_count += 1
            chatbot.updated_at = datetime.now(timezone.utc)
            
            update_interaction_and_assistant(
                session=session,
                chatbot=chatbot,
                company_id=company_id,
                sentiment_str=sentiment_str,
                useful_context=useful_context
            )
            
            return {
                **response_data,
                "chat_code": chatbot.chat_code
            }

        except Exception as e:
            logging.error(f"CHAT >>> Erro ao processar o chat: {e}")
            raise HTTPException(status_code=502, detail="Erro de comunicação com a IA.")

            
