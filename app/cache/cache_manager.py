# app/tasks/cache/cache_manager.py

from datetime import datetime
import logging
from typing import List, Optional
from app.models.chat.assistant import Assistant
from app.models.company.company import Company
from app.cache.cache import Cache
from app.models.service.category_service import CategoryService
from sqlmodel import Session, select

from app.models.schedule.schedule import Schedule
from app.models.schedule.schedule_slot import ScheduleSlot

cache = Cache()

class CacheManager:
    _cache_key_prefix = "chat_data_"
    
    def __init__(self):
        self.cache = cache

    def get_cache_key(self, key: str) -> str:
        """Gera a chave de cache completa com o prefixo"""
        return f"{self._cache_key_prefix}{key}"

    async def load_cached_data(self, key: str) -> Optional[dict]:
        """Carrega dados do cache"""
        cache_key = self.get_cache_key(key)
        cached_data = self.cache.get(cache_key)
        if cached_data:
            logging.info(f"Dados encontrados no cache para a chave: {cache_key}")
        return cached_data

    async def cache_data(self, key: str, data: dict) -> None:
        """Armazena dados no cache"""
        cache_key = self.get_cache_key(key)
        self.cache.set(cache_key, data, ttl=900)
        logging.info(f"Dados armazenados no cache com a chave: {cache_key}")

    async def get_company_data(self, session: Session, company_id: int) -> dict:
        cache_key = self.get_cache_key(f"company_info_{company_id}")
        cached = await self.load_cached_data(cache_key)

        if cached:
            company_status = session.exec(
                select(Company.is_open).where(Company.id == company_id)
            ).first()

            cached["is_open"] = company_status if company_status else "CLOSE"
            return cached

        # Se não está no cache, buscar do banco
        company = session.exec(select(Company).where(Company.id == company_id)).first()

        company_data = {
            "name": company.name if company else "Empresa",
            "status": company.status if company and company.status else "CLOSE",
            "is_open": company.is_open if company and company.is_open else "CLOSE",
            "address": company.addresses[0].street if company and company.addresses else "Endereço não disponível",
            "open_work": (
                f"{company.opening_time.strftime('%H:%M')} às {company.closing_time.strftime('%H:%M')}"
                if company and company.opening_time and company.closing_time else "Horário não disponível"
            ),
            "work_days": company.working_days if company and company.working_days else [],
            "social_media": company.social_media_links if company and company.social_media_links else {},
        }

        await self.cache_data(cache_key, company_data)
        return company_data

    async def get_assistant_data(self, session: Session, company_id: int) -> dict:
        cache_key = self.get_cache_key(f"assistant_info_{company_id}")
        cached = await self.load_cached_data(cache_key)
        if cached:
            status = session.exec(
                select(Assistant.status).where(Assistant.company_id == company_id)
            ).first()
            cached["status"] = status if status else "OFFLINE"
            return cached

        assistant = session.exec(
            select(Assistant).where(Assistant.company_id == company_id)
        ).first()

        if not assistant:
            return {
                "name": "Assistente",
                "status": "OFFLINE",
                "type": None,
                "model": None,
                "api_url": None,
                "token_limit": None,
                "token_usage": 0,
                "token_reset_date": None,
            }

        assistant_data = {
            "name": assistant.assistant_name,
            "status": assistant.status if assistant.status else "OFFLINE",
            "type": assistant.assistant_type,
            "model": assistant.assistant_model,
            "api_url": assistant.assistant_api_url,
        }

        await self.cache_data(cache_key, assistant_data)
        return assistant_data

    async def get_service_data(self, session: Session, company_id: int) -> dict:
        cache_key = self.get_cache_key(f"service_data_{company_id}")
        cached = await self.load_cached_data(cache_key)
        if cached:
            # Atualiza os dados sempre do banco
            categories = session.exec(
                select(CategoryService).where(CategoryService.company_id == company_id)
            ).all()

            service_data = [
                {
                    "category_id": category.id,
                    "category_name": category.name,
                    "services": [
                        {
                            "id": service.id,
                            "name": service.name,
                            "description": service.description,
                            "price": service.price,
                            "duration": service.duration,
                            "availability": service.availability,
                            "rating": service.rating,
                            "image": service.image,
                        }
                        for service in category.services
                        if not service.deleted_at
                    ],
                }
                for category in categories
                if not category.deleted_at
            ]

            await self.cache_data(cache_key, service_data)
            return service_data

        # Se não tá no cache, busca e salva
        categories = session.exec(
            select(CategoryService).where(CategoryService.company_id == company_id)
        ).all()

        service_data = [
            {
                "category_id": category.id,
                "category_name": category.name,
                "services": [
                    {
                        "id": service.id,
                        "name": service.name,
                        "description": service.description,
                        "price": service.price,
                        "duration": service.duration,
                        "availability": service.availability,
                        "rating": service.rating,
                        "image": service.image,
                    }
                    for service in category.services
                    if not service.deleted_at
                ],
            }
            for category in categories
            if not category.deleted_at
        ]

        await self.cache_data(cache_key, service_data)
        return service_data
    
    async def get_schedule_data(self, session: Session, company_id: int) -> dict:
        cache_key = f"schedules_{company_id}"
        
        cached = await self.load_cached_data(cache_key)
        if cached:
            last_update = session.exec(
                select(Schedule.updated_at)
                .where(Schedule.company_id == company_id)
                .order_by(Schedule.updated_at.desc())
            ).first()

            cache_time = datetime.fromisoformat(cached['last_updated'])
            if last_update and last_update <= cache_time:
                return cached

        schedules = session.exec(
            select(Schedule)
            .where(Schedule.company_id == company_id)
            .order_by(Schedule.start)
        ).all()

        calendar_events = [
            schedule.to_calendar_event()
            for schedule in schedules
            if schedule.start
        ]

        schedule_data = {
            "events_data": calendar_events,
            "last_updated": datetime.now().isoformat()
        }

        await self.cache_data(cache_key, schedule_data)
        return schedule_data

    async def get_schedule_slots_data(self, session: Session, company_id: int) -> List[dict]:
        """
        Obtém os slots de agendamento do cache ou do banco de dados.
        Atualiza o cache se necessário.
        """
        cache_key = self.get_cache_key(f"schedule_slots_{company_id}")
        cached = await self.load_cached_data(cache_key)
        
        # Verifica se precisa atualizar o cache
        needs_refresh = False
        if cached:
            # Busca a última atualização no banco
            last_db_update = session.exec(
                select(ScheduleSlot.updated_at)
                .where(ScheduleSlot.company_id == company_id)
                .order_by(ScheduleSlot.updated_at.desc())
            ).first()
            
            if last_db_update and datetime.fromisoformat(cached['last_updated']) < last_db_update:
                needs_refresh = True
        else:
            needs_refresh = True

        if not needs_refresh:
            return cached['slots']

        # Busca os dados atualizados do banco
        slots = session.exec(
            select(ScheduleSlot)
            .where(ScheduleSlot.company_id == company_id)
            .order_by(ScheduleSlot.start)
        ).all()

        # Formata os dados para o cache
        slots_data = [self._format_slot_data(slot) for slot in slots]
        
        # Atualiza o cache
        cache_data = {
            "slots": slots_data,
            "last_updated": datetime.now().isoformat()
        }
        await self.cache_data(cache_key, cache_data)
        
        return slots_data

    async def invalidate_schedule_slots_cache(self, company_id: int) -> None:
        """
        Invalida o cache de slots de agendamento para uma empresa específica.
        Útil quando sabemos que os dados foram alterados.
        """
        cache_key = self.get_cache_key(f"schedule_slots_{company_id}")
        self.cache.delete(cache_key)

    def _format_slot_data(self, slot: ScheduleSlot) -> dict:
        """Formata os dados de um slot para o formato de cache"""
        return {
            "id": slot.id,
            "public_id": slot.public_id,
            "start": slot.start.isoformat(),
            "end": slot.end.isoformat(),
            "all_day": slot.all_day,
            "is_active": slot.is_active,
            "is_recurring": slot.is_recurring,
            "company_id": slot.company_id,
            "service_id": slot.service_id,
            "schedule_id": slot.schedule_id,
            "created_at": slot.created_at.isoformat(),
            "updated_at": slot.updated_at.isoformat()
        }

    async def get_available_slots(self, session: Session, company_id: int, service_id: Optional[int] = None) -> List[dict]:
        """
        Obtém apenas os slots disponíveis (is_active=True e sem schedule_id)
        Opcionalmente filtra por service_id.
        """
        all_slots = await self.get_schedule_slots_data(session, company_id)
        
        available_slots = [
            slot for slot in all_slots 
            if slot['is_active'] and not slot['schedule_id']
        ]
        
        if service_id:
            available_slots = [
                slot for slot in available_slots
                if slot['service_id'] == service_id
            ]
        
        return available_slots