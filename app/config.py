from __future__ import annotations

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Security
    # api_key: str = Field(alias="API_KEY")
    api_key: str = Field(default="dev-api-key", alias="API_KEY")  # Added default value
    bind_host: str = Field(default="127.0.0.1", alias="BIND_HOST")
    port: int = Field(default=8080, alias="PORT")

    # Rate limiting
    rate_limit_per_min: int = Field(default=30, alias="RATE_LIMIT_PER_MIN")
    rate_limit_burst: int = Field(default=60, alias="RATE_LIMIT_BURST")

    # CORS
    allowed_origins: List[str] = Field(default_factory=lambda: ["*"], alias="ALLOWED_ORIGINS")

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def _parse_allowed_origins(cls, v):
        if v is None:
            return ["*"]
        if isinstance(v, str):
            parts = [s.strip() for s in v.split(",")]
            return [p for p in parts if p]
        return v

    # Timeouts
    request_timeout: int = Field(default=60, alias="REQUEST_TIMEOUT")
    selenium_pageload_timeout: int = Field(default=30, alias="SELENIUM_PAGELOAD_TIMEOUT")
    selenium_implicit_wait: int = Field(default=5, alias="SELENIUM_IMPLICIT_WAIT")

    # Selenium / Browser
    browser: str = Field(default="headless-chrome", alias="BROWSER")
    chrome_binary_path: str | None = Field(default=None, alias="CHROME_BINARY_PATH")
    chromedriver_path: str | None = Field(default=None, alias="CHROMEDRIVER_PATH")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=False, alias="LOG_JSON")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # reads from env/.env
