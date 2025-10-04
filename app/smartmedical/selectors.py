"""Centralized CSS/XPath selectors for SmartMedical pages."""

# Auth page
XPATH_USERNAME_INPUT = "//input[@id='username']"
XPATH_PASSWORD_INPUT = "//input[@id='MainContent_password']"
XPATH_LOGIN_BUTTON = "//input[@type='submit' and @name='sendpost']"

# Post-login
XPATH_HEADER_CONTAINER = "//td[@id='header-container']"

# Frames
XPATH_MAIN_IFRAME = "//iframe[@name='_center' or contains(@src,'main.php')]"
# Inner frames within the main iframe (frameset: left menu, right content)
XPATH_LEFT_FRAME = "//frame[@name='_menu_frame' or contains(@src,'_menu_frame.php')]"
XPATH_RIGHT_FRAME = "//frame[@name='_content_frame']"

# Navigation: Timetable menu and Nr_10 item
XPATH_TIMETABLE_MENU_LINK = "//a[@id='sm-31']"
XPATH_NR10_ROW = "//tr[@id='item-77-0']"

# Generic/calendar heuristics
XPATH_CALENDAR_CONTAINER_CANDIDATES = [
    "//div[@id='calendar']",
    "//table[contains(@class,'calendar')]",
    "//div[contains(@class,'calendar')]",
]

# Calendar scraping
XPATH_WEEK_NEXT_BUTTON = "//img[contains(@src,'btt-right.gif') and contains(@onclick, \"MoveCalendar('week', 1)\")]"
XPATH_ALL_TIMESLOTS = "//div[@class='WorkTimeNotEditable']"
XPATH_ALL_RESERVATIONS = "//div[@class='Reservation']"

# Placeholders for future flows
TIMETABLE_TABLE = "#timetable"
BOOK_BUTTON = "#book-btn"
