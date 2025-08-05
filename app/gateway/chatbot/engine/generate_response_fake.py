from datetime import datetime, timedelta, timezone
import logging
import random
from typing import Dict

from app.configuration.settings import Configuration
from app.enums.chat import ChatIntent, ChatSentiment
from app.gateway.chatbot.mock.fake_sentiment_analysis import fake_sentiment_analysis

Configuration()

class FakeAIProvider:
    def __init__(self):
        self.base_token_cost = {
            "prompt_tokens": 50,
            "completion_tokens": 30,
            "total_tokens": 80
        }
        self.variation_range = 20  # Variação de +/- 20 tokens

    def _generate_token_usage(self) -> Dict[str, int]:
        """Calcula prompt + completion com variação, e soma pro total"""
        prompt = max(10, self.base_token_cost["prompt_tokens"] + random.randint(-self.variation_range, self.variation_range))
        completion = max(5, self.base_token_cost["completion_tokens"] + random.randint(-self.variation_range, self.variation_range))
        total = prompt + completion
        return {
            "prompt_tokens": prompt,
            "completion_tokens": completion,
            "total_tokens": total
        }


async def generate_response_fake(context: Dict) -> Dict:
    try:
        # Inicializa o provedor fake
        fake_provider = FakeAIProvider()
        
        # Processa dados básicos do contexto
        main_intent = context.get("main_intent", ChatIntent.GERAL)
        user_message = context.get("user_message", "").lower()
        step = context.get("step", "START")

        # Análise de sentimento (fake)
        sentiment = context.get("sentiment")
        
        if sentiment is None:
            sentiment = fake_sentiment_analysis(user_message)

        # Respostas baseadas em intenção
        responses = {
            ChatIntent.WELCOME: {
                "user_response": "Olá! Seja bem-vindo(a) à nossa empresa. Como posso te ajudar hoje?",
                "system_response": {"function": "greet"},
                "token_boost": 10  # Respostas de saudação costumam ser um pouco maiores
            },
            ChatIntent.SCHEDULE_SLOT_INFO: {
                "user_response": "Vamos agendar! Temos estes horários disponíveis:",
                "system_response": {
                    "function": "schedule_slots",
                    "schedule_slots": [
                        {
                            "id": 1,
                            "public_id": "slot-1",
                            "start": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
                            "end": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
                            "all_day": False,
                            "is_active": True,
                            "is_recurring": False,
                            "company_id": 1,
                            "service_id": None,
                            "schedule_id": None
                        },
                        {
                            "id": 2,
                            "public_id": "slot-2",
                            "start": (datetime.now(timezone.utc) + timedelta(hours=3)).isoformat(),
                            "end": (datetime.now(timezone.utc) + timedelta(hours=4)).isoformat(),
                            "all_day": False,
                            "is_active": True,
                            "is_recurring": False,
                            "company_id": 1,
                            "service_id": None,
                            "schedule_id": None
                        }
                    ]
                },
                "token_boost": 30  # Respostas com dados extras usam mais tokens
            },

            ChatIntent.CANCEL: {
                "user_response": "Seu agendamento foi cancelado com sucesso.",
                "system_response": {"function": "cancel_appointment"},
                "token_boost": 15
            },
            ChatIntent.PAYMENT: {
                "user_response": "Aceitamos Pix, cartão (até 12x) e dinheiro.",
                "system_response": {"function": "show_payment_options"},
                "token_boost": 25
            },
            ChatIntent.DELIVERY: {
                "user_response": "Seu pedido está a caminho! Previsão de entrega: 30-45 minutos.",
                "system_response": {"function": "check_delivery_status"},
                "token_boost": 20
            },
            ChatIntent.COMPLAINT: {
                "user_response": "Lamentamos o ocorrido. Vamos resolver isso para você!",
                "system_response": {"function": "open_complaint_ticket"},
                "token_boost": 15
            },
            ChatIntent.PRAISE: {
                "user_response": "Muito obrigado pelo feedback positivo! Ficamos felizes em te atender.",
                "system_response": {"function": "register_praise"},
                "token_boost": 5
            },
            ChatIntent.DOUBT: {
                "user_response": "Claro, posso te ajudar com isso. O que você gostaria de saber?",
                "system_response": {"function": "answer_question"},
                "token_boost": 10
            },
            ChatIntent.TRANSFER_HUMAN: {
                "user_response": "Vou transferir você para um atendente humano. Um momento por favor...",
                "system_response": {"function": "escalate_to_human"},
                "token_boost": 5
            },
            ChatIntent.GERAL: {
                "user_response": "Entendi. Poderia me dar mais detalhes para que eu possa te ajudar melhor?",
                "system_response": {"function": "general_interaction"},
                "token_boost": 10
            },
            ChatIntent.CLOSE_CHAT: {
                "user_response": "Obrigado por conversar conosco! Poderia avaliar nosso atendimento?",
                "system_response": {"function": "feedback"},
                "token_boost": 5
            },
            ChatIntent.ABUSIVE: {
                "user_response": "Desculpe, mas não podemos aceitar esse tipo de linguagem. Vamos manter o respeito, ok?",
                "system_response": {"function": "abusive_interaction"},
                "token_boost": 15
            },
            ChatIntent.SERVICE_INFO: {
                "user_response": "Temos alguns serviços disponíveis, olha só:",
                "system_response": {
                    "function": "show_service",
                    "service": {
                        "name": "Consulta Geral",
                        "description": "Atendimento clínico completo, ideal para primeira avaliação.",
                        "price": 150.00,
                        "availability": True,
                        "rating": 4.8,
                        "duration": "00:30:00"  # duração em hh:mm:ss
                    }
                },
                "token_boost": 25
            },
            ChatIntent.SERVICE_INFO: {
                "user_response": "Temos alguns serviços disponíveis, olha só:",
                "system_response": {
                    "function": "show_service",
                    "service": [
                        {
                        "name": "Consulta Geral",
                        "description": "Atendimento clínico completo, ideal para primeira avaliação.",
                        "price": 150.00,
                        "availability": True,
                        "rating": 4.8,
                        "duration": "00:30:00"  # duração em hh:mm:ss
                    },
                    {
                        "name": "Consulta Pediátrica",
                        "description": "Atendimento clínico semi, ideal para primeira avaliação.",
                        "price": 350.00,
                        "availability": True,
                        "rating": 4.8,
                        "duration": "1:30:00"  # duração em hh:mm:ss
                    }
                    ]
                },
                "token_boost": 25
            },

        }

        # Seleciona a resposta base ou geral se não encontrada
        selected_response = responses.get(main_intent, responses[ChatIntent.GERAL])
        
        # Ajusta os tokens base com o boost específico da resposta
        fake_provider.base_token_cost["completion_tokens"] += selected_response.get("token_boost", 0)
        token_usage = fake_provider._generate_token_usage()

        # Ajustes baseados em sentimento
        if sentiment == ChatSentiment.NEGATIVE:
            if main_intent == ChatIntent.GERAL:
                selected_response["user_response"] = (
                    "Poxa, parece que algo te incomodou. Me explica melhor pra eu tentar te ajudar?"
                )
            elif main_intent == ChatIntent.CANCEL:
                selected_response["user_response"] = (
                    "Entendi sua frustração. Vamos cancelar conforme solicitado. "
                    "Se quiser remarcar depois, estarei aqui para ajudar."
                )
            elif main_intent == ChatIntent.COMPLAINT:
                selected_response["user_response"] = (
                    "Sinto muito pelo ocorrido! Vamos resolver isso da melhor forma possível."
                )
            # Aumenta tokens para respostas mais elaboradas de sentimentos negativos
            token_usage["completion_tokens"] += 10
            token_usage["total_tokens"] += 10

        elif sentiment == ChatSentiment.POSITIVE:
            if main_intent == ChatIntent.GERAL:
                selected_response["user_response"] = (
                    "Que bom! Fico feliz em te ajudar 😊 Me conta mais detalhes?"
                )
            elif main_intent == ChatIntent.PRAISE:
                selected_response["user_response"] = (
                    "Muito obrigado pelo carinho! Feedback como o seu nos motiva a melhorar cada vez mais ❤️"
                )
            elif main_intent == ChatIntent.SCHEDULE_INFO:
                selected_response["user_response"] = (
                    "Legal! Voce gostaria de visualizar quais agendamentos marcados?"
                )
            elif main_intent == ChatIntent.SCHEDULE_SLOT_INFO:
                selected_response["user_response"] = (
                    "Ótima escolha! Vamos agendar isso para você. Qual desses horários prefere?"
                )
            # Aumenta levemente tokens para respostas positivas
            token_usage["completion_tokens"] += 5
            token_usage["total_tokens"] += 5

        # Ajustes baseados no passo da conversa
        if step != "START":
            token_usage["prompt_tokens"] += 15  # Contexto maior em conversas contínuas
            token_usage["total_tokens"] += 15
            
        history = context.get("history", [])
        history.append({
            "user_message": user_message,
            "ia_response": selected_response["user_response"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "intent": main_intent
        })
        
        return {
            "useful_context": {
                "user_response": selected_response["user_response"],
                "user_last_message": user_message,
                "system_response": selected_response["system_response"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sentiment": sentiment,
                "main_intent": main_intent,
                "history": history,
                "intents": context.get("intents", [main_intent]),
                "token_usage": token_usage
            },
            "status": 200,
        }

    except Exception as e:
        logging.error(f"[FAKE IA] Erro ao gerar resposta fake: {str(e)}")
        return {
            "useful_context": {
                "user_response": "Houve um problema. Pode repetir?",
                "system_response": {"function": "no_action"},
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "token_usage": {
                    "prompt_tokens": 30,
                    "completion_tokens": 10,
                    "total_tokens": 40
                }
            },
            "status": 200,
        }