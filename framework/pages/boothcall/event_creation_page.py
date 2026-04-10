"""
EventCreationPage - Page Object Model

Page Object for the BoothCall Create Event page (/events/new).
Handles event form fields and submission.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class EventCreationPage:
    """
    Page Object for BoothCall Create Event Page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, browser: BrowserInterface):
        """Compose BrowserInterface — NO inheritance."""
        self.browser = browser

    # ==================== LOCATORS (Class Constants) ====================

    PAGE_HEADING = (By.XPATH, "//h1[contains(., 'Create Event')]")
    EVENT_NAME_INPUT = (By.CSS_SELECTOR, "#event-name")
    VENUE_INPUT = (By.CSS_SELECTOR, "#event-venue")
    CITY_INPUT = (By.CSS_SELECTOR, "#event-city")

    # DateTimePicker triggers
    START_DATE_BUTTON = (By.CSS_SELECTOR, "#event-start")
    END_DATE_BUTTON = (By.CSS_SELECTOR, "#event-end")

    # Calendar day selector (pick first available)
    CALENDAR_DAY = (By.XPATH, "//button[@name='day' and not(@disabled)]")

    # Time inputs
    START_TIME_INPUT = (By.XPATH, "(//input[@type='time'])[1]")
    END_TIME_INPUT = (By.XPATH, "(//input[@type='time'])[2]")

    # Timezone selector
    TIMEZONE_TRIGGER = (By.CSS_SELECTOR, "#event-tz")
    TIMEZONE_OPTION_PT = (By.XPATH, "//div[@role='option'][contains(., 'Pacific')]")
    TIMEZONE_OPTION_ET = (By.XPATH, "//div[@role='option'][contains(., 'Eastern')]")

    # Submit
    CREATE_BUTTON = (By.XPATH, "//button[@type='submit'][contains(., 'Create Event')]")
    CANCEL_BUTTON = (By.XPATH, "//button[contains(., 'Cancel')]")

    # Validation errors
    VALIDATION_ERROR = (By.CSS_SELECTOR, ".text-red-400")

    # Success toast
    SUCCESS_TOAST = (By.XPATH, "//li[contains(@class, 'toast')]//div[contains(., 'created')]")

    # ==================== NAVIGATION ====================

    def navigate(self, url: str) -> "EventCreationPage":
        """Navigate to the create event page."""
        self.browser.navigate_to(url)
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def wait_for_page_loaded(self, timeout: int = 15) -> "EventCreationPage":
        """Wait for the Create Event heading to be visible."""
        self.browser.wait_for_element_visible(*self.PAGE_HEADING, timeout=timeout)
        return self

    def enter_event_name(self, name: str) -> "EventCreationPage":
        """Enter an event name."""
        self.browser.type(*self.EVENT_NAME_INPUT, name)
        return self

    def enter_venue(self, venue: str) -> "EventCreationPage":
        """Enter a venue name."""
        self.browser.type(*self.VENUE_INPUT, venue)
        return self

    def enter_city(self, city: str) -> "EventCreationPage":
        """Enter a city."""
        self.browser.type(*self.CITY_INPUT, city)
        return self

    def click_start_date_picker(self) -> "EventCreationPage":
        """Open the start date calendar."""
        self.browser.click(*self.START_DATE_BUTTON)
        return self

    def select_first_available_day(self) -> "EventCreationPage":
        """Select the first available calendar day."""
        self.browser.click(*self.CALENDAR_DAY)
        return self

    def click_end_date_picker(self) -> "EventCreationPage":
        """Open the end date calendar."""
        self.browser.click(*self.END_DATE_BUTTON)
        return self

    def click_create_event(self) -> "EventCreationPage":
        """Click the Create Event submit button."""
        self.browser.click(*self.CREATE_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_page_displayed(self) -> bool:
        """Check if the Create Event heading is visible."""
        return self.browser.is_element_displayed(*self.PAGE_HEADING)

    def is_on_event_detail_page(self) -> bool:
        """Check if redirected to an event detail page after creation."""
        url = self.browser.get_current_url()
        return "/events/" in url and "/new" not in url

    def has_validation_errors(self) -> bool:
        """Check if any validation error messages are shown."""
        return self.browser.is_element_displayed(*self.VALIDATION_ERROR)
