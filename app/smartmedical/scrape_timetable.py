"""Web scraping utilities for SmartMedical domain.

Currently provides a minimal fetch_timetable that logs in and navigates to the
calendar page, returning a confirmation payload with 35 days of placeholder
slots. Actual table scraping is not implemented yet.
"""
from __future__ import annotations

import re
import time
from typing import Any, Dict, List, Optional, Tuple
from datetime import date
from math import gcd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.core.config import get_settings
from app.infrastructure.selenium_client import browser
from app.smartmedical.auth import login as sm_login
from app.smartmedical.navigation import navigate_to_timetable_nr10
from app.smartmedical import selectors as sm_sel

def fetch_timetable() -> Dict[str, Any]:
    """Fetch free timetable slots for the next 5 weeks from SmartMedical.

    Simplified per requirements: just scrape the current week and then click
    "next week" 4 times. No filters, no signatures, no placeholders.
    """
    settings = get_settings()
    scraped_slots: List[Dict[str, Any]] = []

    if not (settings.smartmedical_username and settings.smartmedical_password):
        raise ValueError("SmartMedical credentials are not provided (username/password).")

    with browser() as driver:
        sm_login(driver=driver)
        navigate_to_timetable_nr10(driver)

        for i in range(5):
            week_free, _ = _scrape_week(driver, settings)
            scraped_slots.extend(week_free)

            if i < 4:
                try:
                    next_btn = driver.find_element(By.XPATH, sm_sel.XPATH_WEEK_NEXT_BUTTON)
                    try:
                        driver.execute_script("arguments[0].click();", next_btn)
                    except Exception:
                        next_btn.click()
                    time.sleep(1.0)
                except Exception:
                    break

    # Filter out slots with dates that have already passed
    today_iso = date.today().isoformat()
    future_slots = [s for s in scraped_slots if isinstance(s, dict) and s.get("date") and s["date"] >= today_iso]

    return {
        "doctor": None,
        "date": None,
        "slots": future_slots,
        "source": "smartmedical",
    }


