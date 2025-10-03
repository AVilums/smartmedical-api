from __future__ import annotations

# Thin dependency layer to allow future expansion (DB/session, etc.)
from app.infrastructure.security import API_KEY_HEADER, get_api_key, principal_id  # re-export for routers

__all__ = [
    "API_KEY_HEADER",
    "get_api_key",
    "principal_id",
]
