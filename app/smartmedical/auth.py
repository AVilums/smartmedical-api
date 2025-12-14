"""Authentication utilities for the SmartMedical portal.

Lightweight Selenium-based login flow to vm528.smartmedical.eu, styled similar to navigation.
Supports two-factor authentication (TFA) using time-based one-time passwords (TOTP).
The OTP secret key is configured via the SMARTMEDICAL_OTP_SECRET environment variable.
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
from app.smartmedical.otp import generate_otp

def perform_login(driver, username: str, password: str, timeout: Optional[int] = None) -> bool:
    """Log in using a provided driver and credentials. Returns True on success.

    Handles two-factor authentication by generating and entering an OTP code.
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
        
        # Wait for TFA code input to be clickable
        wait.until(EC.element_to_be_clickable((By.XPATH, sm_sel.XPATH_TFA_CODE_INPUT)))

        # Generate OTP if secret is available
        if settings.smartmedical_otp_secret:
            otp_code = generate_otp(settings.smartmedical_otp_secret)

            # Enter OTP code
            tfa_input = driver.find_element(By.XPATH, sm_sel.XPATH_TFA_CODE_INPUT)
            tfa_input.clear()
            tfa_input.send_keys(otp_code)

            # Click continue button
            driver.find_element(By.XPATH, sm_sel.XPATH_CONTINUE_TFA_BUTTON).click()
        else:
            raise RuntimeError("OTP secret key not provided but TFA is enabled")

        # # Handle pop-up in a separate iFrame
        # try:
        #     wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, sm_sel.XPATH_POPUP_IFRAME)))
        #     wait.until(EC.element_to_be_clickable((By.XPATH, sm_sel.XPATH_CLOSE_POPUP))).click()
        # except Exception:
        #     pass

        driver.switch_to.default_content()
        wait.until(EC.presence_of_element_located((By.XPATH, sm_sel.XPATH_TIMETABLE_MENU_LINK)))
        return True
    except TimeoutException as e:
        raise RuntimeError("Login timed out before reaching the post-login page.") from e


def login(
    username: Optional[str] = None,
    password: Optional[str] = None,
    driver=None,
    timeout: Optional[int] = None,
) -> bool:
    """Perform login. Uses an existing driver if provided; otherwise manages lifecycle.

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