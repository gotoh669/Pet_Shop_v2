import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Pet Shop API")
    api_prefix: str = os.getenv("API_PREFIX", "/api/v1")
    database_url: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./pet_shop_v2.db",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")
    secret_key: str = os.getenv("SECRET_KEY", "pet-shop-v2-dev-secret-change-me")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    sms_code_expire_minutes: int = int(os.getenv("SMS_CODE_EXPIRE_MINUTES", "5"))
    sms_provider: str = os.getenv("SMS_PROVIDER", "mock")
    sms_debug_return_code: bool = os.getenv("SMS_DEBUG_RETURN_CODE", "false").lower() == "true"
    sms_http_url: str = os.getenv("SMS_HTTP_URL", "")
    sms_http_token: str = os.getenv("SMS_HTTP_TOKEN", "")
    aliyun_sms_access_key_id: str = os.getenv("ALIYUN_SMS_ACCESS_KEY_ID", "")
    aliyun_sms_access_key_secret: str = os.getenv("ALIYUN_SMS_ACCESS_KEY_SECRET", "")
    aliyun_sms_sign_name: str = os.getenv("ALIYUN_SMS_SIGN_NAME", "")
    aliyun_sms_template_code: str = os.getenv("ALIYUN_SMS_TEMPLATE_CODE", "")
    aliyun_sms_endpoint: str = os.getenv("ALIYUN_SMS_ENDPOINT", "https://dysmsapi.aliyuncs.com/")
    aliyun_sms_region_id: str = os.getenv("ALIYUN_SMS_REGION_ID", "cn-hangzhou")
    cors_allow_origins: str = os.getenv("CORS_ALLOW_ORIGINS", "*")
    auto_create_tables: bool = os.getenv("AUTO_CREATE_TABLES", "true").lower() == "true"
    default_admin_phone: str = os.getenv("DEFAULT_ADMIN_PHONE", "18800000000")


settings = Settings()
