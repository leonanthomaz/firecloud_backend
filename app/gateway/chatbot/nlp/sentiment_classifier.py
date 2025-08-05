from typing import Optional, Dict, List, Tuple
from app.enums.chat import ChatSentiment
import re
import emoji
from textblob import TextBlob

class SentimentClassifier:
    def __init__(self):
        # Conjuntos expandidos de palavras com nuances emocionais
        self.positive_words = {
            # Gratidão
            "obrigado", "obrigada", "grato", "grata", "agradecido", "agradecida", 
            "muito obrigado", "muito obrigada", "agradeço", "valeu", "brigado", "brigada",
            
            # Entusiasmo
            "excelente", "incrível", "fantástico", "fantástica", "maravilhoso", "maravilhosa",
            "espetacular", "sensacional", "impressionante", "perfeito", "perfeita", "show", 
            "demais", "top", "top demais", "irado", "irrado", "foda", "foda-se", "animal",
            "arrochado", "brabo", "brabíssimo", "show de bola", "fenomenal", "único", "única",
            
            # Satisfação
            "ótimo", "ótima", "bom", "boa", "gostei", "adoro", "amei", "apaixonado", "apaixonada",
            "satisfeito", "satisfeita", "feliz", "contente", "radiante", "eufórico", "eufórica",
            
            # Alívio
            "ufa", "ufa", "alívio", "finalmente", "graças a deus", "deus me livre",
            
            # Afeto
            "amor", "amo", "lindo", "linda", "querido", "querida", "fofo", "fofa", "adorável",
            "especial", "querer", "beijo", "abraço", "carinho", "xodó", "paixão",
            
            # Elogios
            "parabéns", "congratulações", "sucesso", "nota 10", "nota mil", "campeão", "campeã",
            "gênio", "gênia", "inteligente", "sábio", "sábia", "competente", "eficiente",
            
            # Concordância
            "concordo", "exatamente", "isso", "verdade", "realmente", "certíssimo", "certíssima",
            "claro", "sim", "com certeza", "sem dúvida", "óbvio", "lógico",
            
            # Surpresa positiva
            "uau", "nossa", "caramba", "caraca", "eita", "nossinho", "minha nossa",
        }

        self.negative_words = {
            # Raiva/Frustração
            "ruim", "péssimo", "péssima", "horrível", "terrível", "odeio", "detesto", "nojento",
            "nojinho", "asco", "repugnante", "vergonha", "vergonhoso", "vergonhosa", "ridículo",
            "ridícula", "inaceitável", "intolerável", "escroto", "escrota", "porcaria", "lixo",
            "merda", "bosta", "droga", "caralho", "desgraça", "inferno", "puta", "porra",
            
            # Tristeza/Decepção
            "decepcionado", "decepcionada", "triste", "chateado", "chateada", "frustrado", 
            "frustrada", "desanimado", "desanimada", "deprimido", "deprimida", "desesperado",
            "desesperada", "desolado", "desolada", "desapontado", "desapontada", "choro", 
            "chorando", "sofrendo", "angustiado", "angustiada", "machucado", "machucada",
            
            # Medo/Ansiedade
            "medo", "assustado", "assustada", "apavorado", "apavorada", "preocupado", 
            "preocupada", "nervoso", "nervosa", "ansioso", "ansiosa", "pânico", "desespero",
            "terror", "horror", "pesadelo", "trauma", "traumático", "traumática",
            
            # Insatisfação
            "insatisfeito", "insatisfeita", "reclamo", "reclamação", "problema", "defeito",
            "falha", "erro", "atraso", "lento", "lenta", "demorado", "demorada", "preguiça",
            "cansado", "cansada", "exausto", "exausta", "esgotado", "esgotada",
            
            # Discordância
            "discordo", "errado", "errada", "mentira", "falso", "falsa", "não", "nunca", 
            "jamais", "negativo", "absurdo", "absurda", "injusto", "injusta", "ilegal",
            
            # Desprezo
            "patético", "patética", "fracasso", "burro", "burra", "idiota", "imbecil", 
            "estúpido", "estúpida", "incompetente", "inútil", "inúteis", "mediocre", "porco",
            "porca", "vagabundo", "vagabunda", "canalha", "pilantra",
        }

        # Expressões idiomáticas e gírias regionais
        self.idiomatic_expressions = {
            # Positivas
            "valeu a pena": 2.0,
            "salvou meu dia": 2.5,
            "muito bom": 1.5,
            "top demais": 2.0,
            "show de bola": 2.0,
            "nota mil": 2.0,
            "maravilha": 1.5,
            "sensação": 1.5,
            "fiquei feliz": 1.8,
            "amei demais": 2.2,
            
            # Negativas
            "perda de tempo": -2.0,
            "péssimo atendimento": -2.5,
            "não recomendo": -2.0,
            "horrível experiência": -2.5,
            "pior coisa": -2.0,
            "odeio isso": -2.5,
            "que ódio": -2.0,
            "tô puto": -2.5,
            "tô puta": -2.5,
            "quero meu dinheiro de volta": -2.5,
        }

        # Emojis e suas valências emocionais
        self.emoji_sentiment = {
            # Positivos
            "😊": 1.5, "😍": 2.0, "😂": 1.5, "🥰": 2.0, "😎": 1.3,
            "🤩": 2.0, "😘": 1.8, "👍": 1.5, "👏": 1.7, "🎉": 1.8,
            "❤️": 2.0, "💖": 2.0, "✨": 1.3, "🙌": 1.7, "😁": 1.6,
            
            # Negativos
            "😡": -2.5, "😠": -2.0, "🤬": -2.8, "😒": -1.5, "😞": -1.8,
            "😢": -2.0, "😭": -2.3, "👎": -2.0, "💔": -2.0, "😤": -2.0,
            "😨": -1.8, "😰": -1.7, "🤢": -2.0, "🤮": -2.3, "💩": -1.8,
        }

        # Intensificadores e atenuadores
        self.intensifiers = {
            "muito": 1.5, "demais": 1.8, "extremamente": 2.0, "totalmente": 1.7,
            "completamente": 1.7, "absolutamente": 1.9, "super": 1.6, "hiper": 1.8,
            "mega": 1.7, "super": 1.6, "tão": 1.5, "tanto": 1.5, "mais": 1.3,
            "super": 1.6, "incrivelmente": 1.9, "ridiculamente": 1.8,
        }

        self.attenuators = {
            "pouco": 0.5, "quase": 0.6, "meio": 0.7, "mais ou menos": 0.5,
            "nem tanto": 0.4, "um pouco": 0.6, "ligeiramente": 0.7, "parcialmente": 0.7,
        }

        # Níveis de pontuação para diferentes categorias
        self.sentiment_weights = {
            'word': 1.0,
            'idiom': 2.0,
            'emoji': 1.5,
            'punctuation': 0.8,
            'capitalization': 0.5,
            'textblob': 2.0
        }

    def _preprocess_message(self, message: str) -> Tuple[str, Dict[str, List[str]]]:
        """Preprocessa a mensagem extraindo elementos relevantes."""
        features = {
            'words': [],
            'emojis': [],
            'idioms': [],
            'punctuation': [],
            'capitalized': []
        }
        
        # Extrai emojis
        emoji_list = [c for c in message if c in emoji.EMOJI_DATA]
        features['emojis'] = emoji_list
        message_no_emoji = emoji.replace_emoji(message, replace='')
        
        # Verifica capitalização excessiva (gritando)
        if sum(1 for c in message_no_emoji if c.isupper()) / len(message_no_emoji) > 0.5:
            features['capitalized'] = ['EXCESSIVE_CAPS']
        
        # Extrai pontuação repetida
        punctuation = re.findall(r'[!?.]{2,}', message_no_emoji)
        features['punctuation'] = punctuation
        
        # Extrai palavras
        words = re.findall(r'\b\w+\b', message_no_emoji.lower())
        features['words'] = words
        
        # Detecta expressões idiomáticas
        detected_idioms = []
        for idiom in self.idiomatic_expressions:
            if idiom in message_no_emoji.lower():
                detected_idioms.append(idiom)
        features['idioms'] = detected_idioms
        
        return message_no_emoji, features

    def _calculate_textblob_sentiment(self, text: str) -> float:
        """Calcula o sentimento usando TextBlob (análise mais sofisticada)."""
        analysis = TextBlob(text)
        # Converter de -1..1 para -2.5..2.5 para ficar compatível com nosso sistema
        return analysis.sentiment.polarity * 2.5

    def _detect_intensifiers(self, words: List[str], index: int) -> float:
        """Detecta intensificadores próximos a palavras de sentimento."""
        intensity = 1.0
        # Verifica palavras anteriores
        for i in range(max(0, index-2), index):
            if words[i] in self.intensifiers:
                intensity *= self.intensifiers[words[i]]
        # Verifica palavras posteriores
        for i in range(index+1, min(index+3, len(words))):
            if words[i] in self.intensifiers:
                intensity *= self.intensifiers[words[i]]
        return intensity

    def _calculate_sentiment_score(self, features: Dict[str, List[str]]) -> float:
        """Calcula uma pontuação de sentimento composta."""
        total_score = 0.0
        
        # Pontuação das palavras
        for i, word in enumerate(features['words']):
            word_score = 0.0
            if word in self.positive_words:
                word_score = 1.0 * self._detect_intensifiers(features['words'], i)
            elif word in self.negative_words:
                word_score = -1.0 * self._detect_intensifiers(features['words'], i)
            
            total_score += word_score * self.sentiment_weights['word']
        
        # Pontuação das expressões idiomáticas
        for idiom in features['idioms']:
            total_score += self.idiomatic_expressions[idiom] * self.sentiment_weights['idiom']
        
        # Pontuação dos emojis
        for emoji_char in features['emojis']:
            if emoji_char in self.emoji_sentiment:
                total_score += self.emoji_sentiment[emoji_char] * self.sentiment_weights['emoji']
        
        # Pontuação da pontuação (repetição de !!! ou ???)
        for punct in features['punctuation']:
            if '!' in punct:
                total_score += -1.5 * self.sentiment_weights['punctuation']
            elif '?' in punct:
                total_score += -0.5 * self.sentiment_weights['punctuation']
        
        # Pontuação de capitalização (gritar)
        if features['capitalized']:
            total_score += -1.0 * self.sentiment_weights['capitalization']
        
        # Adiciona análise do TextBlob
        text = ' '.join(features['words'])
        textblob_score = self._calculate_textblob_sentiment(text)
        total_score += textblob_score * self.sentiment_weights['textblob']
        
        return total_score

    def detect_sentiment(self, message: str) -> Optional[ChatSentiment]:
        """Detecta o sentimento da mensagem com análise multifatorial."""
        if not message or not message.strip():
            return None

        # Pré-processamento e extração de features
        _, features = self._preprocess_message(message)
        
        # Cálculo da pontuação composta
        sentiment_score = self._calculate_sentiment_score(features)
        
        # Limiares para decisão (ajustáveis conforme necessidade)
        if sentiment_score >= 0.8: 
            return ChatSentiment.POSITIVE
        elif sentiment_score <= -0.8:
            return ChatSentiment.NEGATIVE

        
        # Caso esteja no meio, usa análise mais granular
        positive_count = sum(1 for word in features['words'] if word in self.positive_words)
        negative_count = sum(1 for word in features['words'] if word in self.negative_words)
        
        if positive_count > negative_count:
            return ChatSentiment.POSITIVE
        elif negative_count > positive_count:
            return ChatSentiment.NEGATIVE
        
        return ChatSentiment.NEUTRAL

    def get_sentiment_intensity(self, message: str) -> Tuple[Optional[ChatSentiment], float]:
        """Retorna o sentimento e sua intensidade numérica."""
        if not message or not message.strip():
            return None, 0.0

        _, features = self._preprocess_message(message)
        sentiment_score = self._calculate_sentiment_score(features)
        
        if sentiment_score >= 1.5:
            return ChatSentiment.POSITIVE, sentiment_score
        elif sentiment_score <= -1.5:
            return ChatSentiment.NEGATIVE, abs(sentiment_score)
        
        return None, 0.0