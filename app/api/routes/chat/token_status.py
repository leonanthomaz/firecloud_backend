import os
from app.configuration.settings import Configuration
from app.enums.token_status import Provider
import httpx
import logging
from fastapi import APIRouter, HTTPException, status

configuration = Configuration()

class TokenStatusRouter(APIRouter):
    """
    Roteador para verificar o status dos tokens de provedores de IA.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.openassistant_api_key = os.environ.get("OPENassistant_api_key")
        self.deepseek_api_key = os.environ.get("DEEPSEEK_API_KEY")
        self.add_api_route("/check_token_status/{provider}", self.check_token_status, methods=["GET"])

    async def check_openai_status(self, api_key: str) -> dict:
        url = "https://openrouter.ai/api/v1/auth/key" 
        headers = {"Authorization": f"Bearer {api_key}"}
        try:
            logging.info("Fazendo requisição para o OpenAI")
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
            data = response.json()
            key_info = data.get("data", {})
            logging.info(f"Status da resposta do OpenAI: {response.status_code}")
            logging.info(f"Créditos usados: {key_info.get('usage')}, Limite de créditos: {key_info.get('limit')}")
            logging.info(f"Rate Limit Requests: {key_info['rate_limit']['requests']}, Intervalo: {key_info['rate_limit']['interval']}")
            return {
                "provider": "OpenAI",
                "label": key_info.get("label"),
                "credits_used": key_info.get("usage"),
                "credit_limit": key_info.get("limit"),
                "is_free_tier": key_info.get("is_free_tier"),
                "rate_limit_requests": key_info["rate_limit"]["requests"],
                "rate_limit_interval": key_info["rate_limit"]["interval"],
            }
        except httpx.HTTPStatusError as e:
            logging.error(f"Erro ao acessar OpenAI: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Erro ao acessar OpenAI: {e}")
        except httpx.RequestError as e:
            logging.error(f"Erro ao acessar OpenAI: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao acessar OpenAI: {e}")

    async def check_deepseek_status(self, api_key: str) -> dict:
        url = "https://openrouter.ai/api/v1/auth/key" 
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            logging.info("Fazendo requisição para o OpenRouter (DeepSeek via OpenRouter)")
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
            data = response.json()
            key_info = data.get("data", {})
            return {
                "provider": "DeepSeek",
                "credits_used": key_info.get("usage"),
                "credit_limit": key_info.get("limit"),
                "is_free_tier": key_info.get("is_free_tier"),
                "rate_limit_requests": key_info["rate_limit"]["requests"],
                "rate_limit_interval": key_info["rate_limit"]["interval"],
            }
        except httpx.HTTPStatusError as e:
            logging.error(f"Erro ao acessar DeepSeek: {e}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Erro ao acessar DeepSeek: {e}")
        except httpx.RequestError as e:
            logging.error(f"Erro ao acessar DeepSeek: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao acessar DeepSeek: {e}")

    async def check_token_status(self, provider: Provider):
        logging.info(f"Verificando status do token para o provedor: {provider}")
        if provider == Provider.OPENAI and self.openassistant_api_key:
            return await self.check_openai_status(self.openassistant_api_key)
        elif provider == Provider.DEEPSEEK and self.deepseek_api_key:
            return await self.check_deepseek_status(self.deepseek_api_key)
        else:
            logging.error("Provedor inválido ou chave não configurada corretamente.")
            raise HTTPException(status_code=status.HTTP_BAD_REQUEST, detail="Provedor inválido ou chave não configurada corretamente.")
