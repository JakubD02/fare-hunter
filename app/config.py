from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    redis_url: str = "redis://redis:6379/0"
    jwt_secret_key: str

    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    app_env: str = "development"
    log_level: str = "DEBUG"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
