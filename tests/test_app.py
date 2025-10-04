import importlib
import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient


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


def test_timetable_implemented_returns_placeholder():
    client = make_client({'API_KEY': 'test-key'})
    r = client.get('/timetable', headers={'X-API-Key': 'test-key'})
    assert r.status_code == 200
    body = r.json()
    assert body.get('source') == 'smartmedical'
    assert isinstance(body.get('slots'), list)
    # Expect at least 35 days worth of entries (plus optional meta)
    assert len(body['slots']) >= 35


def test_book_not_implemented():
    client = make_client({'API_KEY': 'test-key'})
    payload = {
        'doctor': 'Dr X',
        'date': '2025-12-01',
        'time': '10:30',
        'patient': {'first_name': 'A', 'last_name': 'B'}
    }
    r = client.post('/book', headers={'X-API-Key': 'test-key'}, json=payload)
    assert r.status_code == 501
    body = r.json()
    assert 'error' in body


def test_rate_limit_exceeded():
    client = make_client({'API_KEY': 'test-key', 'RATE_LIMIT_PER_MIN': '1', 'RATE_LIMIT_BURST': '1'})
    # First request should pass (returns 501 because not implemented)
    r1 = client.get('/timetable', headers={'X-API-Key': 'test-key'})
    assert r1.status_code in (501, 200)
    # Second immediate request should be rate limited
    r2 = client.get('/timetable', headers={'X-API-Key': 'test-key'})
    assert r2.status_code == 429
