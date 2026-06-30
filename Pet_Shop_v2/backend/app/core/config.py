import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://pet_shop:change_me@127.0.0.1:3306/pet_shop_v2?charset=utf8mb4",
    )
    redis_url: str = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
    deepseek_api_key: str = os.getenv("DEEPSEEK_API_KEY", "")


settings = Settings()
