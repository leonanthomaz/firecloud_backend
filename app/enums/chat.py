from enum import Enum

class ChatStep(str, Enum):
    # ===== INICIO =====
    START = "START"                         # Início da conversa (primeira mensagem)
    IN_PROGRESS = "IN_PROGRESS"             # Conversa em andamento (IA respondendo normalmente)
    # ===== INICIO =====                    
    BOT_HANDLING = "BOT_HANDLING"           # IA assumiu a conversa de forma ativa
    WAITING_HUMAN = "WAITING_HUMAN"         # Usuário pediu humano, aguardando assumir
    HUMAN_HANDLING = "HUMAN_HANDLING"       # Humano assumiu a conversa
    # ===== BLOQUEIOS =====
    BLOCKED_ABUSE = "BLOCKED_ABUSE"         # Conversa bloqueada por abuso/ofensas
    BLOCKED_LIMIT = "BLOCKED_LIMIT"         # Conversa bloqueada por atingir limite de interações
    BLOCKED_SYSTEM = "BLOCKED_SYSTEM"       # Bloqueio por erro interno, indisponibilidade
    # ===== AÇÕES =====
    WAITING_FEEDBACK = "WAITING_FEEDBACK"   # Aguardando avaliação do usuário
    FEEDBACK = "FEEDBACK"                   # Coletando feedback ativo
    CLOSING = "CLOSING"                     # Encerrando a conversa (mensagem final)
    COMPLETED = "COMPLETED"                 # Conversa finalizada

class ChatbotStatus(str, Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"

class ChatIntent(str, Enum):
    # ===== INTENÇÕES PRIMÁRIAS =====
    START = "START"
    WELCOME = "WELCOME"
    FEEDBACK = "FEEDBACK"
    ABUSIVE = "ABUSIVE"
    
    # ===== INTENÇÕES DE NEGÓCIO =====
    SCHEDULE_INFO = "SCHEDULE_INFO"              # Veridicar agendamento marcado
    SCHEDULE_SLOT_INFO = "SCHEDULE_SLOT_INFO"              # Marcar agendamento
    CANCEL = "CANCEL"                  # Cancelar serviço
    PAYMENT = "PAYMENT"                # Perguntar/preencher pagamento
    DELIVERY = "DELIVERY"              # Info sobre entrega
    COMPANY_INFO = "COMPANY_INFO"      # Detalhes da empresa
    PRODUCT_INFO = "PRODUCT_INFO"      # Detalhes de produto
    SERVICE_INFO = "SERVICE_INFO"      # Detalhes de serviço
    ORDER_STATUS = "ORDER_STATUS"      # Status de pedido/agendamento
    OPENING_HOURS = "OPENING_HOURS"    # Horários de funcionamento
    LOCATION = "LOCATION"              # Endereço/unidade
    PROMOTION = "PROMOTION"            # Promoções ou descontos

    # ===== INTERAÇÃO HUMANA =====
    COMPLAINT = "COMPLAINT"            # Reclamação
    PRAISE = "PRAISE"                  # Elogio
    DOUBT = "DOUBT"                    # Dúvida genérica

    # ===== CONTROLE DE FLUXO =====
    TRANSFER_HUMAN = "TRANSFER_HUMAN"  # Pedir humano
    CLOSE_CHAT = "CLOSE_CHAT"          # Encerrar conversa
    RESTART = "RESTART"                # Recomeçar conversa
    
    GERAL = "GERAL"    

class ChatSentiment(str, Enum):
    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"
    URGENT = "URGENT"
    
class ChatType(str, Enum):
    CHATBOT = "CHATBOT"
    WHATSAPP = "WHATSAPP"
