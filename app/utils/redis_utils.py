# app/utils/redis_utils.py

from app.configuration.settings import Configuration
import logging
from redis.exceptions import RedisError

class RedisCache:
    def __init__(self):
        self.config = Configuration()
        self.redis_client = self.config.get_redis_client()

    def get_cached_response(self, message: str):
        try:
            cached_response = self.redis_client.get(message)

            if cached_response:
                logging.info("Resposta retornada do cache do Redis.")
                return cached_response.decode("utf-8") if isinstance(cached_response, bytes) else cached_response
            return None

        except RedisError as e:
            logging.error(f"Erro ao tentar acessar o Redis: {e}")
            return None

    def cache_response(self, message: str, response: str, expiration: int = 3600):
        try:
            self.redis_client.setex(message, expiration, response)
            logging.info("Resposta armazenada no cache do Redis.")

        except RedisError as e:
            logging.error(f"Erro ao tentar armazenar no Redis: {e}")
