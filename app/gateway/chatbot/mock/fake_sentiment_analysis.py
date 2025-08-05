
# Falso generate_response sem IA
from app.enums.chat import ChatSentiment

def fake_sentiment_analysis(text: str) -> str | None:
    text = text.lower()
    negativos = ["não", "nunca", "péssimo", "ruim", "triste", "odiar", "reclamar", "chateado", "problema"]
    positivos = ["bom", "legal", "ótimo", "maravilha", "adoro", "obrigado", "valeu", "parabéns"]

    if any(p in text for p in positivos):
        return ChatSentiment.POSITIVE
    if any(n in text for n in negativos):
        return ChatSentiment.NEGATIVE
    return None