def _scrape_week(driver, settings) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Scrape a single week and compute free intervals per day.

    Algorithm per requirements:
    - Potential intervals per day come from elements //div[@class='WorkTimeNotEditable'].
    - Occupied intervals per day come from elements //div[@class='Reservation'].
    - Free intervals = union(Potential) minus union(Occupied), computed per day.
    """
    wait = WebDriverWait(driver, settings.request_timeout)
    try:
        # Wait for at least the potential work time elements to appear (best-effort)
        wait.until(EC.presence_of_all_elements_located((By.XPATH, sm_sel.XPATH_ALL_TIMESLOTS)))
    except Exception:
        pass

    all_elems = driver.find_elements(By.XPATH, sm_sel.XPATH_ALL_TIMESLOTS)
    res_elems = driver.find_elements(By.XPATH, sm_sel.XPATH_ALL_RESERVATIONS)

    # Keyed by (date, doctor)
    pot_map: Dict[Tuple[str, Optional[str]], List[Tuple[int, int]]] = {}
    res_map: Dict[Tuple[str, Optional[str]], List[Tuple[int, int]]] = {}
    # Reservations with no doctor parsed will be subtracted from all doctors on that date
    res_unknown_by_date: Dict[str, List[Tuple[int, int]]] = {}

    week_dates: set[str] = set()

    # Collect potential intervals from WorkTimeNotEditable
    for el in all_elems:
        try:
            title = el.get_attribute("title") or ""
            elem_id = el.get_attribute("id") or ""
            start_s, end_s, doc = _parse_time_range_and_doctor_from_work(title)
            date = _extract_date_from_id(elem_id) or _closest_date_via_dom(driver, el)
            if not (start_s and end_s and date):
                continue
            start_m, end_m = _to_minutes(start_s), _to_minutes(end_s)
            if start_m is None or end_m is None or end_m <= start_m:
                continue
            doc = (doc or "").strip() or None
            week_dates.add(date)
            pot_map.setdefault((date, doc), []).append((start_m, end_m))
        except Exception:
            continue

    # Collect occupied intervals from Reservation
    for el in res_elems:
        try:
            title = el.get_attribute("title") or ""
            start_s, end_s, doc = _parse_time_range_and_doctor_from_res(title)
            # Try to resolve date via DOM proximity
            date = _closest_date_via_dom(driver, el)
            if not date:
                try:
                    container = el.find_element(By.XPATH, "./ancestor::*[@id][1]")
                    date = _extract_date_from_id(container.get_attribute("id"))
                except Exception:
                    date = None
            if not (start_s and end_s and date):
                continue
            start_m, end_m = _to_minutes(start_s), _to_minutes(end_s)
            if start_m is None or end_m is None or end_m <= start_m:
                continue
            week_dates.add(date)
            doc = (doc or "").strip() or None
            if doc is None:
                res_unknown_by_date.setdefault(date, []).append((start_m, end_m))
            else:
                res_map.setdefault((date, doc), []).append((start_m, end_m))
        except Exception:
            continue

    # Infer base interval per (date, doctor) from raw potentials and reservations
    interval_map: Dict[Tuple[str, Optional[str]], Optional[int]] = {}
    for key, pots in pot_map.items():
        d, doc = key
        occ_for_doc = res_map.get((d, doc), [])
        occ_unknown = res_unknown_by_date.get(d, [])
        interval_map[key] = _infer_interval(pots, occ_for_doc + occ_unknown)

    # Compute free intervals per (date, doctor): union(potential) - union(reservations)
    free_slots: List[Dict[str, Any]] = []
    # Determine all doctor keys present in potentials
    for (date, doc) in sorted(pot_map.keys(), key=lambda k: (k[0], k[1] or "")):
        pot = _merge_intervals(pot_map.get((date, doc), []))
        # Reservations for this doctor
        occ_for_doc = _merge_intervals(res_map.get((date, doc), []))
        # Plus any unknown reservations that should block all doctors that day
        occ_unknown = _merge_intervals(res_unknown_by_date.get(date, []))
        # Merge both occupied sets
        occ = _merge_intervals(occ_for_doc + occ_unknown)
        free = _subtract_intervals(pot, occ)
        inferred = interval_map.get((date, doc))
        for start_m, end_m in free:
            slot = {
                "date": date,
                "start": _to_hhmm(start_m),
                "end": _to_hhmm(end_m),
                "doctor": doc,
                "type": "free",
            }
            if inferred is not None:
                slot["interval"] = str(inferred)
            free_slots.append(slot)

    return free_slots, sorted(week_dates)


def _parse_time_range_and_doctor_from_work(title: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    # Example: "15:40 - 16:00 Sandra Milta"
    if not title:
        return None, None, None
    m = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})\s*(.*)", title)
    if not m:
        return None, None, None
    start, end, doc = m.group(1), m.group(2), (m.group(3) or '').strip()
    return start, end, doc


def _parse_time_range_and_doctor_from_res(title: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    # Example: "PĒTERIS OLIŅŠ [17] 15:20- 15:40 Tips: Sandra Milta"
    if not title:
        return None, None, None
    tm = re.search(r"(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})", title)
    doc = None
    dm = re.search(r"Tips:\s*(.+)$", title)
    if dm:
        doc = dm.group(1).strip()
    if tm:
        return tm.group(1), tm.group(2), doc
    return None, None, doc


def _extract_date_from_id(elem_id: Optional[str]) -> Optional[str]:
    if not elem_id:
        return None
    m = re.search(r"(\d{4}-\d{2}-\d{2})", elem_id)
    return m.group(1) if m else None


def _closest_date_via_dom(driver, element) -> Optional[str]:
    try:
        return driver.execute_script(
            """
            var el = arguments[0];
            for (var i=0; i<10 && el; i++) {
              if (el.id && /(\\d{4}-\\d{2}-\\d{2})/.test(el.id)) {
                var m = el.id.match(/(\\d{4}-\\d{2}-\\d{2})/);
                if (m) return m[1];
              }
              el = el.parentElement;
            }
            return null;
            """,
            element,
        )
    except Exception:
        return None

# ----- Interval utilities -----

def _to_minutes(t: str) -> Optional[int]:
    """Convert HH:MM to minutes since midnight. Returns None if invalid.
    Accepts H:MM or HH:MM. Allows 24:00 as 1440.
    """
    try:
        if not t or ":" not in t:
            return None
        h_s, m_s = t.strip().split(":", 1)
        h, m = int(h_s), int(m_s)
        if h == 24 and m == 0:
            return 24 * 60
        if not (0 <= h <= 23 and 0 <= m <= 59):
            return None
        return h * 60 + m
    except Exception:
        return None


def _to_hhmm(total_minutes: int) -> str:
    """Convert minutes since midnight to HH:MM string. Supports 1440 -> 24:00."""
    if total_minutes >= 24 * 60:
        return "24:00"
    if total_minutes < 0:
        total_minutes = 0
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h:02d}:{m:02d}"


def _merge_intervals(intervals: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Merge overlapping or contiguous intervals.
    Intervals are (start, end) in minutes. Assumes end > start per interval.
    """
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda x: (x[0], x[1]))
    merged: List[Tuple[int, int]] = []
    cs, ce = intervals[0]
    for s, e in intervals[1:]:
        if s <= ce:  # overlap or contiguous
            ce = max(ce, e)
        else:
            merged.append((cs, ce))
            cs, ce = s, e
    merged.append((cs, ce))
    return merged


def _subtract_intervals(potentials: List[Tuple[int, int]], occupied: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Subtract occupied intervals from potentials.
    Returns list of free intervals (in minutes), non-overlapping and sorted.
    """
    if not potentials:
        return []
    occ = _merge_intervals(occupied)
    result: List[Tuple[int, int]] = []
    for ps, pe in _merge_intervals(potentials):
        cur = ps
        for os, oe in occ:
            if oe <= cur:
                continue
            if os >= pe:
                break
            if os > cur:
                result.append((cur, min(os, pe)))
            cur = max(cur, min(oe, pe))
            if cur >= pe:
                break
        if cur < pe:
            result.append((cur, pe))
    return result


def _infer_interval(
    potentials: List[Tuple[int, int]],
    occupied: List[Tuple[int, int]]
) -> Optional[int]:
    """Infer base timeslot interval from potential and occupied time blocks."""
    # Calculate durations from both potentials and occupied blocks
    durations: List[int] = [
        e - s for seq in (potentials, occupied) for s, e in seq if e > s
    ]
    # Filter out implausible durations
    durations = [d for d in durations if 5 <= d <= 180]
    if not durations:
        return None

    # Compute GCD of durations and prefer sane range (10 to 60 mins)
    g = durations[0]
    for d in durations[1:]:
        g = gcd(g, d)
        if g == 1:  # No meaningful GCD, break early
            break

    return g if 10 <= g <= 60 else min(durations)  # Fallback to minimum plausible duration