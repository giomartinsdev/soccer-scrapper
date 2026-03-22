"""Persist worker configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    mongodb_url: str = "mongodb://mongodb:27017"
    mongodb_db: str = "soccer_scrapper"
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"
    persist_queue_name: str = "persist.queue"
    batch_size: int = 100
    upsert_enabled: bool = True


settings = Settings()
