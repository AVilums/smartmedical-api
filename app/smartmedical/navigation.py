"""Navigation utilities for SmartMedical portal.

Provides functions to move from the main (post-login) page to the timetable/calendar
view for a specific department/doctor entry.

Current flow implemented:
- Directly click the hidden Timetable link with id `sm-31` (no hover required).
- Click the Nr_10 row (id `item-77-0`) to reach the calendar.

These functions expect that authentication has already been performed and that the
post-login page is loaded.
"""
from __future__ import annotations

import time
from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from app.core.config import get_settings
from app.smartmedical import selectors as sm_sel


def _wait_for_calendar_loaded(driver, timeout: int) -> bool:
    """Heuristic wait until a calendar/timetable view seems loaded.

    Tries multiple known calendar container XPaths and also checks URL hints.
    """
    end = time.time() + timeout
    last_url = None
    while time.time() < end:
        # Element candidates
        for xp in getattr(sm_sel, "XPATH_CALENDAR_CONTAINER_CANDIDATES", []):
            try:
                if driver.find_elements(By.XPATH, xp):
                    return True
            except Exception:
                pass
        # URL heuristic
        try:
            current_url = driver.current_url
            if current_url != last_url:
                last_url = current_url
                if any(k in current_url.lower() for k in ["calendar", "reservations", "timetable", "agenda"]):
                    return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def navigate_to_timetable_nr10(driver, timeout: Optional[int] = None) -> bool:
    """Navigate from the SmartMedical main page to the timetable (calendar) page for Nr_10.

    This function:
    - Waits for the post-login header container (ensuring we are logged in)
    - Clicks the hidden timetable link (id sm-31) via JavaScript to avoid hover
    - Clicks the Nr_10 row (tr id item-77-0)
    - If a new window is opened, switches to it
    - Waits for the calendar page to be loaded using heuristics

    Returns True on success, otherwise raises RuntimeError on timeout.
    """
    settings = get_settings()
    wait_timeout = timeout or settings.request_timeout

    wait = WebDriverWait(driver, wait_timeout)

    try:
        # Click the hidden menu link directly (no hover): //a[@id='sm-31'] in default content
        print("Waiting for timetable menu link...")
        menu_link = wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_TIMETABLE_MENU_LINK)))
        try:
            driver.execute_script("arguments[0].click();", menu_link)
        except Exception:
            # fallback to a normal click
            try:
                menu_link.click()
            except Exception:
                pass

        # Switch into the main content iframe before clicking Nr_10
        print("Switching into main content iframe before clicking Nr_10...")
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, sm_sel.XPATH_MAIN_IFRAME)))
        # Inside main iframe there is a frameset with left and right frames; go to right content frame
        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, sm_sel.XPATH_RIGHT_FRAME)))
        except Exception:
            # If right frame not available immediately, try brief fallback wait then proceed
            try:
                WebDriverWait(driver, 2).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, sm_sel.XPATH_RIGHT_FRAME)))
            except Exception:
                pass

        # Wait for the Nr_10 row and click it
        pre_handles = set(driver.window_handles)
        print("Waiting for Nr_10 row...")
        nr10_row = wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_NR10_ROW)))
        try:
            nr10_row.click()
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", nr10_row)
            except Exception:
                pass

        # If a popup/new window opened, switch to it
        time.sleep(0.5)  # brief moment to allow popup
        post_handles = set(driver.window_handles)
        new_handles = list(post_handles - pre_handles)
        if new_handles:
            try:
                driver.switch_to.window(new_handles[-1])
            except Exception:
                pass
            # After switching window, reset and try to switch into iframe -> right content frame again if present
            try:
                driver.switch_to.default_content()
                WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, sm_sel.XPATH_MAIN_IFRAME)))
                try:
                    WebDriverWait(driver, 5).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, sm_sel.XPATH_RIGHT_FRAME)))
                except Exception:
                    pass
            except Exception:
                # If iframe isn't there, continue in current context
                pass

        # Final wait for calendar content
        if not _wait_for_calendar_loaded(driver, wait_timeout):
            raise RuntimeError("Calendar view did not load in time after navigating to Nr_10.")

        return True
    except TimeoutException as e:
        raise RuntimeError("Navigation to timetable Nr_10 timed out.") from e
