from __future__ import annotations
from typing import Any, Dict, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.core.config import get_settings
from app.infrastructure.selenium_client import browser
from app.smartmedical.auth import login as sm_login
from app.smartmedical.navigation import navigate_to_timetable_nr10
from app.smartmedical import selectors as sm_sel
from app.smartmedical.scrape_timetable import _scrape_week, _to_minutes, _parse_time_range_and_doctor_from_work


def _find_clickable_timeslot_for(driver, want_date: str, want_time: str):
    """Find a WorkTimeNotEditable element that covers the requested date/time.
    Returns the element or None.
    """
    elems = driver.find_elements(By.XPATH, sm_sel.XPATH_ALL_TIMESLOTS)
    want_min = _to_minutes(want_time)
    if want_min is None:
        return None

    for el in elems:
        try:
            title = el.get_attribute("title") or ""
            elem_id = el.get_attribute("id") or ""
            start_s, end_s, _doc = _parse_time_range_and_doctor_from_work(title)
            # Determine date from id or by walking DOM (same heuristics as scraping)
            from app.smartmedical.scrape_timetable import _extract_date_from_id, _closest_date_via_dom
            date = _extract_date_from_id(elem_id) or _closest_date_via_dom(driver, el)
            if not (start_s and end_s and date):
                continue
            if date != want_date:
                continue
            s_min = _to_minutes(start_s)
            e_min = _to_minutes(end_s)
            if s_min is None or e_min is None:
                continue
            if s_min <= want_min < e_min:
                return el
        except Exception:
            continue
    return None


def create_booking(
    *,
    date: str,
    time: str,
    first_name: str,
    last_name: str,
    phone: str,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a booking at SmartMedical calendar for the given date/time.

    Steps:
    - Login and navigate to the timetable (Nr_10)
    - Ensure the week containing `date` is visible (advance up to 5 weeks)
    - Check availability using scraping helpers (no overlapping Reservation)
    - Click the corresponding WorkTimeNotEditable slot
    - Switch to reservation iframe and fill patient details (name, surname, notes)

    Returns a dict compatible with BookingResponse: {status, booking_id?, message?}
    """
    settings = get_settings()

    if not (settings.smartmedical_username and settings.smartmedical_password):
        return {"status": "error", "message": "SmartMedical credentials are not provided (username/password)."}

    with browser() as driver:
        # Authenticate and navigate
        sm_login(driver=driver)
        navigate_to_timetable_nr10(driver)

        # Try up to 5 weeks to locate the requested date
        found_week = False
        available = False
        for i in range(5):
            free_slots, week_dates = _scrape_week(driver, settings)
            if date in week_dates:
                found_week = True
                # Determine if requested time is within a free interval for the date
                want_min = _to_minutes(time)
                if want_min is None:
                    return {"status": "error", "message": f"Invalid time format: {time}"}
                for s in free_slots:
                    try:
                        if s.get("date") == date:
                            s_min = _to_minutes(s.get("start"))
                            e_min = _to_minutes(s.get("end"))
                            if s_min is not None and e_min is not None and s_min <= want_min < e_min:
                                available = True
                                break
                    except Exception:
                        continue
                break
            # Advance to next week if not yet found
            try:
                next_btn = driver.find_element(By.XPATH, sm_sel.XPATH_WEEK_NEXT_BUTTON)
                driver.execute_script("arguments[0].click();", next_btn)
                import time as _t; _t.sleep(0.8)
            except Exception:
                break

        if not found_week:
            return {"status": "error", "message": f"Requested date {date} not visible in calendar."}
        if not available:
            return {"status": "unavailable", "message": f"No free slot at {date} {time}."}

        # Click a suitable timeslot element that covers the desired time
        el = _find_clickable_timeslot_for(driver, date, time)
        if el is None:
            return {"status": "error", "message": "Could not locate a clickable timeslot element."}
        try:
            try:
                el.click()
            except Exception:
                driver.execute_script("arguments[0].click();", el)
        except Exception:
            return {"status": "error", "message": "Failed to click on the timeslot element."}

        # Wait for reservation iframe and switch to it
        wait = WebDriverWait(driver, settings.request_timeout)
        try:
            # Ensure we are in top-level context where the popup iframe is usually injected
            try:
                driver.switch_to.default_content()
            except Exception:
                pass
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, sm_sel.XPATH_RESERVATION_IFRAME)))
        except Exception:
            return {"status": "error", "message": "Reservation iframe did not appear."}

        # Locate the time_from field in the reservation form and verify it matches
        time_from_field = wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_TIME_FROM)))
        time_from_value = time_from_field.get_attribute("value")

        if time_from_value != time: return {"status": "error", "message": "Reservation form time_from field does not match."}

        # Fill in name, surname, and notes
        try:
            fn = wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_INPUT_FIRST_NAME)))
            ln = wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_INPUT_LAST_NAME)))
            pn = wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_INPUT_PHONE)))
            nt = wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_TEXTAREA_NOTES)))
            try:
                pn.clear(); fn.clear(); ln.clear(); nt.clear()
            except Exception:
                pass
            fn.send_keys(first_name)
            ln.send_keys(last_name)
            pn.send_keys(phone)
            if notes: nt.send_keys(notes)
        except Exception:
            return {"status": "error", "message": "Failed to fill reservation form fields."}

        # Press submit
        try:
            save_btn = wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_SAVE_BUTTON)))
            driver.execute_script("arguments[0].click();", save_btn)
        except Exception:
            return {"status": "error", "message": "Failed to submit the reservation form."}

        # Consider the booking initiated
        return {"status": "ok", "message": "Reservation form submitted successfully."}
