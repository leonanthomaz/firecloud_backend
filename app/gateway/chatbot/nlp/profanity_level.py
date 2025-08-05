import re
from typing import Dict
from enum import Enum

class ProfanityLevel(Enum):
    MILD = 1       # Palavras leves, socialmente aceitas em alguns contextos
    MODERATE = 2    # Palavras mais fortes, geralmente inapropriadas
    SEVERE = 3      # Palavras muito ofensivas
    HATE_SPEECH = 4 # Discurso de ódio ou extremamente ofensivo

class ProfanityClassifier:
    def __init__(self):
        self.profanity_words: Dict[str, ProfanityLevel] = {
            
            # Nível leve (socialmente aceito em alguns contextos)
            "droga": ProfanityLevel.MILD,
            "putz": ProfanityLevel.MILD,
            "cacete": ProfanityLevel.MILD,

            # Nível moderado (palavrões comuns, mas ofensivos)
            "porra": ProfanityLevel.MODERATE,
            "merda": ProfanityLevel.MODERATE,
            "caralho": ProfanityLevel.MODERATE,
            "bosta": ProfanityLevel.MODERATE,
            "foda": ProfanityLevel.MODERATE,
            "pau": ProfanityLevel.MODERATE,
            "leitar": ProfanityLevel.MODERATE,
            "babaca": ProfanityLevel.MODERATE,
            "otário": ProfanityLevel.MODERATE,
            "otária": ProfanityLevel.MODERATE,

            # Nível severo (ofensivo de forma direta, sexual ou depreciativa)
            "cu": ProfanityLevel.SEVERE,
            "cuzinho": ProfanityLevel.SEVERE,
            "buceta": ProfanityLevel.SEVERE,
            "xereca": ProfanityLevel.SEVERE,
            "xerecão": ProfanityLevel.SEVERE,
            "xerequinha": ProfanityLevel.SEVERE,
            "piroca": ProfanityLevel.SEVERE,
            "puta": ProfanityLevel.SEVERE,
            "vadia": ProfanityLevel.SEVERE,
            "foder": ProfanityLevel.SEVERE,
            "piranha": ProfanityLevel.SEVERE,
            "prostituta": ProfanityLevel.SEVERE,
            

            # Discurso de ódio (ataque direto a grupos ou insultos graves)
            "viado": ProfanityLevel.HATE_SPEECH,
            "retardado": ProfanityLevel.HATE_SPEECH,
            "bicha": ProfanityLevel.HATE_SPEECH,
            "sapatão": ProfanityLevel.HATE_SPEECH,  # quando usado de forma pejorativa
        }


        self.profanity_phrases: Dict[str, ProfanityLevel] = {
            "vai se foder": ProfanityLevel.SEVERE,
            "vai se fuder": ProfanityLevel.SEVERE,
            "vai tomar no cu": ProfanityLevel.SEVERE,
            "vai te tomar no cu": ProfanityLevel.SEVERE,
            "olho do cu": ProfanityLevel.SEVERE,
            "olho do seu cu": ProfanityLevel.SEVERE,
            "filho da puta": ProfanityLevel.SEVERE,
            "filha da puta": ProfanityLevel.SEVERE,
            "seu cu": ProfanityLevel.SEVERE,
            "que merda": ProfanityLevel.MILD,
            "que porra": ProfanityLevel.MODERATE,
            "me fudi": ProfanityLevel.MODERATE,
            "que bosta": ProfanityLevel.MODERATE,
            "arrombado": ProfanityLevel.SEVERE,
            "escroto": ProfanityLevel.MODERATE,
            "pau no cu": ProfanityLevel.SEVERE,
            "foda-se": ProfanityLevel.SEVERE,
        }

        self.word_variations = {
            "porra": ["porr", "porraa", "porraaa"],
            "caralho": ["carai", "caralhoo", "karalho"],
            "foder": ["fuder", "fodê", "fudê"],
            "puta": ["putinha", "putão"],
            "merda": ["merd", "merdaa"]
        }

    def classify_profanity(self, message: str) -> Dict[str, any]:
        """
        Analisa a mensagem e retorna um dicionário com:
        - contains_profanity: bool
        - level: ProfanityLevel (o nível mais alto encontrado)
        - words: lista de palavras ofensivas encontradas
        - sanitized_message: mensagem com palavrões substituídos
        """
        message_lower = self._normalize_message(message.lower())
        results = {
            "contains_profanity": False,
            "level": None,
            "words": [],
            "sanitized_message": message
        }

        # Verifica palavras individuais
        for word, level in self.profanity_words.items():
            if self._contains_word(message_lower, word):
                results["contains_profanity"] = True
                results["words"].append(word)
                if results["level"] is None or level.value > results["level"].value:
                    results["level"] = level

        # Verifica frases completas
        for phrase, level in self.profanity_phrases.items():
            if phrase in message_lower:
                results["contains_profanity"] = True
                results["words"].append(phrase)
                if results["level"] is None or level.value > results["level"].value:
                    results["level"] = level

        # Sanitiza a mensagem se necessário
        if results["contains_profanity"]:
            results["sanitized_message"] = self._sanitize_message(message)

        return results

    def _contains_word(self, message: str, word: str) -> bool:
        """
        Verifica se a palavra está presente respeitando bordas de palavras
        e variações conhecidas
        """
        # 1. Verifica correspondência exata usando bordas de palavras
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, message):
            return True

        # 2. Verifica variações comuns (se aplicável)
        variations = self.word_variations.get(word, [])
        for variation in variations:
            pattern_var = r'\b' + re.escape(variation) + r'\b'
            if re.search(pattern_var, message):
                return True

        return False

    def _normalize_message(self, message: str) -> str:
        """Normaliza a mensagem para melhor análise"""
        replacements = {
            "4": "a", "@": "a", "3": "e", "1": "i", "0": "o",
            "5": "s", "7": "t", "!": "i", "+": "t"
        }
        for char, replacement in replacements.items():
            message = message.replace(char, replacement)
        return message

    def _sanitize_message(self, message: str) -> str:
        """Substitui palavrões por asteriscos"""
        words_to_replace = set()
        
        # Adiciona palavras individuais
        for word in self.profanity_words:
            if self._contains_word(message.lower(), word):
                words_to_replace.add(word)
        
        # Adiciona frases
        for phrase in self.profanity_phrases:
            if phrase in message.lower():
                words_to_replace.add(phrase)
        
        # Substitui na mensagem original (mantendo capitalização)
        sanitized = message
        for profanity in words_to_replace:
            sanitized = self._replace_profanity(sanitized, profanity)
        
        return sanitized

    def _replace_profanity(self, text: str, profanity: str) -> str:
        """Substitui uma palavra/frase ofensiva por asteriscos"""
        parts = text.split(profanity)
        replacement = '*' * len(profanity)
        return replacement.join(parts)
