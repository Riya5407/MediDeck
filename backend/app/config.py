from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/medidesk"
    DATABASE_URL_TEST: str = "postgresql://user:password@localhost:5432/medidesk_test"
    LOW_STOCK_THRESHOLD: int = 20
    EXPIRY_WARNING_DAYS: int = 30
    PAYMENT_MODES: str = "Cash,Card,UPI"
    CORS_ORIGINS: str = "http://localhost:5173"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
