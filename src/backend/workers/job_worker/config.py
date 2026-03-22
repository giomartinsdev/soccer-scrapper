"""Job worker configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    rabbitmq_url: str = "amqp://guest:guest@rabbitmq:5672//"
    bzzoiro_api_url: str = "https://sports.bzzoiro.com/api"
    bzzoiro_api_token: str = ""
    job_queue_name: str = "job.queue"
    persist_queue_name: str = "persist.queue"
    request_timeout: int = 30
    max_retries: int = 3
    retry_delay: int = 5


settings = Settings()
