from typing import ClassVar

from celery.schedules import crontab
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AirlineConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    # IATA, 2-character code used comercially (e.g. LO, U2)
    iata_code_length: int = 2
    # ICAO, 3-letter code used for air traffic control (e.g. LOT, DLH)
    icao_code_length: int = 3
    name_min_length: int = 3
    name_max_length: int = 100


class AirportConfig(BaseModel):
    model_config = ConfigDict(frozen=True)
    # Airports codes (e.g. WAW, JFK)
    iata_code_length: int = 3

    # 4-letter code used for air traffic control (e.g. EPWA, KJFK)
    icao_code_length: int = 4

    # Airports name
    name_min_length: int = 3
    name_max_length: int = 100

    # City name
    city_min_length: int = 2
    city_max_length: int = 100

    # Country name
    country_min_length: int = 2
    country_max_length: int = 60

    # Country code (Exactly 2 letters e.g. "PL", "GB", "US")
    country_code_length: int = 2


class MockConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    mock_num_results: int = 5
    mock_total_generated: int = 20

    mock_price_min: int = 400
    mock_price_max: int = 1500


class PriceConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    price_max_digits: int = 10
    price_decimal_places: int = 2

    price_min_value: int = 1


class UserConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    first_name_min_length: int = 3
    first_name_max_length: int = 50

    email_max_length: int = 255

    password_min_length: int = 8
    password_max_length: int = 72
    password_hash_max_length: int = 255


class PaginationConfig(BaseModel):
    model_config = ConfigDict(frozen=True)

    default_limit: int = 20
    max_limit: int = 100
    min_limit: int = 1
    default_offset: int = 0
    min_offset: int = 0


class Settings(BaseSettings):
    # database
    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5434/fare_hunter"

    # redis & celery
    REDIS_URL: str = "redis://localhost:6379/0"

    # jwt
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # constants
    airline: AirlineConfig = AirlineConfig()
    airports: AirportConfig = AirportConfig()
    mock: MockConfig = MockConfig()
    price: PriceConfig = PriceConfig()
    user_config: UserConfig = UserConfig()
    pagination: PaginationConfig = PaginationConfig()

    # serpapi
    SERPAPI_KEY: str
    SERPAPI_URL: str = "https://serpapi.com"

    # sendgrid
    SENDGRID_API_KEY: str
    FROM_EMAIL: EmailStr = Field(default="noreply@farehunter.app", validate_default=True)
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
