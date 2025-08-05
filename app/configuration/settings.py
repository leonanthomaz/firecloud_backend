import logging
import os
import redis
from dotenv import load_dotenv

# Configuração de logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Carrega as variáveis de ambiente
load_dotenv(dotenv_path=".env", encoding="utf-8")

# Silencia logs de SQLAlchemy
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

class Configuration:
    def __init__(self):
        
        # Url base
        self.base_url = os.getenv("APP_WEB_URL", "http://localhost:3000")
        self.url_notifications_pix = os.getenv("PAY_URL_NOTIFICATIONS_PIX", "http://localhost:3000")
        
        self.google_client_id = os.getenv("GOOGLE_ID_CLIENT")
        self.google_client_secret = os.getenv("GOOGLE_SECRET_KEY")
        self.google_client_redirect = os.getenv("GOOGLE_REDIRECT_URI")

        # Carrega as variáveis de ambiente
        self.ia_provider = os.getenv("IA_PROVIDER", "mock").lower()
        
        # Assistente
        self.assistant_name = os.getenv("ASSISTANT_NAME")
        self.assistant_user = os.getenv("ASSISTANT_USER")

        # IA - DEEPSEEK
        self.deepseek_url = os.getenv("DEEPSEEK_URL")
        self.deepseek_model = os.getenv("DEEPSEEK_MODEL")
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

        # IA - OPENAI
        self.openassistant_api_key = os.getenv("OPENassistant_api_key")
        self.openai_base_url = "https://openrouter.ai/api/v1"

        # IA - GEMINI
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")

        # Configurações do ambiente e banco de dados
        self.environment = os.getenv("APP_ENVIRONMENT_DEFAULT", "development").lower()
        
        # Email
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        
        # POSTGRES PRODUCTION
        self.db_user = os.getenv("DB_USER")
        self.db_password = os.getenv("DB_PASSWORD")
        self.db_host = os.getenv("DB_HOST")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME")
        
        # POSTGRES
        self.db_dev_user = os.getenv("DB_DEV_USER")
        self.db_dev_password = os.getenv("DB_DEV_PASSWORD")
        self.db_dev_host = os.getenv("DB_DEV_HOST")
        self.db_dev_port = os.getenv("DB_DEV_PORT", "5432")
        self.db_dev_name = os.getenv("DB_DEV_NAME")
        
        self.endpoint_url_r2 = os.getenv("ENDPOINT_CLOUDFLARE_R2")
        self.aws_access_key_id_aws = os.getenv("AWS_ACCESS_KEY_ID")
        self.aws_secret_access_key_aws = os.getenv("AWS_SECRET_ACCESS_KEY_ID")
        self.r2_bucket_name = os.getenv("R2_BUCKET_NAME")
        self.r2_url_public = os.getenv("ENDPOINT_PUBLIC_R2")
        
        self.facebook_phone_number_id = os.getenv("FACEBOOK_PHONE_NUMBER_ID")
        self.facebook_secret_key = os.getenv("FACEBOOK_SECRET_KEY")
        self.facebook_access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.facebook_number = os.getenv("FACEBOOK_NUMBER")
        
        self.mercado_pago_access_token_prod = os.getenv("MERCADO_PAGO_ACCESS_TOKEN_PROD")
        self.mercado_pago_access_token_test = os.getenv("MERCADO_PAGO_ACCESS_TOKEN_TEST")
                    
    def get_redis_client(self):
        """Retorna uma instância do cliente Redis configurado."""
        return redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            username=os.getenv("REDIS_USERNAME", ""),
            password=os.getenv("REDIS_PASSWORD", ""),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True
        )

    def connect_to_postgresql(self):
        # Montar a URL de conexão corretamente
        db_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        logging.info(f"BANCO DE DADOS >>> URL - DB PRODUÇÃO: {db_url}")
        return db_url
    
    def connect_to_postgresql_dev(self):
        # Montar a URL de conexão corretamente
        db_url = f"postgresql://{self.db_dev_user}:{self.db_dev_password}@{self.db_dev_host}:{self.db_dev_port}/{self.db_dev_name}"
        logging.info(f"BANCO DE DADOS >>> URL - DB DESENVOLVIMENTO: {db_url}")
        return db_url
    