from datetime import datetime, timedelta, timezone
import re
from app.configuration.settings import Configuration
from app.models.credit.credit import Credit
from app.models.user.user import User
from fastapi import APIRouter, HTTPException, Depends, Request
from app.integration.mercado_pago import sdk
from sqlmodel import Session, select
from app.enums.payment import PaymentMethod, PaymentStatus
from app.models.payment.payment import Payment
from app.models.company.company import Company
from app.models.plan.plan import Plan
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.schemas.payment.payment import PaymentPixProcess
from app.services.email import EmailService
from app.tasks.websockets.ws_manager import payment_ws_manager
import logging

# Configuração de logging
configuration = Configuration()

db_session = get_session
get_current_user = AuthRouter().get_current_user
email_service = EmailService()

class PixRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(prefix="/pix", *args, **kwargs)                
        self.add_api_route("/webhook", self.handle_webhook, methods=["POST"])
        self.add_api_route("/qrcode", self.generate_pix_qrcode, methods=["POST"], response_model=dict)

    async def handle_webhook(self, request: Request, session: Session = Depends(db_session)):
        try:
            body = await request.json()

            logging.info(f"MERCADO PAGO >>> Webhook recebido: {body}")

            if body.get("type") != "payment":
                return {"status": "ignored"}

            payment_id = body.get("data", {}).get("id")

            if not payment_id:
                return {"status": "no_payment_id"}

            try:
                result = sdk.payment().get(payment_id)
            except Exception as e:
                logging.error(f"MERCADO PAGO >>> Erro ao buscar pagamento {payment_id} - {e}")
                return {"status": "payment_not_found"}

            mp_payment = result.get("response")

            if not mp_payment:
                logging.error(f"MERCADO PAGO >>> Pagamento {payment_id} não encontrado")
                return {"status": "payment_not_found"}

            transaction_code = str(mp_payment["id"])
            status = mp_payment["status"]

            payment = session.exec(
                select(Payment).where(Payment.transaction_code == transaction_code)
            ).first()

            if not payment:
                return {"status": "not_found"}

            expires_at = payment.valid_until
            if expires_at and expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if expires_at and expires_at < datetime.now(timezone.utc):
                return {"status": "expired"}

            if status == "approved":
                payment.status = PaymentStatus.PAID
                payment.paid_at = datetime.now(timezone.utc)
                payment.qr_code_base64 = None
            elif status in ["rejected", "cancelled"]:
                payment.status = PaymentStatus.CANCELED
                payment.qr_code_base64 = None
            elif payment.valid_until and payment.valid_until < datetime.now(timezone.utc):
                payment.status = PaymentStatus.CANCELED
                payment.qr_code_base64 = None
            else:
                payment.status = PaymentStatus.PENDING
                
            payment.updated_at = datetime.now(timezone.utc)
            session.add(payment)
            session.commit()
            
            await payment_ws_manager.broadcast({
                "type": "payment_status",
                "transaction_code": transaction_code,
                "status": payment.status,
                "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
            })

            return {"status": "ok"}

        except Exception as e:
            session.rollback()
            logging.error(f"Erro interno no webhook -> {e}")
            return {"status": "internal_error", "detail": str(e)}
        
    def generate_pix_qrcode(self, data: PaymentPixProcess, session: Session = Depends(db_session)):
        try:
            # Busca o pagamento original
            payment = session.exec(select(Payment).where(Payment.id == data.payment_id)).first()
            if not payment:
                raise HTTPException(status_code=404, detail="Pagamento não encontrado")
            
            # Verifica se o pagamento já está pago
            if payment.status == PaymentStatus.PAID:
                raise HTTPException(status_code=400, detail="Pagamento já foi realizado")
            
            # Verifica se já tem QR Code válido (não expirado)
            now_utc = datetime.now(timezone.utc)
            expires_at = payment.valid_until

            if expires_at and expires_at.tzinfo is None:
                expires_at = expires_at.replace(tzinfo=timezone.utc)

            if payment.qr_code and expires_at and expires_at > now_utc:
                return self._build_qrcode_response(payment, session)

            # Busca informações da empresa e usuário
            company = session.exec(select(Company).where(Company.id == payment.company_id)).first()
            if not company:
                raise HTTPException(status_code=404, detail="Empresa não encontrada")
            
            db_user = session.exec(select(User).where(User.company_id == company.id)).first()
            if not db_user:
                raise HTTPException(status_code=404, detail="Usuário não encontrado")

            # Validação dos dados
            if not db_user.email:
                raise HTTPException(status_code=400, detail="E-mail do usuário não cadastrado")
            
            if not db_user.first_name:
                raise HTTPException(status_code=400, detail="Nome do usuário não cadastrado")
            
            if not db_user.last_name:
                raise HTTPException(status_code=400, detail="Sobrenome do usuário não cadastrado")
            
            # Determina a descrição com base no tipo de pagamento
            if payment.plan_id:
                plan = session.exec(select(Plan).where(Plan.id == payment.plan_id)).first()
                descricao = f"Mensalidade de {datetime.now().strftime('%m/%Y')} - {plan.name if plan else 'Plano'}"
            elif payment.credit_id:
                credit = session.exec(select(Credit).where(Credit.id == payment.credit_id)).first()
                descricao = f"Créditos {credit.token_amount if credit else ''} tokens - {company.name}"
            else:
                descricao = f"Pagamento para {company.name}"

            body = {
                "transaction_amount": float(payment.amount),
                "description": descricao,
                "payment_method_id": "pix",
                "payer": {
                    "email": db_user.email,
                    "first_name": db_user.first_name or "Empresa",
                    "last_name": db_user.last_name or company.name,
                    "identification": {
                        "type": "CNPJ",
                        "number": re.sub(r'\D', '', company.cnpj)
                    }
                },
                # "notification_url": configuration.url_notifications_pix,
                # "date_of_expiration": (now_utc + timedelta(minutes=30)).isoformat(timespec='seconds') + 'Z'
            }

            logging.info(f"Enviando para Mercado Pago: {body}")

            try:
                result = sdk.payment().create(body)
                response = result.get("response")
                
                if not response:
                    raise HTTPException(status_code=400, detail="Resposta vazia do Mercado Pago")
                
                if response.get("status") != "pending":
                    error_message = response.get("message", "Erro ao gerar PIX")
                    raise HTTPException(status_code=400, detail=error_message)
               
                poi = response.get("point_of_interaction", {})
                transaction_data = poi.get("transaction_data", {})
                qr_code = transaction_data.get("qr_code")
                qr_code_base64 = transaction_data.get("qr_code_base64")
                transaction_code = str(response["id"])

                if not qr_code:
                    raise HTTPException(status_code=400, detail="QR Code não gerado pelo Mercado Pago")

                # Atualiza o pagamento existente
                expires_at = now_utc + timedelta(minutes=30)
                payment.qr_code = qr_code
                payment.qr_code_base64 = qr_code_base64
                payment.transaction_code = transaction_code
                payment.valid_until = expires_at
                payment.status = PaymentStatus.PENDING
                payment.updated_at = now_utc
                payment.payment_method = PaymentMethod.PIX

                session.add(payment)
                session.commit()
                session.refresh(payment)

                return self._build_qrcode_response(payment, session)

            except Exception as mp_error:
                logging.error(f"Erro na API do Mercado Pago: {str(mp_error)}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Erro na comunicação com o Mercado Pago: {str(mp_error)}"
                )

        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logging.error(f"Erro ao gerar PIX: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao processar PIX: {str(e)}"
            )

    def _build_qrcode_response(self, payment: Payment, session: Session) -> dict:
        """Helper para construir a resposta padronizada do QR Code"""
        response_data = {
            "qr_code": payment.qr_code,
            "qr_code_base64": payment.qr_code_base64,
            "transaction_code": payment.transaction_code,
            "expires_at": payment.valid_until.isoformat(),
            "status": payment.status,
            "amount": payment.amount,
            "company_id": payment.company_id
        }

        # Adiciona informações específicas do plano ou crédito
        if not payment.credit_id:
            plan = session.exec(select(Plan).where(Plan.id == payment.plan_id)).first()
            if plan:
                response_data["plan"] = {
                    "id": plan.id,
                    "name": plan.name,
                    "price": plan.price
                }
        
        if payment.credit_id:
            credit = session.exec(select(Credit).where(Credit.id == payment.credit_id)).first()
            if credit:
                response_data["credit"] = {
                    "id": credit.id,
                    "name": credit.name,
                    "token_amount": credit.token_amount,
                    "price": credit.price
                }
                response_data["token_amount"] = credit.token_amount

        return response_data
