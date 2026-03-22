"""Job API configuration."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    host: str = "0.0.0.0"
    port: int = 8001
    debug: bool = False
    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"
    job_queue_name: str = "job.queue"


settings = Settings()
