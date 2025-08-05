from typing import Dict, Any, Set
from app.enums.chat import ChatIntent
from app.gateway.chatbot.nlp.profanity_level import ProfanityClassifier


class ContextFilter:
    def __init__(self):
        self.profanity_classifier = ProfanityClassifier()

        # Grupos de intenções por comportamento
        self.no_context_intents: Set[ChatIntent] = {
            ChatIntent.CLOSE_CHAT,
            ChatIntent.ABUSIVE,
            ChatIntent.START,
            ChatIntent.RESTART,
            ChatIntent.GERAL,
        }

        self.basic_info_intents: Set[ChatIntent] = {
            ChatIntent.COMPANY_INFO,
            ChatIntent.LOCATION,
            ChatIntent.OPENING_HOURS,
            ChatIntent.PROMOTION,
            ChatIntent.WELCOME,
        }

        self.sensitive_intents: Set[ChatIntent] = {
            ChatIntent.ABUSIVE,
            ChatIntent.COMPLAINT,
            ChatIntent.TRANSFER_HUMAN,
        }
        
    def filter_context_by_intent(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Filtra o contexto com prioridade para mensagens abusivas e intenções sensíveis"""

        message = context.get("user_message", "")
        profanity_result = self._check_profanity(message)

        # Força intenção ABUSIVE se detectado palavrão severo
        if profanity_result["level"] in ["SEVERE", "HATE_SPEECH"] and profanity_result["contains_profanity"]:
            context["main_intent"] = ChatIntent.ABUSIVE
            context["intents"] = [ChatIntent.ABUSIVE]
            context["step"] = "handle_abuse"
            context["sanitized_message"] = "[mensagem removida por violação dos termos]"
            context["profanity_analysis"] = profanity_result

        main_intent_str = context.get("main_intent", ChatIntent.GERAL)
        main_intent = ChatIntent[main_intent_str]
        

        # **Valida se o 'assistant' existe no contexto e é dict, se não, erro explícito**
        data = context.get("data", {})
        assistant = data.get("assistant")
        if not assistant or not isinstance(assistant, dict):
            raise ValueError("Contexto inválido: 'assistant' é obrigatório e deve ser um dict")

        # 1. Mensagens abusivas
        if main_intent == ChatIntent.ABUSIVE:
            return self._handle_abusive_context(context, profanity_result)

        # 2. Intenções sensíveis (reclamação, transferência)
        if main_intent in self.sensitive_intents:
            return self._handle_sensitive_context(context)

        # 3. Intenções que não exigem contexto
        if main_intent in self.no_context_intents:
            return {
                "user_message": message,
                "intents": context.get("intents", []),
                "main_intent": main_intent,
                "step": context.get("step"),
                "assistant": assistant,
                "profanity_analysis": profanity_result if main_intent == ChatIntent.ABUSIVE else None,
            }

        # 4. Intenções com dados básicos apenas
        if main_intent in self.basic_info_intents:
            company = data.get("company", {})
            return {
                **context,
                "data": {
                    "company": company,
                    "assistant": assistant,
                },
                "profanity_analysis": None,
            }

        # 5. Padrão: retorna contexto completo
        return {
            **context,
            "profanity_analysis": None,
        }

    def _check_profanity(self, message: str) -> Dict[str, Any]:
        """Classifica a mensagem quanto a palavrões"""
        result = self.profanity_classifier.classify_profanity(message)
        return {
            "contains_profanity": result["contains_profanity"],
            "level": result["level"] if result["level"] else None,
            "words_found": result["words"],
            "sanitized_message": result["sanitized_message"],
        }

    def _handle_abusive_context(
        self, context: Dict[str, Any], profanity_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Tratamento especial para mensagens abusivas"""
        return {
            "user_message": profanity_result["sanitized_message"],
            "original_message": context["user_message"],
            "intents": [ChatIntent.ABUSIVE],
            "main_intent": ChatIntent.ABUSIVE,
            "step": "handle_abuse",
            # "assistant": context["data"]["assistant"],
            # "data": context["data"],
            "profanity_analysis": profanity_result,
            "requires_human": profanity_result["level"] in ["SEVERE", "HATE_SPEECH"],
        }

    def _handle_sensitive_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Tratamento para intenções sensíveis (reclamações, transferências)"""
        main_intent = ChatIntent[context["main_intent"]]
        base_context = {
            "user_message": context["user_message"],
            "intents": context["intents"],
            "main_intent": main_intent,
            "step": context["step"],
            "assistant": context["data"]["assistant"],
            "company": context["data"]["company"],
        }

        if main_intent == ChatIntent.COMPLAINT:
            base_context["service_info"] = context["data"].get("services")
            base_context["order_info"] = context["data"].get("schedule")

        return base_context
