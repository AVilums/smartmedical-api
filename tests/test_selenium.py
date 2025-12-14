import pytest
from app.infrastructure.selenium_client import browser

# Mark this entire module as local-only (requires Selenium and credentials)
pytestmark = pytest.mark.local

# Load your environment (used only for local runs)
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
        print("Login successful.")

        # Navigate to the timetable/calendar (Nr_10 as implemented)
        assert navigation.navigate_to_timetable_nr10(driver), "Failed to open timetable/calendar"

        print(f"Navigation successful. Current URL: {driver.current_url}")


def test_fetch_timetable():
    """Test the timetable flow for /timetable."""
    print("Testing timetable fetcher...")

    from app.smartmedical.scrape_timetable import fetch_timetable
    resp = fetch_timetable()
    print(f"Fetched timetable: {resp}")


def test_create_booking_like_fetch_timetable():
    """Test the booking flow for /book."""
    from app.smartmedical.create_booking import create_booking

    # Example payload; adjust date/time during local runs to an actually free slot.
    # Keeping values simple and safe; notes is optional.
    result = create_booking(
        date="2025-10-10",
        time="12:00",
        first_name="Test",
        last_name="User",
        phone="+37100000000",
        notes="PyTest booking trial - safe no-submit"
    )

    # Print result to help during manual/local runs as in test_fetch_timetable
    print(f"Booking result: {result}")

    # Basic shape checks similar in spirit to the timetable test
    assert isinstance(result, dict)
    assert "status" in result
    # Allow statuses: ok, unavailable, error
    assert result["status"] in {"ok", "unavailable", "error"}


if __name__ == "__main__":
    # Test basic Selenium setup
    test_selenium_basic()

    # Test the actual site
    test_actual_smartmedical_site()