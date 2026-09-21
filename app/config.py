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

    # sendgrid
    SENDGRID_API_KEY: str
    FROM_EMAIL: str = "noreply@fareh\u200bunter.app"
    APP_URL: str = "http://localhost:8000"

    APP_ENV: str = "development"
    LOG_LEVEL: str = "DEBUG"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
