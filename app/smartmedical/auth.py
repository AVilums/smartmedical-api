"""Authentication utilities for the SmartMedical portal.

Lightweight Selenium-based login flow to vm528.smartmedical.eu, styled similar to navigation.
"""
from __future__ import annotations

from typing import Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from app.core.config import get_settings
from app.infrastructure.selenium_client import browser
from app.smartmedical import selectors as sm_sel


def perform_login(driver, username: str, password: str, timeout: Optional[int] = None) -> bool:
    """Log in using provided driver and credentials. Returns True on success.

    Raises RuntimeError on timeout or unexpected page state.
    """
    settings = get_settings()
    wait_timeout = timeout or settings.request_timeout

    wait = WebDriverWait(driver, wait_timeout)
    driver.get(settings.smartmedical_base_url)

    try:
        # Wait for inputs
        wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_USERNAME_INPUT)))

        u_input = driver.find_element(By.XPATH, sm_sel.XPATH_USERNAME_INPUT)
        p_input = driver.find_element(By.XPATH, sm_sel.XPATH_PASSWORD_INPUT)
        try:
            u_input.clear()
            p_input.clear()
        except Exception:
            # Some inputs may not support clear(); continue
            pass
        u_input.send_keys(username)
        p_input.send_keys(password)

        driver.find_element(By.XPATH, sm_sel.XPATH_LOGIN_BUTTON).click()

        wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_HEADER_CONTAINER)))
        return True
    except TimeoutException as e:
        raise RuntimeError("Login timed out before reaching the post-login page.") from e


def login(
    username: Optional[str] = None,
    password: Optional[str] = None,
    driver=None,
    timeout: Optional[int] = None,
) -> bool:
    """Perform login. Uses existing driver if provided; otherwise manages lifecycle.

    Credentials default to SMARTMEDICAL_USERNAME/PASSWORD.
    """
    settings = get_settings()
    user = username or settings.smartmedical_username
    pwd = password or settings.smartmedical_password
    wait_timeout = timeout or settings.request_timeout

    if not user or not pwd:
        raise ValueError("SmartMedical credentials are not provided (username/password).")

    if driver is not None:
        return perform_login(driver, user, pwd, wait_timeout)
    # Manage driver automatically
    with browser() as drv:
        return perform_login(drv, user, pwd, wait_timeout)