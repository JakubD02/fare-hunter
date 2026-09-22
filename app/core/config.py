from typing import ClassVar

from celery.schedules import crontab
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # database
    DATABASE_URL: str

    # redis & celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # jwt
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # serpapi
    SERPAPI_KEY: str
    SERPAPI_URL: str = "https://serpapi.com/api"

    # sendgrid
    SENDGRID_API_KEY: str
    FROM_EMAIL: str = "noreply@fareh\u200bunter.app"
    APP_URL: str = "http://localhost:8000"

    # app
    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"

    # celery beat schedule
    CELERY_BEAT_SCHEDULE: ClassVar[dict] = {
        "fetch-prices-every-8h": {
            "task": "app.tasks.price_tasks.fetch_all_prices_periodic",
            "schedule": crontab(minute=0, hour="*/8"),
        }
    }

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
