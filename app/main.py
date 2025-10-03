from __future__ import annotations

import uvicorn
from app.config import get_settings

# Re-export FastAPI app built in the new API layer
from app.api.app import app  # noqa: F401


if __name__ == "__main__":
    s = get_settings()
    uvicorn.run("app.main:app", host=s.bind_host, port=s.port, reload=False, log_level="info")
