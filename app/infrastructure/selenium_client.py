from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService

from app.core.config import get_settings


def _build_chrome_options(settings) -> ChromeOptions:
    options = ChromeOptions()
    # Container-friendly flags
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
    - Otherwise, starts a local ChromeDriver instance.
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
            # Local ChromeDriver fallback
            if settings.chromedriver_path:
                service = ChromeService(executable_path=settings.chromedriver_path)
                driver = webdriver.Chrome(service=service, options=options)
            else:
                driver = webdriver.Chrome(options=options)

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
    """Placeholder client for SmartMedical website interactions.

    Methods are intentionally not implemented. They should navigate the website
    and perform scraping/booking using Selenium.
    """

    def __init__(self) -> None:
        # Put any required shared state here
        pass

    def get_timetable(self, doctor: Optional[str], date_str: Optional[str]) -> List[dict]:
        raise NotImplementedError("SmartMedical timetable scraping is not implemented yet.")

    def book(self, booking_payload: dict) -> dict:
        raise NotImplementedError("SmartMedical booking automation is not implemented yet.")

