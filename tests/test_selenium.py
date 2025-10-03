import os
from app.infrastructure.selenium_client import browser
from app.core.config import get_settings

# Load your environment
from dotenv import load_dotenv

load_dotenv()


def test_selenium_basic():
    """Basic test to see if Selenium browser opens and works"""
    print("Testing Selenium setup...")

    with browser() as driver:
        print(f"Browser opened: {driver.title}")

        # Test basic navigation
        driver.get("https://www.google.com")
        print(f"Navigated to Google. Title: {driver.title}")

        # You can add more basic tests here
        print("Selenium test completed successfully!")


def test_actual_smartmedical_site():
    """Use smartmedical auth and navigation to reach the timetable (calendar) page."""
    print("Testing SmartMedical login and navigation to calendar...")

    # Import here to keep test module imports minimal
    from app.smartmedical import auth, navigation

    with browser() as driver:
        # Perform login using credentials from environment/settings
        assert auth.login(driver=driver), "Login failed"

        # Navigate to the timetable/calendar (Nr_10 as implemented)
        assert navigation.navigate_to_timetable_nr10(driver), "Failed to open timetable/calendar"

        print(f"Navigation successful. Current URL: {driver.current_url}")


if __name__ == "__main__":
    # Test basic Selenium setup
    test_selenium_basic()

    # Test actual site (when you're ready)
    test_actual_smartmedical_site()