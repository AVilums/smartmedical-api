from __future__ import annotations

import json
import logging
import sys
from typing import Any, Dict

from .config import get_settings


class PiiSafeFilter(logging.Filter):
    """Filter to prevent logging of sensitive fields in extra dicts."""

    SENSITIVE_KEYS = {"patient_name", "patient_id", "phone", "email", "personal_code"}

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        try:
            if hasattr(record, "extra") and isinstance(record.extra, dict):
                record.extra = {k: ("***" if k in self.SENSITIVE_KEYS else v) for k, v in record.extra.items()}
        except Exception:
            pass
        return True


def configure_logging() -> None:
    settings = get_settings()

    root = logging.getLogger()
    if root.handlers:
        # Avoid duplicate handlers in hot-reload
        for h in list(root.handlers):
            root.removeHandler(h)

    level = getattr(logging, settings.log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    if settings.log_json:
        class JsonFormatter(logging.Formatter):
            def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
                payload: Dict[str, Any] = {
                    "level": record.levelname,
                    "logger": record.name,
                    "message": record.getMessage(),
                    "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
                }
                if hasattr(record, "extra") and isinstance(getattr(record, "extra"), dict):
                    payload.update(record.extra)
                if record.exc_info:
                    payload["exc_info"] = self.formatException(record.exc_info)
                return json.dumps(payload, ensure_ascii=False)
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    handler.addFilter(PiiSafeFilter())
    root.addHandler(handler)
    root.setLevel(level)
