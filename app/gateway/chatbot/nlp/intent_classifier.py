from typing import List, Set

from app.enums.chat import ChatIntent
from app.gateway.chatbot.nlp.profanity_level import ProfanityClassifier, ProfanityLevel

class IntentClassifier:
    def __init__(self):
        self.profanity_classifier = ProfanityClassifier()
         # Gatilhos comuns para agendamento (usado por 2 intents)
         
        self.intent_triggers = {
            ChatIntent.WELCOME: {
                'words': {"oi", "olá", "ola", "opa", "eae", "fala", "salve", "bom dia", "boa tarde", "boa noite"},
                'phrases': {"e aí", "fala comigo", "to aqui", "cheguei"}
            },
            ChatIntent.TRANSFER_HUMAN: {
                'words': {"atendente", "humano", "pessoa", "gerente", "alguém", "funcionário"},
                'phrases': {"falar com alguém", "quero ajuda de verdade", "quero falar com gente", "me chama um atendente", "me passa pro humano"}
            },
            ChatIntent.RESTART: {
                'words': {"bot", "robô", "chatbot", "sistema"},
                'phrases': {"atendimento automático", "voltar para o chatbot", "reiniciar conversa", "começar do zero"}
            },
            ChatIntent.COMPANY_INFO: {
                'words': {"endereço", "telefone", "contato", "whatsapp", "funcionamento", "dias úteis", "empresa", "trabalham", "trabalha"},
                'phrases': {"onde fica", "como chegar", "formas de contato", "qual o telefone", "qual o zap", "como funciona", "quais os horários"}
            },
            ChatIntent.SCHEDULE_SLOT_INFO: {
                'words': {"agendar", "marcar", "novo", "disponível", "disponivel"},
                'phrases': {
                    "quero marcar consulta",
                    "tem horário disponível",
                    "agendar nova sessão",
                    "quero marcar um horário"
                }
            },
            ChatIntent.SCHEDULE_INFO: {
                'words': {"agendamentos", "marcados", "meu", "minha", "horário", "consulta"},
                'phrases': {"meu agendamento", "meu horário marcado", "quero ver meus agendamentos"}
            },
            ChatIntent.CANCEL: {
                'words': {"cancelar", "desmarcar", "adiar", "remarcar", "não vou", "não posso"},
                'phrases': {"não posso ir", "não vou conseguir", "quero cancelar", "remarcar minha consulta", "muda meu horário"}
            },
            ChatIntent.PAYMENT: {
                'words': {"pix", "boleto", "pagar", "cartão", "preço", "valor", "custo", "grátis", "pagamento"},
                'phrases': {"quanto custa", "como pago", "tem desconto", "tem parcelamento"}
            },
            ChatIntent.ORDER_STATUS: {
                'words': {"pedido", "status", "andamento", "confirmado", "recebido"},
                'phrases': {"já chegou", "foi aprovado", "confirmaram meu pedido", "status da consulta"}
            },
            ChatIntent.DELIVERY: {
                'words': {"entrega", "frete", "enviar", "transportadora"},
                'phrases': {"quando chega", "já saiu para entrega", "vai entregar", "tem rastreio"}
            },
            ChatIntent.PRODUCT_INFO: {
                'words': {"produto", "item", "mercadoria", "coisa"},
                'phrases': {"fala do produto", "me mostra os produtos", "vende o que", "o que tem pra vender"}
            },
            ChatIntent.SERVICE_INFO: {
                'words': {"serviço", "serviços", "atendimento", "oferta"},
                'phrases': {"que serviços tem", "fala dos atendimentos", "qual o serviço"}
            },
            ChatIntent.LOCATION: {
                'words': {"endereço", "local", "localização", "mapa"},
                'phrases': {"onde é", "onde fica", "como chegar", "tem unidade perto"}
            },
            ChatIntent.OPENING_HOURS: {
                'words': {"horário", "funciona", "abre", "fecha"},
                'phrases': {"que horas abre", "qual horário", "funciona domingo", "até que horas", "horário de funcionamento", "quais horários"}
            },
            ChatIntent.PROMOTION: {
                'words': {"promoção", "desconto", "oferta", "barato", "cupom"},
                'phrases': {"tem desconto", "tá mais barato", "alguma promoção", "tem brinde"}
            },
            ChatIntent.COMPLAINT: {
                'words': {"reclamar", "problema", "ruim", "péssimo", "insuportável"},
                'phrases': {"tô insatisfeito", "isso não funciona", "péssimo atendimento", "vou reclamar no procon"}
            },
            ChatIntent.PRAISE: {
                'words': {"obrigado", "valeu", "bom", "ótimo", "excelente", "top"},
                'phrases': {"curti demais", "ótimo atendimento", "parabéns", "vocês são 10"}
            },
            ChatIntent.DOUBT: {
                'words': {"duvida", "como", "o que", "qual", "quando", "porque", "por que", "onde"},
                'phrases': {"tenho uma dúvida", "não entendi", "me explica", "como funciona"}
            },
            ChatIntent.FEEDBACK: {
                'words': {"feedback", "avaliação", "opinião"},
                'phrases': {"posso dar uma sugestão", "tenho uma crítica", "quero avaliar"}
            },
            ChatIntent.CLOSE_CHAT: {
            'words': {"sair", "encerrar", "fechar", "acabou", "terminar", "despedir", "tchau", "adeus"},
                'phrases': {"pode encerrar", "tchau", "até mais", "valeu, já resolvi", "nada mais", "até logo"}
            },
            ChatIntent.START: {
                'words': {"começar", "iniciar", "início"},
                'phrases': {"vamos começar", "começa aí", "pode iniciar"}
            },
        }

        self.priority_order = [
            ChatIntent.TRANSFER_HUMAN,
            ChatIntent.SCHEDULE_INFO,
            ChatIntent.SCHEDULE_SLOT_INFO,
            ChatIntent.CANCEL,
            ChatIntent.PAYMENT,
            ChatIntent.ORDER_STATUS,
            ChatIntent.DELIVERY,
            ChatIntent.PRODUCT_INFO,
            ChatIntent.SERVICE_INFO,
            ChatIntent.LOCATION,
            ChatIntent.OPENING_HOURS,
            ChatIntent.PROMOTION,
            ChatIntent.COMPLAINT,
            ChatIntent.DOUBT,
            ChatIntent.PRAISE,
            ChatIntent.FEEDBACK,
            ChatIntent.CLOSE_CHAT,
            ChatIntent.RESTART,
            ChatIntent.WELCOME,
            ChatIntent.START,
            ChatIntent.ABUSIVE,
            ChatIntent.GERAL,
        ]
    
    def classify_intent(self, key_words: List[str], message: str) -> Set[ChatIntent]:
        message_lower = self._normalize_message(message.lower())
        intents: Set[ChatIntent] = set()
        
        profanity_result = self.profanity_classifier.classify_profanity(message)
        
        if profanity_result["contains_profanity"]:
            if profanity_result["level"] in [ProfanityLevel.SEVERE, ProfanityLevel.HATE_SPEECH]:
                return {ChatIntent.ABUSIVE}

        # Verifica se alguma palavra ou frase bate com o texto normalizado
        for intent, triggers in self.intent_triggers.items():
            if any(word in message_lower for word in triggers.get('words', [])):
                intents.add(intent)
            if any(phrase in message_lower for phrase in triggers.get('phrases', [])):
                intents.add(intent)

        # Também considera keywords extraídas
        intents.update(self._check_keywords(key_words))

        return intents or {ChatIntent.GERAL}

    def get_priority_intent(self, intents: Set[ChatIntent]) -> ChatIntent:
        for intent in self.priority_order:
            if intent in intents:
                return intent
        return ChatIntent.GERAL

    def _normalize_message(self, message: str) -> str:
        replacements = {
            "vc": "você", "vcs": "vocês", "q": "que", "pq": "porque",
            "tb": "também", "tá": "está", "ta": "está", "tô": "estou",
            "qdo": "quando", "qnt": "quanto", "qnto": "quanto",
            "qntas": "quantas", "qntos": "quantos", "me ve": "me vê",
            "me vê": "me vê", "cmg": "comigo",
            "blz": "beleza", "pfv": "por favor", "pls": "por favor",
            "obg": "obrigado", "agr": "agora", "hj": "hoje"
        }
        for short, full in replacements.items():
            message = message.replace(short, full)
        return message

    def _check_keywords(self, key_words: List[str]) -> Set[ChatIntent]:
        intents = set()
        
        # Mapeamento de palavras-chave para intenções
        keyword_mapping = {
            # WELCOME
            "oi": ChatIntent.WELCOME,
            "olá": ChatIntent.WELCOME,
            "ola": ChatIntent.WELCOME,
            "oi": ChatIntent.WELCOME,
            "tudo bem": ChatIntent.WELCOME,
            "bom dia": ChatIntent.WELCOME,
            "boa tarde": ChatIntent.WELCOME,
            "boa noite": ChatIntent.WELCOME,
            
            # TRANSFER_HUMAN
            "atendente": ChatIntent.TRANSFER_HUMAN,
            "humano": ChatIntent.TRANSFER_HUMAN,
            
            # RESTART
            "reiniciar": ChatIntent.RESTART,
            "começar": ChatIntent.RESTART,
            
            # COMPANY_INFO
            "empresa": ChatIntent.COMPANY_INFO,
            "contato": ChatIntent.COMPANY_INFO,
            
            # SCHEDULE_INFO
            "agendamentos": ChatIntent.SCHEDULE_INFO,
            "consultas": ChatIntent.SCHEDULE_INFO,
            "marcadas": ChatIntent.SCHEDULE_INFO,
            "verificar": ChatIntent.SCHEDULE_INFO,
            
            # SCHEDULE_SLOT_INFO
            "agendar": ChatIntent.SCHEDULE_SLOT_INFO,
            "consultar": ChatIntent.SCHEDULE_SLOT_INFO,
            "marcar": ChatIntent.SCHEDULE_SLOT_INFO,
            
            # CANCEL
            "cancelar": ChatIntent.CANCEL,
            "desmarcar": ChatIntent.CANCEL,
            
            # PAYMENT
            "pagar": ChatIntent.PAYMENT,
            "valor": ChatIntent.PAYMENT,
            
            # ORDER_STATUS
            "pedido": ChatIntent.ORDER_STATUS,
            "status": ChatIntent.ORDER_STATUS,
            
            # DELIVERY
            "entrega": ChatIntent.DELIVERY,
            "frete": ChatIntent.DELIVERY,
            
            # PRODUCT_INFO
            "produto": ChatIntent.PRODUCT_INFO,
            "item": ChatIntent.PRODUCT_INFO,
            
            # SERVICE_INFO
            "serviço": ChatIntent.SERVICE_INFO,
            "atendimento": ChatIntent.SERVICE_INFO,
            
            # LOCATION
            "endereço": ChatIntent.LOCATION,
            "local": ChatIntent.LOCATION,
            
            # OPENING_HOURS
            "horário": ChatIntent.OPENING_HOURS,
            "funcionamento": ChatIntent.OPENING_HOURS,
            
            # PROMOTION
            "promoção": ChatIntent.PROMOTION,
            "desconto": ChatIntent.PROMOTION,
            
            # COMPLAINT
            "reclamação": ChatIntent.COMPLAINT,
            "problema": ChatIntent.COMPLAINT,
            
            # PRAISE
            "elogio": ChatIntent.PRAISE,
            "parabéns": ChatIntent.PRAISE,
            
            # DOUBT
            "dúvida": ChatIntent.DOUBT,
            "pergunta": ChatIntent.DOUBT,
            
            # FEEDBACK
            "feedback": ChatIntent.FEEDBACK,
            "avaliação": ChatIntent.FEEDBACK,
            
            # CLOSE_CHAT
            "encerrar": ChatIntent.CLOSE_CHAT,
            "sair": ChatIntent.CLOSE_CHAT,
            
            # START
            "começar": ChatIntent.START,
            "iniciar": ChatIntent.START
        }
        
        for word in key_words:
            if word in keyword_mapping:
                intents.add(keyword_mapping[word])
        
        return intents
    

