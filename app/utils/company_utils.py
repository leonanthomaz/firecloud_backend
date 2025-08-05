import logging
import uuid
from fastapi import HTTPException, UploadFile

from app.auth.auth import AuthRouter
from app.configuration.settings import Configuration
from app.database.connection import get_session
from app.integration.R2Service import R2Service
from app.models.plan.plan import Plan
from app.services.email import EmailService

# Instâncias
db_session = get_session
email_service = EmailService()
configuration = Configuration()
get_current_user = AuthRouter().get_current_user
r2_service = R2Service()

async def upload_logo_company(image_file: UploadFile) -> dict:
    try:
        file_extension = image_file.filename.split(".")[-1].lower()
        image_filename = f"{uuid.uuid4().hex}.{file_extension}"
        
        contents = await image_file.read()
        image_url = await r2_service.upload_file(
            file_content=contents,
            file_name=image_filename,
            content_type=image_file.content_type
        )

        return {"filename": image_filename, "url": image_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer upload do logo: {e}")

def remove_logo_company(image_filename: str):
    try:
        if not image_filename:
            return

        r2_service.delete_file(image_filename)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover o logo: {e}")
    
def calculate_plan_duration(plan: Plan) -> int:
        """Calcula a duração em dias do plano"""
        try:
            if plan.interval == "month":
                return plan.interval_count * 30
            elif plan.interval == "year":
                return plan.interval_count * 365
            else:  # day
                return plan.interval_count
        except Exception as e:
            logging.error(f"Erro ao calcular duração do plano: {str(e)}")
            return 30  # Default para 30 dias
