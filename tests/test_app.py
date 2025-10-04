import importlib
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.local


def make_client(env: dict) -> TestClient:
    os.environ.update(env)
    # Clear cached settings and limiter singleton before import
    import app.core.config as cfg
    import app.infrastructure.rate_limit as rl
    cfg.get_settings.cache_clear()  # type: ignore[attr-defined]
    rl._limiter = None  # type: ignore[attr-defined]

    # Reload main to apply new settings at import time
    if 'app.main' in list(importlib.sys.modules.keys()):
        importlib.reload(importlib.import_module('app.main'))
    else:
        import app.main  # noqa: F401
    from app.main import app
    return TestClient(app)


def test_health_ok():
    client = make_client({
        'API_KEY': 'test-key',
        'BIND_HOST': '127.0.0.1',
        'PORT': '0',
    })
    resp = client.get('/health')
    assert resp.status_code == 200
    assert resp.json() == {'status': 'ok'}


def test_auth_required():
    client = make_client({'API_KEY': 'test-key'})
    # No API key
    r1 = client.get('/timetable')
    assert r1.status_code == 401
    # Wrong API key
    r2 = client.get('/timetable', headers={'X-API-Key': 'wrong'})
    assert r2.status_code == 401


def test_timetable_requires_credentials_or_scrapes():
    client = make_client({'API_KEY': 'test-key'})
    r = client.get('/timetable', headers={'X-API-Key': 'test-key'})
    # Without credentials, we expect 501; with credentials, 200
    if r.status_code == 200:
        body = r.json()
        assert body.get('source') == 'smartmedical'
        assert isinstance(body.get('slots'), list)
    else:
        assert r.status_code == 501
        body = r.json()
        assert 'detail' in body


def test_rate_limit_exceeded():
    client = make_client({'API_KEY': 'test-key', 'RATE_LIMIT_PER_MIN': '1', 'RATE_LIMIT_BURST': '1'})
    # The first request should pass (returns 501 because not implemented)
    r1 = client.get('/timetable', headers={'X-API-Key': 'test-key'})
    assert r1.status_code in (501, 200)
    # The second immediate request should be rate limited
    r2 = client.get('/timetable', headers={'X-API-Key': 'test-key'})
    assert r2.status_code == 429
