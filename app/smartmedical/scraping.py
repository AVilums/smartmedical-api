"""Web scraping utilities for SmartMedical domain.

Currently provides a minimal fetch_timetable that logs in and navigates to the
calendar page, returning a confirmation payload with 35 days of placeholder
slots. Actual table scraping is not implemented yet.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from app.core.config import get_settings
from app.infrastructure.selenium_client import browser
from app.smartmedical.auth import login as sm_login
from app.smartmedical.navigation import navigate_to_timetable_nr10

def fetch_timetable(doctor: Optional[str] = None, date_str: Optional[str] = None) -> Dict[str, Any]:
    """Attempt to log in and navigate to the timetable page, then return
    a placeholder timetable covering 35 calendar days.

    - If SMARTMEDICAL_USERNAME/PASSWORD are provided, uses Selenium to log in
      and navigate to the calendar to confirm reachability.
    - If credentials are not provided or navigation fails, still returns the
      placeholder timetable (with a meta slot indicating the status).
    """
    settings = get_settings()

    reached_calendar = False
    login_attempted = False
    login_error: Optional[str] = None

    # Only attempt real login/navigation if credentials are available
    if settings.smartmedical_username and settings.smartmedical_password:
        login_attempted = True
        try:
            with browser() as driver:
                # Login using existing driver
                sm_login(driver=driver)
                # Navigate to timetable (Nr_10)
                navigate_to_timetable_nr10(driver)
                reached_calendar = True
        except Exception as e:
            login_error = str(e)
            reached_calendar = False

    # Compute base date
    if date_str:
        try:
            base_date = datetime.fromisoformat(date_str).date()
        except Exception:
            base_date = datetime.utcnow().date()
    else:
        base_date = datetime.utcnow().date()

    # Generate 35-day placeholder timetable
    days: List[Dict[str, Any]] = []
    example_times = ["09:00", "10:00", "11:00", "14:00", "15:00"]

    for i in range(35):
        d = base_date + timedelta(days=i)
        day_entry: Dict[str, Any] = {
            "date": d.isoformat(),
            "doctor": doctor or "Unknown Doctor",
            "times": [{"time": t, "available": True} for t in example_times],
        }
        days.append(day_entry)

    # We keep TimetableResponse lenient: slots is a list[dict]
    slots: List[Dict[str, Any]] = [{
        "meta": {
            "login_attempted": login_attempted,
            "reached_calendar": reached_calendar,
            **({"error": login_error} if login_error else {}),
        }
    }, *days]

    return {
        "doctor": doctor,
        "date": base_date.isoformat(),
        "slots": slots,
        "source": "smartmedical",
    }

def book(*args, **kwargs):
    raise NotImplementedError