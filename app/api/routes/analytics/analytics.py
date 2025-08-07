from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlmodel import Session
from datetime import datetime
from app.models.chat.assistant import Assistant
from app.models.chat.interaction import Interaction
from app.models.company.company import Company
from app.auth.auth import AuthRouter
from app.database.connection import get_session

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from fastapi.responses import FileResponse
import tempfile

db_session = get_session
get_current_user = AuthRouter().get_current_user

class AnalyticsRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_api_route("/analytics/report/{company_id}", self.generate_report, methods=["GET"])
    
    async def generate_report(self, company_id: int, session: Session = Depends(get_session)):
        try:
            company = session.query(Company).filter(Company.id == company_id).first()
            if not company:
                raise HTTPException(status_code=404, detail="Empresa não encontrada")

            assistant = session.query(Assistant).filter(Assistant.company_id == company_id).first()
            interactions = session.query(Interaction).filter(Interaction.company_id == company_id).all()

            metrics = self._calculate_metrics(interactions, assistant)

            filename = f"relatorio_{company.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"

            # Cria arquivo temporário
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                doc = SimpleDocTemplate(tmp.name, pagesize=A4)
                styles = getSampleStyleSheet()
                elements = [
                    Paragraph(f"Relatório de Análise - {company.name}", styles["Title"]),
                    Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]),
                    Spacer(1, 12),

                    Paragraph("Métricas:", styles["Heading2"]),
                    Paragraph(f"Total de Interações: {metrics['total_interactions']}", styles["Normal"]),
                    Paragraph(f"Total de Clientes Únicos: {metrics['unique_clients']}", styles["Normal"]),
                    Paragraph(f"Tokens Usados: {metrics['tokens_used']} de {metrics['tokens_available']} ({metrics['token_usage_percentage']}%)", styles["Normal"]),
                    Paragraph(f"Média de Tokens por Interação: {metrics['avg_tokens']}", styles["Normal"]),
                    Paragraph(f"Limite de Tokens: {metrics['token_limit']}", styles["Normal"]),
                    Paragraph(f"Reset de Tokens: {metrics['token_reset_date']}", styles["Normal"]),
                    Paragraph(f"Atendimentos Humanos: {metrics['human_attendances']}", styles["Normal"]),
                    Paragraph(f"Última Interação: {metrics['last_interaction'].strftime('%d/%m/%Y %H:%M') if metrics['last_interaction'] else 'N/A'}", styles["Normal"]),
                    Spacer(1, 12),

                    Paragraph("Assistente:", styles["Heading2"]),
                    Paragraph(f"Nome: {metrics['assistant_name']}", styles["Normal"]),
                    Paragraph(f"Tipo: {metrics['assistant_type']}", styles["Normal"]),
                    Paragraph(f"Modelo: {metrics['assistant_model']}", styles["Normal"]),
                    Spacer(1, 12),

                    Paragraph("Sentimentos:", styles["Heading2"]),
                ]
                for k, v in metrics["sentiments"].items():
                    elements.append(Paragraph(f"{k}: {v}", styles["Normal"]))

                doc.build(elements)
                tmp_path = tmp.name

            # Retorna como FileResponse forçando o download
            return FileResponse(
                tmp_path,
                media_type='application/pdf',
                filename=filename,
                headers={"Content-Disposition": f'attachment; filename="{filename}"'}
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

    
    def _calculate_metrics(self, interactions, assistant):
        base_metrics = {
            "total_interactions": len(interactions),
            "sentiments": {"POSITIVE": 0, "NEUTRAL": 0, "NEGATIVE": 0},
            "unique_clients": len(set(i.client_contact for i in interactions if i.client_contact)),
            "last_interaction": max((i.created_at for i in interactions if i.created_at), default=None),
            "human_attendances": sum(1 for i in interactions if i.chat and i.chat.human_attendance),
        }

        for interaction in interactions:
            sentiment = interaction.sentiment.upper() if interaction.sentiment else "NEUTRAL"
            if sentiment in base_metrics["sentiments"]:
                base_metrics["sentiments"][sentiment] += 1

        if not assistant:
            return {
                **base_metrics,
                "tokens_used": 0,
                "tokens_available": 0,
                "token_usage_percentage": 0,
                "avg_tokens": 0,
                "token_limit": 0,
                "token_reset_date": "N/A",
                "assistant_name": "N/A",
                "assistant_type": "N/A",
                "assistant_model": "N/A",
            }

        tokens_used = assistant.assistant_token_usage or 0
        tokens_available = assistant.assistant_token_limit or 0

        token_usage_percentage = (
            round((tokens_used / tokens_available) * 100) if tokens_available > 0 else 0
        )

        avg_tokens = (
            round(sum(i.total_tokens or 0 for i in interactions) / len(interactions))
            if len(interactions) > 0
            else 0
        )

        return {
            **base_metrics,
            "tokens_used": tokens_used,
            "tokens_available": tokens_available,
            "token_usage_percentage": token_usage_percentage,
            "avg_tokens": avg_tokens,
            "token_limit": tokens_available,
            "token_reset_date": assistant.assistant_token_reset_date.strftime("%d/%m/%Y")
            if assistant.assistant_token_reset_date
            else "N/A",
            "assistant_name": assistant.assistant_name or "N/A",
            "assistant_type": assistant.assistant_type or "N/A",
            "assistant_model": assistant.assistant_model or "N/A",
        }
