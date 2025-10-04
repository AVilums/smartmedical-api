from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

from app.core.config import get_settings


def _build_chrome_options(settings) -> ChromeOptions:
    options = ChromeOptions()
    # Container-friendly flags
    # Headless only if explicitly requested via BROWSER starting with "headless"
    browser = (getattr(settings, "browser", None) or "headless-chrome").lower()
    if browser.startswith("headless"):
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    if settings.chrome_binary_path:
        options.binary_location = settings.chrome_binary_path
    return options


@contextmanager
def browser() -> Generator[webdriver.Chrome, None, None]:
    """Context manager that yields a configured Chrome WebDriver.

    - If SELENIUM_REMOTE_URL is provided, connects to a remote Selenium node (Docker/Grid).
    - Otherwise, starts a local ChromeDriver instance with auto-managed driver.
    """
    settings = get_settings()
    options = _build_chrome_options(settings)

    driver = None
    try:
        if getattr(settings, "selenium_remote_url", None):
            # Remote WebDriver for Docker containers / Selenium Grid
            driver = webdriver.Remote(
                command_executor=settings.selenium_remote_url,
                options=options,
            )
        else:
            # Local ChromeDriver with auto-management
            if settings.chromedriver_path:
                # Use manually specified path if provided
                service = ChromeService(executable_path=settings.chromedriver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                # Auto-install and manage ChromeDriver
                service = ChromeService(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)

        driver.set_page_load_timeout(settings.selenium_pageload_timeout)
        driver.implicitly_wait(settings.selenium_implicit_wait)
        yield driver
    finally:
        if driver is not None:
            try:
                driver.quit()
            except Exception:
                pass


class SmartMedicalClient:
    """Client for SmartMedical website interactions.

    For now, delegates to scraping utilities implemented in app.smartmedical.scraping.
    """

    def __init__(self) -> None:
        # Put any required shared state here
        pass

    def get_timetable(self, doctor: Optional[str], date_str: Optional[str]) -> List[dict]:
        # Lazy import to avoid circular dependencies
        from app.smartmedical.scraping import fetch_timetable
        resp = fetch_timetable(doctor=doctor, date_str=date_str)
        # Return just slots for backward compatibility with previous call site
        return resp.get("slots", [])

    def book(self, booking_payload: dict) -> dict:
        # Still not implemented; keep explicit error for booking
        raise NotImplementedError("SmartMedical booking automation is not implemented yet.")

