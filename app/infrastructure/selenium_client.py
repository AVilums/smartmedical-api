from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

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

