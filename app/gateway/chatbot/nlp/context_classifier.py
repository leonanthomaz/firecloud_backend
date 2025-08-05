from typing import Dict, Any
from app.enums.chat import ChatIntent

class ContextClassifier:
    """Filtra o contexto removendo dados desnecessários com base na intenção principal."""
    
    # Definição dos conjuntos de intenções
    BASIC_ONLY = {
        ChatIntent.WELCOME, ChatIntent.PRAISE, ChatIntent.CLOSE_CHAT, 
        ChatIntent.FEEDBACK, ChatIntent.START, ChatIntent.GERAL,
        ChatIntent.ORDER_STATUS, ChatIntent.DELIVERY, ChatIntent.CANCEL, 
        ChatIntent.TRANSFER_HUMAN, ChatIntent.RESTART, ChatIntent.ABUSIVE,
        ChatIntent.COMPLAINT
    }

    # COMPANY_INFO e LOCATION agora são tratados com serviços
    NEED_SERVICES = {
        ChatIntent.DOUBT, ChatIntent.COMPANY_INFO, ChatIntent.SERVICE_INFO, 
        ChatIntent.PRODUCT_INFO, ChatIntent.PROMOTION, ChatIntent.PAYMENT, 
        ChatIntent.LOCATION
    }

    NEED_SCHEDULE_INFO = {ChatIntent.SCHEDULE_INFO}
    NEED_SCHEDULE_SLOTS = {ChatIntent.SCHEDULE_SLOT_INFO}

    # Campos essenciais
    ESSENTIAL_COMPANY_KEYS = ["name", "is_open", "chatbot_status", "address", "open_work", "work_days", "social_media"]

    ESSENTIAL_ASSISTANT_KEYS = ["name", "status", "type"]
    
    # Campos mínimos para serviços
    SERVICE_KEYS = ["id", "name", "description", "price", "duration"]
    
    # Campos para agendamentos (baseado no modelo Schedule)
    SCHEDULE_KEYS = [
        "public_id", "title", "start", "end", "all_day", "color",
        "status", "description", "customer_name", "customer_contact"
    ]
    
    # Campos para slots de agendamento (baseado no modelo ScheduleSlot)
    SCHEDULE_SLOT_KEYS = [
        "public_id", "start", "end", "all_day", "is_active", "is_recurring"
    ]

    @classmethod
    def filter_context(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """Filtra o contexto com base na intenção principal."""
        if not context:
            return context
            
        main_intent = context.get("main_intent")
        data = context.get("data", {})
        
        if main_intent in cls.BASIC_ONLY:
            cls._handle_basic_intent(data, context)
        elif main_intent in cls.NEED_SERVICES:
            cls._handle_services_intent(data, context)
        elif main_intent in cls.NEED_SCHEDULE_INFO:
            cls._handle_schedule_info_intent(data)
        elif main_intent in cls.NEED_SCHEDULE_SLOTS:
            cls._handle_schedule_slot_intent(data)
        
        return context

    @classmethod
    def _handle_basic_intent(cls, data: Dict[str, Any], context: Dict[str, Any]):
        """Filtra contexto para intenções básicas."""
        cls._filter_essential_data(data)
        data.pop("services", None)
        data.pop("schedule", None)
        data.pop("schedule_slots", None)
        context.pop("profanity_analysis", None)

    @classmethod
    def _handle_services_intent(cls, data: Dict[str, Any], context: Dict[str, Any]):
        """Filtra contexto para intenções relacionadas a serviços."""
        cls._filter_essential_data(data)
        
        if "services" in data:
            data["services"] = [
                {
                    "category_name": category.get("category_name"),
                    "services": [
                        {k: service[k] for k in cls.SERVICE_KEYS if k in service}
                        for service in category.get("services", [])
                    ]
                }
                for category in data["services"] 
                if category.get("services")
            ]
            
        data.pop("schedule", None)
        data.pop("schedule_slots", None)

    @classmethod
    def _handle_schedule_info_intent(cls, data: Dict[str, Any]):
        """Filtra contexto para verificar agendamentos existentes."""
        cls._filter_essential_data(data)
        
        # Mantém apenas campos essenciais dos agendamentos
        if "schedule" in data:
            if isinstance(data["schedule"], list):
                data["schedule"] = [
                    {k: s[k] for k in cls.SCHEDULE_KEYS if k in s}
                    for s in data["schedule"]
                ]
            else:
                data["schedule"] = {k: data["schedule"][k] for k in cls.SCHEDULE_KEYS if k in data["schedule"]}
        
        # Remove slots pois não são necessários para verificação
        data.pop("schedule_slots", None)

    @classmethod
    def _handle_schedule_slot_intent(cls, data: Dict[str, Any]):
        """Filtra contexto para marcar novos agendamentos."""
        cls._filter_essential_data(data)
        
        # Mantém apenas campos essenciais dos slots
        if isinstance(data.get("schedule_slots"), list):
            data["schedule_slots"] = [
                {k: slot[k] for k in cls.SCHEDULE_SLOT_KEYS if k in slot}
                for slot in data["schedule_slots"]
            ]
        else:
            data["schedule_slots"] = []

        data.pop("schedule", None)

    @classmethod
    def _filter_essential_data(cls, data: Dict[str, Any]):
        """Filtra os dados essenciais da empresa e assistente."""
        if "company" in data:
            data["company"] = {
                k: v for k, v in data["company"].items() 
                if k in cls.ESSENTIAL_COMPANY_KEYS
            }
            
        if "assistant" in data:
            data["assistant"] = {
                k: v for k, v in data["assistant"].items() 
                if k in cls.ESSENTIAL_ASSISTANT_KEYS
            }