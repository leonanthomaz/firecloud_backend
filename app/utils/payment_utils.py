
import logging
from app.configuration.settings import Configuration
from app.tasks.websockets.ws_manager import payment_ws_manager
from app.models.payment.payment import Payment

Configuration()

async def notify_payment_paid(payment: Payment):
    logging.info(f"Notificando pagamento pago: {payment.transaction_code}")
    
    notification_data = {
        "type": "payment_status",
        "transaction_code": payment.transaction_code,
        "status": payment.status,
        "paid_at": payment.paid_at.isoformat() if payment.paid_at else None
    }
    
    await payment_ws_manager.broadcast(notification_data)
    
    # Aqui você pode adicionar outras notificações (email, etc.)