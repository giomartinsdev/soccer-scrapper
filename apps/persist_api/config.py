"""Persist API configuration."""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(env_file=".env", extra="allow")

    host: str = "0.0.0.0"
    port: int = 8002
    debug: bool = False
    mongodb_url: str = "mongodb://mongodb:27017"
    mongodb_db: str = "soccer_scrapper"


settings = Settings()
