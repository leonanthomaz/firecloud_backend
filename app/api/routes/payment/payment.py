from datetime import datetime, timedelta, timezone
from typing import List
from app.configuration.settings import Configuration
from app.enums.credit import CreditOriginEnum
from app.models.credit.credit import Credit
from fastapi import APIRouter, HTTPException, status, Depends
from app.integration.mercado_pago import sdk
from sqlmodel import Session, select
from app.enums.payment import PaymentStatus, PaymentType
from app.models.payment.payment import Payment
from app.models.company.company import Company
from app.models.plan.plan import Plan
from app.auth.auth import AuthRouter
from app.database.connection import get_session
from app.schemas.payment.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from app.services.email import EmailService
import logging

from app.utils.company_utils import calculate_plan_duration
from app.utils.payment_utils import notify_payment_paid

# Configuração de logging
configuration = Configuration()

db_session = get_session
get_current_user = AuthRouter().get_current_user
email_service = EmailService()

class PaymentRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.add_api_route("/payments/", self.list_payments, methods=["GET"], response_model=List[PaymentResponse])
        self.add_api_route("/payments/", self.create_payment, methods=["POST"], response_model=PaymentResponse)
                
        self.add_api_route("/payments/{payment_id}", self.get_payment_by_id, methods=["GET"], response_model=PaymentResponse)
        self.add_api_route("/payments/{payment_id}", self.update_payment, methods=["PUT"], response_model=PaymentResponse)
        
        self.add_api_route("/payments/status/{transaction_code}", self.check_payment_status, methods=["GET"])
        self.add_api_route("/payments/company/{company_id}", self.get_payments_by_company, methods=["GET"], response_model=List[PaymentResponse])

    async def list_payments(self, session: Session = Depends(db_session)):
        """Lista todos os pagamentos"""
        try:
            logging.info("Iniciando listagem de pagamentos")
            payments = session.exec(select(Payment)).all()
            
            if not payments:
                logging.warning("Nenhum pagamento encontrado")
                return []
                
            logging.info(f"Retornando {len(payments)} pagamentos")
            
            return payments
            
        except Exception as e:
            logging.error(f"Erro ao listar pagamentos: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao listar pagamentos"
            )
            
    async def get_payment_by_id(self, payment_id: int, session: Session = Depends(db_session)):
        """Retorna um pagamento específico por ID"""
        try:
            logging.info(f"Buscando pagamento com ID {payment_id}")
            
            payment = session.get(Payment, payment_id)
            if not payment:
                logging.error(f"Pagamento não encontrado: {payment_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pagamento não encontrado"
                )

            return payment

        except Exception as e:
            logging.error(f"Erro ao buscar pagamento {payment_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar pagamento"
            )

    async def create_payment(self, payment_request: PaymentCreate, session: Session = Depends(db_session)):
        logging.info(f"DADOS VINDOS DO PAGAMENTO >>> {payment_request}")
        """Cria um novo pagamento (para planos ou créditos)"""
        try:
            if not payment_request.company_id:
                raise HTTPException(status_code=400, detail="ID da empresa é obrigatório")

            if not payment_request.amount or payment_request.amount <= 0:
                raise HTTPException(status_code=400, detail="Valor do pagamento deve ser positivo")

            is_credit_payment = payment_request.credit_id is not None

            # Valida empresa
            company = session.get(Company, payment_request.company_id)
            if not company:
                raise HTTPException(status_code=404, detail="Empresa não encontrada")

            plan = None
            description = ""
            valid_until = None
            
            if is_credit_payment:
                # Pagamento de crédito
                credit = session.get(Credit, payment_request.credit_id)
                if not credit:
                    raise HTTPException(status_code=404, detail="Crédito não encontrado")

                # Crédito sempre precisa de plano associado
                plan = session.get(Plan, credit.plan_id)
                if not plan:
                    raise HTTPException(status_code=404, detail="Plano associado ao crédito não encontrado")

                if float(payment_request.amount) != float(credit.price):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Valor do pagamento ({payment_request.amount}) não corresponde ao preço do crédito ({credit.price})"
                    )
                
                origin = CreditOriginEnum.CREDIT
                description = f"Compra de {credit.token_amount} tokens - Plano {plan.name}"
                valid_until = datetime.now(timezone.utc) + timedelta(days=30)
            else:
                # Pagamento de plano
                if not payment_request.plan_id:
                    raise HTTPException(status_code=400, detail="ID do plano é obrigatório")

                plan = session.get(Plan, payment_request.plan_id)
                if not plan:
                    raise HTTPException(status_code=404, detail="Plano não encontrado")

                if float(payment_request.amount) != float(plan.price):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Valor do pagamento ({payment_request.amount}) não corresponde ao preço do plano ({plan.price})"
                    )

                existing_payment = session.exec(
                    select(Payment).where(
                        (Payment.company_id == company.id) &
                        (Payment.plan_id == plan.id) &
                        (Payment.credit_id.is_(None)) &
                        (Payment.status.in_([PaymentStatus.PENDING, PaymentStatus.PAID, PaymentStatus.TRIAL]))
                    )
                ).first()

                if existing_payment:
                    raise HTTPException(
                        status_code=400,
                        detail="Já existe um pagamento ativo para este plano"
                    )

                origin = CreditOriginEnum.PLAN
                description = f"Assinatura do plano {plan.name}"
                valid_until = datetime.now(timezone.utc) + timedelta(days=calculate_plan_duration(plan))
                
            # Criação do pagamento
            payment = Payment(
                company_id=company.id,
                type=PaymentType.PLAN if not is_credit_payment else PaymentType.CREDIT,
                name=plan.name if plan else payment_request.name,
                slug=plan.slug if plan else payment_request.slug,
                description=payment_request.description or description,
                quantity=payment_request.quantity or 1,
                total=payment_request.amount * (payment_request.quantity or 1),
                reference_id=plan.id if plan else payment_request.credit_id,
                plan_id=plan.id if plan else None,
                credit_id=payment_request.credit_id if is_credit_payment else None,
                amount=payment_request.amount,
                payment_date=datetime.now(timezone.utc),
                valid_from=datetime.now(timezone.utc),
                valid_until=valid_until,
                status=payment_request.status or PaymentStatus.PENDING,
                payment_method=payment_request.payment_method,
                origin=origin,
            )

            session.add(payment)
            session.commit()
            session.refresh(payment)

            logging.info(f"Pagamento {payment.id} criado com sucesso - Tipo: {'Crédito' if is_credit_payment else 'Plano'}")
            return payment

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Erro ao criar pagamento: {str(e)}", exc_info=True)
            session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno ao criar pagamento: {str(e)}"
            )

    async def update_payment(self, payment_id: int, payment_update: PaymentUpdate, session: Session = Depends(db_session)):
        """Atualiza um pagamento existente"""
        try:
            logging.info(f"Iniciando atualização do pagamento {payment_id}")
            
            payment = session.get(Payment, payment_id)
            if not payment:
                logging.error(f"Pagamento não encontrado: {payment_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Pagamento não encontrado"
                )
                
            for field, value in update_data.items():
                if field not in ["company_id"]:
                    setattr(payment, field, value)

            # Atualiza apenas campos válidos
            update_data = payment_update.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(payment, field, value)

            payment.updated_at = datetime.now(datetime.timezone.utc)
            
            session.add(payment)
            session.commit()
            session.refresh(payment)
            
            if payment.status == PaymentStatus.PAID:
                payment.paid_at = datetime.now(timezone.utc)
                await notify_payment_paid(payment)
            
            logging.info(f"Pagamento {payment_id} atualizado com sucesso")
            
            return payment

        except HTTPException:
            raise
        except Exception as e:
            logging.error(f"Erro ao atualizar pagamento {payment_id}: {str(e)}")
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao atualizar pagamento"
            )

    async def get_payments_by_company(self, company_id: int, session: Session = Depends(db_session)):
        """Lista pagamentos por empresa"""
        try:
            logging.info(f"Buscando pagamentos para empresa {company_id}")
            
            company = session.get(Company, company_id)
            if not company:
                logging.error(f"Empresa não encontrada: {company_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Empresa não encontrada"
                )

            payments = session.exec(
                select(Payment)
                .where(Payment.company_id == company_id)
                .order_by(Payment.created_at.desc())
            ).all()
            
            logging.info(f"Encontrados {len(payments)} pagamentos para empresa {company_id}")
            return payments

        except Exception as e:
            logging.error(f"Erro ao buscar pagamentos para empresa {company_id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno ao buscar pagamentos"
            )

    async def check_payment_status(self, transaction_code: str, session: Session = Depends(db_session)):
        try:
            logging.info(f"Monitorando status do pagamento {transaction_code}")
            payment = session.exec(
                select(Payment).where(Payment.transaction_code == transaction_code)
            ).first()

            if not payment:
                raise HTTPException(status_code=404, detail="Pagamento não encontrado")
            
            # Se já estiver pago, notifica e retorna
            if payment.status == PaymentStatus.PAID:
                payment.paid_at = datetime.now(timezone.utc)
                session.add(payment)
                session.commit()
                
                await notify_payment_paid(payment)
                logging.info(f"Notificando pagamento pago: {transaction_code}")
                
                return {
                    "status": payment.status,
                    "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
                }
            
            # Se não estiver pago, verifica no Mercado Pago
            try:
                result = sdk.payment().get(transaction_code)
                mp_payment = result.get("response")
                
                if mp_payment and mp_payment["status"] == "approved":
                    payment.status = PaymentStatus.PAID
                    payment.paid_at = datetime.now(timezone.utc)
                    payment.qr_code_base64 = None
                    session.add(payment)
                    session.commit()
                    
                    await notify_payment_paid(payment)
                    logging.info(f"Pagamento {transaction_code} confirmado via Mercado Pago")
                    
                    return {
                        "status": payment.status,
                        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
                    }
                    
            except Exception as mp_error:
                logging.warning(f"Erro ao verificar pagamento no Mercado Pago: {mp_error}")
                # Continua mesmo com erro, pois pode ser um pagamento ainda pendente
            
            return {
                "status": payment.status,
                "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
            }

        except Exception as e:
            logging.error(f"Erro ao monitorar pagamento: {e}")
            raise HTTPException(status_code=500, detail="Erro interno")