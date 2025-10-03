from __future__ import annotations

from contextlib import contextmanager
from typing import Generator, List, Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions

from .config import get_settings


@contextmanager
def browser() -> Generator[webdriver.Chrome, None, None]:
    """Context manager that yields a configured headless Chrome WebDriver.
    Note: Actual scraping logic will be implemented later.
    """
    settings = get_settings()

    options = ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    if settings.chrome_binary_path:
        options.binary_location = settings.chrome_binary_path

    driver = webdriver.Chrome(options=options)
    try:
        driver.set_page_load_timeout(settings.selenium_pageload_timeout)
        driver.implicitly_wait(settings.selenium_implicit_wait)
        yield driver
    finally:
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
