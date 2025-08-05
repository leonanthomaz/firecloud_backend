# app/api/deepseek_api.py (DeepSeek)
from datetime import datetime, timezone
import json
import logging
import requests
from typing import Dict, Any

from app.configuration.settings import Configuration
from app.gateway.chatbot.handlers.handlers import handle_interaction_response, handle_action_response, call_fallback

config = Configuration()

class DeepSeekProvider:
    def __init__(self):
        self.max_response_length = 1000
        self.api_url = config.deepseek_url
        self.model = config.deepseek_model
        self.api_key = config.deepseek_api_key
        
        logging.info(f"IA >>> Inicializado DeepSeek Provider com modelo {self.model}")

    async def generate_response(self, context: Dict[str, Any]) -> Dict[str, Any]:
        logging.info("IA >>> Iniciando geração de resposta...")

        try:
            # Valida contexto inicial
            context = self._validate_context(context)

            # Monta prompt pro modelo
            prompt = self._build_prompt(context)
            logging.debug(f"Prompt: {json.dumps(prompt, indent=2, ensure_ascii=False)}")

            # Chamada ao modelo DeepSeek
            api_result = self._call_api(prompt)
            raw_response = api_result["response"]
            token_usage = api_result.get("usage", {})
            logging.info(f"IA >>> Resposta Bruta: {raw_response}")
            logging.info(f"TOKENS USADOS >>> Prompt: {token_usage.get('prompt_tokens', 0)}, Completion: {token_usage.get('completion_tokens', 0)}, Total: {token_usage.get('total_tokens', 0)}")

            # Verifica resposta vazia ou inválida
            if not raw_response or not raw_response.get('choices'):
                return await call_fallback(
                    context=context,
                    error=ValueError("Resposta da IA vazia ou inválida"),
                    origin="empty_api_response"
                )

            # Processa e formata a resposta
            formatted = await self._format_response(raw_response, context)
            logging.info(f"IA >>> Resposta Formatada: {formatted}")
            
            # Gera resposta final normalizada
            formatted["token_usage"] = token_usage
            final_response = self._send_response(formatted)
            final_response["token_usage"] = token_usage

            logging.info("IA >>> Resposta gerada com sucesso")
            return final_response

        except Exception as e:
            logging.error(f"Erro ao gerar resposta: {str(e)}", exc_info=True)
            return await call_fallback(
                context=context,
                error=e,
                origin="generate_response_error"
            )
            
    def _validate_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Valida os campos essenciais, mas permite que alguns sejam opcionais"""

        # Campos obrigatórios no topo (ex: user_message e data)
        if "user_message" not in context:
            raise ValueError("Campo obrigatório faltando: user_message")
        if "data" not in context:
            raise ValueError("Campo obrigatório faltando: data")

        data = context["data"]

        if not isinstance(data, dict):
            raise ValueError("'data' deve ser um dicionário")

        if "assistant" not in data:
            raise ValueError("Campo obrigatório faltando: assistant")

        # Campos dentro de data que são opcionais 
        optional_fields = ["company", "services", "schedule", "schedule_slots"]

        for field in optional_fields:
            if field not in data or data[field] is None:
                data[field] = {} 

        return context

    def _build_prompt(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Construção do prompt simplificado"""
        essential_context = {
            "user_message": context["user_message"],
            "step": context["step"],
            "history": context["history"],
            "company": context["data"]["company"],
            "assistant": context["data"]["assistant"],
            "services": context["data"]["services"],
            "schedule": context["data"]["schedule"],
            "schedule_slots": context["data"]["schedule_slots"],
        }

        instructions = "\n".join([
            "INSTRUÇÕES:",
            "- Responda APENAS com JSON válido (sem markdown, texto fora de {}).",
            f"- Você é {context['data']['assistant']['name']} ({context['data']['assistant']['type']}) da empresa {context['data']['company']['name']}.",
            "- Use SOMENTE os dados do contexto (company, assistant, services, schedule, schedule_slots). Não invente.",
            "- Considere detalhes do cliente e mensagens anteriores (history) para coerência.",

            "SERVIÇOS:",
            "- Dados: services[].category_name, services[].services[].(name, description, price, duration, rating, availability).",
            "- 1 serviço → system_response.service (objeto).",
            "- Vários → system_response.services (array).",
            "- NUNCA mude preço/duração.",

            "AGENDAMENTOS:",
            "- Copie schedule_slots como system_response.schedule_slots (array).",
            "- 1 agendamento → system_response.schedule.",
            "- Vários → system_response.schedules.",
            "- Nenhum dado → system_response: { 'function': 'no_action' }.",

            "RESPOSTA:",
            "- Seja clara logo na primeira mensagem.",
            "- Mostrou serviço/agendamento → inclua 'function': 'show_service', 'schedule_slots' ou 'schedule'.",
            "- Só mencionou → NÃO inclua 'function'.",
            "- Nada a fazer → function: 'no_action'.",

            "ERROS:",
            "- Dados faltando → 'incomplete_data'",
            "- Erro interno → 'internal_error'",
            "- Desconhecido → 'unknown_action'",
            "- Mensagem incompleta → 'incomplete_message'",
            "- Incompreensível → 'incomprehensible_message'",
            "- Sem agendamentos → 'no_schedule'",
            "- Sem horários → 'no_schedule_slots'",
            "- Humano indisponível → 'human_unavailable'",
            "- Chatbot indisponível → 'chatbot_unavailable'",
            "- Limite atingido → 'limit_reached'",
            "- Abusivo → 'abusive_interaction'",

            "FORMATO:",
            "- JSON começa com { e termina com }, sem explicações.",
            "- Ex. serviço único: { 'user_response': '...', 'system_response': { 'function': 'show_service', 'service': {...} } }",
            "- Ex. múltiplos serviços: { 'user_response': '...', 'system_response': { 'function': 'show_service', 'services': [...] } }",
            "- Ex. múltiplos agendamentos: { 'user_response': '...', 'system_response': { 'function': 'schedule', 'schedules': [...] } }",
            "- Ex. horários disponíveis (máx 3): { 'user_response': '...', 'system_response': { 'function': 'schedule_slots', 'schedule_slots': [...] } }",
        ])

        prompt = {
            "context": essential_context,
            "instructions": instructions
        }
        
        logging.debug(f"Prompt construído com {len(instructions)} caracteres de instrução")
        return prompt

    def _call_api(self, prompt_data: Dict[str, Any]) -> Any:
        """Chamada à API com URL correta"""
        # Construa a URL corretamente
        api_url = f"{self.api_url.rstrip('/')}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "FireCloud Chatbot"
        }

        messages = [
            {
                "role": "system",
                "content": prompt_data["instructions"]
            },
            {
                "role": "user",
                "content": json.dumps({
                    "user_message": prompt_data["context"]["user_message"],
                    "context": prompt_data["context"]
                }, ensure_ascii=False)
            }
        ]

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.5,
            "max_tokens": self.max_response_length,
            "response_format": {"type": "json_object"}
        }

        try:
            logging.info(f"Chamando API em: {api_url}")
            response = requests.post(api_url, headers=headers, json=data, timeout=15)
            
            # DEBUG - Essencial para troubleshooting
            logging.debug(f"Status Code: {response.status_code}")
            logging.debug(f"Response Text: {response.text}")
            
            response.raise_for_status()
            json_response = response.json()

            # Captura os tokens se disponíveis
            token_usage = json_response.get("usage", {})

            return {
                "response": json_response,
                "usage": token_usage
            }
                
        except Exception as e:
            logging.error(f"Falha na chamada API: {str(e)}")
            return None
        except requests.Timeout:
            logging.error("Timeout na requisição à API da IA")
            raise TimeoutError("A IA demorou demais para responder")
    
    async def _format_response(self, api_response: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """Formatação básica da resposta"""
        try:
            raw_text = api_response["choices"][0]["message"]["content"]
            logging.debug(f"Resposta bruta da IA: {raw_text[:200]}...")
            
            clean_content = self._sanitize_response(raw_text)
            response = json.loads(clean_content)
            
            if "user_response" not in response:
                error_msg = "Resposta da IA incompleta - falta 'user_response'"
                logging.error(error_msg)
                return await call_fallback(
                    context=context,
                    error=ValueError(error_msg),
                    origin="incomplete_ai_response"
                )
            
            function = response.get("system_response", {}).get("function")
            if function:
                return await handle_action_response(response, context)
                
            return await handle_interaction_response(response, context)

        except json.JSONDecodeError as e:
            logging.error(f"Erro ao decodificar JSON da IA: {str(e)}")
            return await call_fallback(
                context=context,
                error=e,
                origin="invalid_ai_json"
            )
        except Exception as e:
            logging.error(f"Erro ao formatar resposta: {str(e)}", exc_info=True)
            return await call_fallback(
                context=context,
                error=e,
                origin="format_response_error"
            )

    def _sanitize_response(self, raw_content: str) -> str:
        """Limpeza básica da resposta"""
        raw_content = raw_content.strip()
        
        # Remove markdown se existir
        for delim in ['```json', '```', "'''json", "'''"]:
            raw_content = raw_content.replace(delim, '')
            
        return raw_content.strip()

    def _send_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Preparação da resposta final"""
        useful_context = response.get("useful_context", {})
        token_usage = response.get("token_usage", {})
        
        return {
            "useful_context": {
                "user_response": useful_context.get("user_response", ""),
                "user_message": useful_context.get("user_message", ""),
                "system_response": useful_context.get("system_response", {}),
                "token_usage": token_usage,
                "timestamp": datetime.now(timezone.utc).isoformat()
            },
            "status": 200
        }