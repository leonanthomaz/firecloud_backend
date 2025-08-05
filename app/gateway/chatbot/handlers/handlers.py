# app/handlers/handlers.py

from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, Optional
from app.configuration.settings import Configuration
from fastapi import HTTPException

Configuration()

# Função que 
async def call_fallback( 
                        context: Dict[str, Any],
                        error: Optional[Exception] = None,
                        reason: Optional[str] = None,
                        origin: Optional[str] = None) -> Dict[str, Any]:
    """Padroniza todas as chamadas ao handle_fallback com logs detalhados"""
    log_context = {
        "origin": origin,
        "error": str(error) if error else None,
        "reason": reason,
        "context_keys": list(context.keys())
    }
    
    logging.warning(f"DEEPSEEK >>> Acionando fallback. Contexto: {json.dumps(log_context, indent=2)}")
    
    fallback_response = await handle_fallback(
        error=error,
        reason=reason or getattr(error, 'detail', None)
    )
    
    logging.debug(f"DEEPSEEK >>> Resposta do fallback: {json.dumps(fallback_response, indent=2)}")
    return {"useful_context": fallback_response}

def determine_error_reason(error: Optional[Exception], reason: Optional[str]) -> str:
    """Classifica o tipo de erro ocorrido"""
    if reason:
        return reason.lower()
    if isinstance(error, HTTPException):
        pass
    return "internal_error"

# HANDLERS
async def handle_fallback(error: Optional[Exception] = None, reason: Optional[str] = None) -> dict:
    error_map = {
        "unknown_action": "Não entendi o que deseja fazer. Poderia reformular?",
        "incomplete_message": "Poderia passar mais detalhes para que eu possa ajudar?",
        "incomprehensible_message": "Não consegui entender. Poderia dizer de outra forma?",
        "no_schedule": "Desculpe, estamos sem agendamentos marcados.",
        "no_schedule_slots": "Desculpe, não encontrei agendamentos disponíveis.",
        "internal_error": "Ocorreu um erro interno. Já estamos verificando!",
        "human_unavailable": "Irei transferir para um atendente humano. Só um instante...",
        "chatbot_unavailable": "Lamento! O chatbot está indisponível no momento. Por favor, tente novamente mais tarde.",
        "limit_reached": "Desculpe, mas atingimos o limite de interações. Por favor, tente novamente mais tarde.",
        "abusive_interaction": "Desculpe, mas não podemos aceitar esse tipo de linguagem. Vamos manter o respeito, ok?",
    }

    error_reason = determine_error_reason(error, reason)

    return {
        "useful_context": {
            "user_response": error_map.get(error_reason, "Ocorreu um erro"),
            "system_response": None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "function": "handle_fallback",
                "reason": error_reason,
                "error_details": str(error) if error else None
            },
            "token_usage": 0
        },
        "status": 401 if error_reason == "abusive_interaction" else 500,
        "chat_code": None
    }


async def handle_action_response(response: Dict, context: Dict) -> Dict:
    """Processamento de ações com validação alinhada às instruções"""
    try:
        system_response = response.get("system_response", {})

        # Verificação básica
        if not isinstance(system_response, dict):
            raise ValueError("System response deve ser um dicionário")

        function_name = system_response.get("function", "no_action")

        # --- SHOW SERVICE ---
        if function_name == "show_service":
            service = system_response.get("service")
            services = system_response.get("services")

            # Conflito: não pode vir os dois juntos
            if service and services:
                raise ValueError("Resposta ambígua: veio 'service' e 'services' ao mesmo tempo")

            # Se vier um único serviço (mantém 'service' conforme instruções)
            if service:
                # Garante que seja dict
                if not isinstance(service, dict):
                    raise ValueError("'service' deve ser um objeto")
                # Remove services se a IA mandou por engano
                system_response.pop("services", None)

            # Se vier lista de serviços
            elif services:
                # Se a IA mandou categorias, achata
                if any("category_name" in s for s in services):
                    flat_services = []
                    for category in services:
                        flat_services.extend(category.get("services", []))
                    system_response["services"] = flat_services
                # Se não for categorias, mantém como veio
                elif not all(isinstance(s, dict) for s in services):
                    raise ValueError("'services' deve ser uma lista de objetos")

                # Remove 'service' se vier por engano
                system_response.pop("service", None)

            # Se nada veio, usa contexto
            else:
                context_services = context.get("data", {}).get("services", [])
                if context_services:
                    # Achata se tiver categorias no contexto
                    flat_services = []
                    for category in context_services:
                        flat_services.extend(category.get("services", []))
                    system_response["services"] = flat_services

        # --- SCHEDULE ---
        elif function_name == "schedule":
            if "schedule" not in system_response:
                system_response["schedule"] = context.get("data", {}).get("schedule", {})

        # --- SCHEDULE SLOTS ---
        elif function_name == "schedule_slots":
            if not system_response.get("schedule_slots"):
                # Garante no máximo 3 slots (instruções)
                all_slots = context.get("data", {}).get("schedule_slots", [])
                system_response["schedule_slots"] = all_slots[:3]

        # --- NO ACTION ---
        elif function_name == "no_action":
            # Limpa qualquer lixo
            system_response = {"function": "no_action"}

        return {
            "type": "action",
            "useful_context": {
                **context,
                "user_response": response.get("user_response", ""),
                "system_response": system_response,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "metadata": {
                    "function": function_name,
                    "intent": context.get("main_intent", "unknown")
                }
            }
        }

    except Exception as e:
        logging.error(f"Erro ao processar resposta de ação: {str(e)}", exc_info=True)
        return await call_fallback(
            context=context,
            error=e,
            origin="action_processing_error"
        )


async def handle_interaction_response(response: Dict, context: Dict) -> Dict:
    """Processamento de interações normais"""
    logging.info(f"DEEPSEEK >>> Processando interação do tipo: {context.get('main_intent', 'unknown')}")

    # 1. Tenta pegar o system_response direto da IA
    system_response = response.get("system_response")
            
    # 2. Fallback final se nada foi definido
    if not system_response:
        system_response = {
            "function": "no_action"
        }

    return {
        "type": "interaction",
        "useful_context": {
            **context,
            "user_response": response.get("user_response", ""),
            "system_response": system_response,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "function": system_response.get("function", "interaction"),
                "intent": context.get("main_intent", "unknown")
            }
        }
    }
