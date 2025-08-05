# from datetime import datetime, timezone
import logging
import os
import json
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from google.auth.transport.requests import Request
from google.oauth2 import credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from app.schemas.schedule.google_schedule import ScheduleRequest, ScheduleUpdate
from app.configuration.settings import Configuration
from app.models.user.user import User
from app.auth.auth import AuthRouter
from fastapi.responses import RedirectResponse

# Configuração de Autenticação e Google Calendar
SCOPES = ["https://www.googleapis.com/auth/calendar"]

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_ID_CLIENT")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_SECRET_KEY")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

get_current_user = AuthRouter().get_current_user
configuration = Configuration()

# Função para gerar credenciais a partir do token recebido do frontend
def generate_creds_from_token(token_data: dict):
    try:
        # Verifica se o token_data contém as informações necessárias
        required_fields = ['token', 'token_uri', 'client_id', 'client_secret', 'scopes']
        if not all(field in token_data for field in required_fields):
            logging.error("Token inválido ou incompleto.")
            return None

        # Cria as credenciais
        creds = credentials.Credentials(
            token=token_data.get('token'),
            refresh_token=token_data.get('refresh_token'),  # Pode ser None
            token_uri=token_data.get('token_uri'),
            client_id=token_data.get('client_id'),
            client_secret=token_data.get('client_secret'),
            scopes=token_data.get('scopes')
        )
        return creds
    except Exception as e:
        logging.error(f"Erro ao gerar credenciais a partir do token: {e}")
        return None

# Valida e atualiza o token, se necessário
def validate_token(creds: credentials.Credentials):
    try:
        if creds and creds.expired and creds.refresh_token:
            logging.info("Token expirado. Tentando renovar...")
            creds.refresh(Request())
            return True
        if creds and creds.valid:
            return True
        logging.error("Token inválido ou não pode ser renovado.")
        return False
    except Exception as e:
        logging.error(f"Erro ao validar o token: {e}")
        return False

class GoogleCalendarRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(prefix="/api/google_calendar", *args, **kwargs)
        self.add_api_route("/events", self.create_event, methods=["POST"], response_model=dict)
        self.add_api_route("/events", self.list_events, methods=["GET"])
        self.add_api_route("/events/{event_id}", self.update_event, methods=["PATCH"], response_model=dict)
        self.add_api_route("/events/{event_id}", self.delete_event, methods=["DELETE"], response_model=dict)
        self.add_api_route("/callback", self.google_callback, methods=["GET"], response_model=dict)

    def get_calendar_service(self, googleToken: dict):
        """Processa o token e retorna o serviço do Google Calendar."""
        try:
            # Verifica se o token está válido
            creds = generate_creds_from_token(googleToken)
            if not creds or not validate_token(creds):
                raise HTTPException(status_code=400, detail="Token inválido ou expirado.")
            
            # Cria o serviço do Google Calendar
            service = build('calendar', 'v3', credentials=creds)
            return service
        except Exception as e:
            logging.error(f"Erro ao processar o googleToken: {e}")
            raise HTTPException(status_code=400, detail="Erro ao processar o token.")

    async def list_events(self, googleToken: str = Query(...)):
        try:
            googleToken = json.loads(googleToken)  # Converte a string JSON de volta para um objeto
            logging.info(f"GOOGLE TOKEN: {googleToken}")
            
            if not googleToken:
                logging.error("Token não fornecido.")
                raise HTTPException(status_code=400, detail="Token não fornecido.")
            
            creds = generate_creds_from_token(googleToken)
            if not creds:
                logging.error("Falha ao gerar credenciais a partir do token.")
                raise HTTPException(status_code=400, detail="Falha ao gerar credenciais.")

            if not validate_token(creds):
                logging.error("Token inválido ou expirado.")
                raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

            calendar_service = build('calendar', 'v3', credentials=creds)
            logging.info("Tentando listar eventos do Google Calendar...")
            
            # # Definir o período para o ano de 2025
            # time_min = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat()
            # time_max = datetime(2026, 1, 1, 0, 0, 0, tzinfo=timezone.utc).isoformat()

            # events_result = calendar_service.events().list(
            #     calendarId='primary',
            #     timeMin=time_min,
            #     timeMax=time_max,
            #     maxResults=100,  # Aumentei o maxResults para pegar mais eventos
            #     singleEvents=True,
            #     orderBy='startTime'
            # ).execute()
            
            events_result = calendar_service.events().list(calendarId='primary', maxResults=10).execute()
            events = events_result.get('items', [])
            return events
        except Exception as e:
            logging.error(f"Erro ao listar eventos: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Erro ao listar eventos: {str(e)}")

    def create_event(self, schedule_request: ScheduleRequest, googleToken: str = Body(embed=True), current_user: User = Depends(get_current_user)):
        """Cria um evento no Google Calendar."""
        if not current_user:
            logging.error("Usuário não autenticado.")
            raise HTTPException(status_code=401, detail="Usuário não autenticado.")

        try:
            googleToken_dict = json.loads(googleToken)
            calendar_service = self.get_calendar_service(googleToken_dict)

            event = {
                'summary': schedule_request.summary,
                'start': {
                    'dateTime': schedule_request.start_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
                'end': {
                    'dateTime': schedule_request.end_time.isoformat(),
                    'timeZone': 'America/Sao_Paulo',
                },
            }
            event = calendar_service.events().insert(calendarId='primary', body=event).execute()
            return event
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Token inválido.")

    def update_event(self, event_id: str, schedule_update: ScheduleUpdate, googleToken: str = Body(embed=True), current_user: User = Depends(get_current_user)):
        """Atualiza um evento no Google Calendar."""
        if not current_user:
            logging.error("Usuário não autenticado.")
            raise HTTPException(status_code=401, detail="Usuário não autenticado.")

        try:
            googleToken_dict = json.loads(googleToken)
            calendar_service = self.get_calendar_service(googleToken_dict)

            event = calendar_service.events().get(calendarId='primary', eventId=event_id).execute()
            event['summary'] = schedule_update.summary
            event['start']['dateTime'] = schedule_update.start_time.isoformat()
            event['end']['dateTime'] = schedule_update.end_time.isoformat()

            updated_event = calendar_service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
            return updated_event
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Token inválido.")

    def delete_event(self, event_id: str, googleToken: str = Body(embed=True), current_user: User = Depends(get_current_user)):
        """Deleta um evento do Google Calendar."""
        if not current_user:
            logging.error("Usuário não autenticado.")
            raise HTTPException(status_code=401, detail="Usuário não autenticado.")

        try:
            googleToken_dict = json.loads(googleToken)
            calendar_service = self.get_calendar_service(googleToken_dict)

            calendar_service.events().delete(calendarId='primary', eventId=event_id).execute()
            return {"message": "Evento deletado com sucesso."}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Token inválido.")
        
    async def google_callback(self, code: str = Query(...)):
        """Processa o código de callback do Google e gera o token para enviar ao frontend."""
        try:
            logging.info(f"Callback recebido com código: {code}")
            flow = InstalledAppFlow.from_client_secrets_file(
                'google_credentials.json',
                scopes=SCOPES,
                redirect_uri=GOOGLE_REDIRECT_URI,
            )
            logging.info("Flow inicializado")
            flow.fetch_token(code=code, access_type='offline')
            logging.info("Token obtido")

            creds = flow.credentials
            if not creds:
                logging.error("Falha ao obter credenciais")
                raise HTTPException(status_code=400, detail="Falha na obtenção do token.")

            logging.info("Credenciais obtidas")
            # redirect_url = f"http://localhost:3000/dashboard/schedules?token={quote(creds.to_json())}"
            redirect_url = f"https://firecloud-frontend.vercel.app/dashboard/schedules?token={quote(creds.to_json())}"
            return RedirectResponse(url=redirect_url)

        except Exception as e:
            logging.error(f"Erro no processo de callback: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Erro ao processar o código de autenticação.")
