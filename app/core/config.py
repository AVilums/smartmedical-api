from __future__ import annotations

from functools import lru_cache
from typing import List
import os
import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Security
    api_key: str = Field(default="dev-api-key", alias="API_KEY")
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
    selenium_remote_url: str | None = Field(default=None, alias="SELENIUM_REMOTE_URL")

    # SmartMedical
    smartmedical_base_url: str = Field(default="https://vm528.smartmedical.eu/", alias="SMARTMEDICAL_BASE_URL")
    smartmedical_username: str | None = Field(default=None, alias="SMARTMEDICAL_USERNAME")
    smartmedical_password: str | None = Field(default=None, alias="SMARTMEDICAL_PASSWORD")
    smartmedical_login_on_timetable: bool = Field(default=True, alias="SMARTMEDICAL_LOGIN_ON_TIMETABLE")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=False, alias="LOG_JSON")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> "Settings":
    # Normalize ALLOWED_ORIGINS to JSON array if a simple string is provided in env
    val = os.environ.get("ALLOWED_ORIGINS")
    if isinstance(val, str):
        s = val.strip()
        # If user provided '*' or comma-separated list like 'http://a, http://b',
        # convert it to a JSON array string so pydantic_settings won't try to json.loads('*').
        if s and not s.startswith("["):
            if s == "*":
                os.environ["ALLOWED_ORIGINS"] = json.dumps(["*"])
            else:
                parts = [p.strip() for p in s.split(",")]
                parts = [p for p in parts if p]
                if parts:
                    os.environ["ALLOWED_ORIGINS"] = json.dumps(parts)
    return Settings()  # reads from env/.env
