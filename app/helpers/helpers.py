
from app.configuration.settings import Configuration
from app.database.connection import get_session
from sqlmodel import Session

Configuration()

def get_session() -> Session:
    return get_session()


