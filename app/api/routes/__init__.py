from app.auth.auth import AuthRouter
from app.api.routes.company.home import HomeRouter
from app.api.routes.admin.users import AdminRouter
from app.api.routes.company.company import CompanyRouter
from app.api.routes.company.register import RegisterRouter
from app.api.routes.user.users import UserRouter
from app.api.routes.service.service import ServiceRouter
from app.api.routes.service.category_service import CategoryServiceRouter
from app.api.routes.schedule.schedule import ScheduleRouter
from app.api.routes.schedule.schedule_slot import ScheduleSlotRouter
from app.api.routes.product.category_product import CategoryProductRouter
from app.api.routes.product.product import ProductRouter
from app.api.routes.payment.payment import PaymentRouter 
from app.api.routes.plan.plan import PlanRouter
from app.api.routes.finance.finance import FinanceRouter
from app.api.routes.finance.finance_category import FinanceCategoryRouter
from app.api.routes.credit.credit import CreditRouter
from app.api.routes.payment.payment_pix import PixRouter
from app.api.routes.chat.token_status import TokenStatusRouter
from app.api.routes.chat.chat import ChatRouter
from app.api.routes.chat.assistant import AssistantRouter
from app.api.routes.chat.interaction import InteractionRouter
from app.api.routes.google.google_calendar import GoogleCalendarRouter
from app.api.routes.analytics.analytics import AnalyticsRouter

def register_routes(app):
    app.include_router(HomeRouter())

    app.include_router(AuthRouter())
    app.include_router(AdminRouter())
    app.include_router(UserRouter())
    app.include_router(CompanyRouter())
    app.include_router(RegisterRouter())

    app.include_router(CategoryProductRouter())
    app.include_router(ProductRouter())

    app.include_router(CategoryServiceRouter())
    app.include_router(ServiceRouter())
    app.include_router(ScheduleRouter())
    app.include_router(ScheduleSlotRouter())

    app.include_router(TokenStatusRouter())
    app.include_router(ChatRouter())
    app.include_router(AssistantRouter())
    app.include_router(InteractionRouter())

    app.include_router(PaymentRouter())
    app.include_router(PlanRouter())
    app.include_router(PixRouter())

    app.include_router(CreditRouter())
    app.include_router(FinanceCategoryRouter())
    app.include_router(FinanceRouter())
    
    app.include_router(AnalyticsRouter())

    app.include_router(GoogleCalendarRouter())
