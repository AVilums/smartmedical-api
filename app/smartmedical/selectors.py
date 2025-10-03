"""Centralized CSS/XPath selectors for SmartMedical pages."""

# Auth page
XPATH_USERNAME_INPUT = "//input[@id='username']"
XPATH_PASSWORD_INPUT = "//input[@id='MainContent_password']"
XPATH_LOGIN_BUTTON = "//input[@type='submit' and @name='sendpost']"

# Post-login
XPATH_HEADER_CONTAINER = "//td[@id='header-container']"

# Navigation: Timetable menu and Nr_10 item
XPATH_TIMETABLE_MENU_LINK = "//a[@id='sm-29']"
XPATH_NR10_ROW = "//tr[@id='item-77-0']"

# Generic/calendar heuristics
XPATH_CALENDAR_CONTAINER_CANDIDATES = [
    "//div[@id='calendar']",
    "//table[contains(@class,'calendar')]",
    "//div[contains(@class,'calendar')]",
]

# Placeholders for future flows
TIMETABLE_TABLE = "#timetable"
BOOK_BUTTON = "#book-btn"
