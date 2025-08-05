import logging
from app.configuration.settings import Configuration

config = Configuration()

class OpenaiProvider:
    def __init__(self):
        self.max_response_length = 500
        self.model = "gpt-3.5-turbo"
        self.api_url = "https://api.openai.com/v1/chat/completions"
        self.api_key = config.openassistant_api_key
        logging.info(f"CHAVE: {self.api_key} == URL: {self.api_url}")
