from __future__ import annotations

import hashlib
from typing import Optional

from fastapi import Depends, Header, HTTPException, status

from app.core.config import get_settings

API_KEY_HEADER = "X-API-Key"


def get_api_key(x_api_key: Optional[str] = Header(default=None, alias=API_KEY_HEADER)) -> str:
    settings = get_settings()
    if not x_api_key or x_api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")
    return x_api_key


def principal_id(api_key: str = Depends(get_api_key)) -> str:
    """Return a stable identifier derived from the API key for rate limiting and logging."""
    return hashlib.sha256(api_key.encode("utf-8")).hexdigest()[:16]
