"""
EventDashboardPage - Page Object Model

Page Object for the BoothCall event dashboard (/events) and
individual event detail pages (/events/[id]).
Handles event listing, navigation tabs, and shift management actions.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class EventDashboardPage:
    """
    Page Object for BoothCall Event Dashboard.

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

    # Events list page
    PAGE_HEADING = (By.XPATH, "//h1[contains(., 'Events')]")
    CREATE_EVENT_BUTTON = (By.XPATH, "//a[contains(., 'New Event')]")
    EVENT_CARD = (By.CSS_SELECTOR, "[class*='rounded-2xl'][class*='border']")

    # Event detail page — tabs
    COVERAGE_TAB = (By.XPATH, "//a[contains(., 'Coverage')]")
    SHIFTS_TAB = (By.XPATH, "//a[contains(., 'Shifts')]")
    TEAM_TAB = (By.XPATH, "//a[contains(., 'Team')]")
    RECONCILE_TAB = (By.XPATH, "//a[contains(., 'Reconcile')]")

    # Event detail page — header
    EVENT_TITLE = (By.CSS_SELECTOR, "h1")

    # ==================== NAVIGATION ====================

    def navigate(self, url: str) -> "EventDashboardPage":
        """Navigate to the events dashboard."""
        self.browser.navigate_to(url)
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def wait_for_events_page(self, timeout: int = 15) -> "EventDashboardPage":
        """Wait for the events page heading to be visible."""
        self.browser.wait_for_element_visible(*self.PAGE_HEADING, timeout=timeout)
        return self

    def click_first_event_card(self) -> "EventDashboardPage":
        """Click the first event card to open event detail."""
        self.browser.click(*self.EVENT_CARD)
        return self

    def click_coverage_tab(self) -> "EventDashboardPage":
        """Click the Coverage tab."""
        self.browser.click(*self.COVERAGE_TAB)
        return self

    def click_shifts_tab(self) -> "EventDashboardPage":
        """Click the Shifts tab."""
        self.browser.click(*self.SHIFTS_TAB)
        return self

    def click_team_tab(self) -> "EventDashboardPage":
        """Click the Team tab."""
        self.browser.click(*self.TEAM_TAB)
        return self

    def click_reconcile_tab(self) -> "EventDashboardPage":
        """Click the Reconcile tab."""
        self.browser.click(*self.RECONCILE_TAB)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_events_page_displayed(self) -> bool:
        """Check if the events page heading is visible."""
        return self.browser.is_element_displayed(*self.PAGE_HEADING)

    def is_event_detail_page(self) -> bool:
        """Check if an event detail page is displayed (any tab visible)."""
        return self.browser.is_element_displayed(*self.COVERAGE_TAB)

    def is_shifts_tab_displayed(self) -> bool:
        """Check if the Shifts tab link is visible."""
        return self.browser.is_element_displayed(*self.SHIFTS_TAB)

    def get_event_title(self) -> str:
        """Get the event title text."""
        return self.browser.get_text(*self.EVENT_TITLE)

    def get_event_card_count(self) -> int:
        """Get the count of event cards displayed."""
        cards = self.browser.find_elements(*self.EVENT_CARD, timeout=5)
        return len(cards)
