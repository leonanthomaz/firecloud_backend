# app/api/gemini_api.py (Gemini)
import logging
from app.configuration.settings import Configuration
import google.generativeai as genai

config = Configuration()

class GeminiProvider:
    def __init__(self):
        self.max_response_length = 500
        self.model = "gemini-2.0-flash"
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        self.api_key = config.gemini_api_key
        genai.configure(api_key=self.api_key)
        logging.info(f"Inicializado Gemini Provider com modelo {self.model}")
