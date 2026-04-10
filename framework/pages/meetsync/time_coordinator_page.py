"""
TimeCoordinatorPage - Page Object Model

Page Object for the MeetSync Global Time Coordinator grid (/meetings).
Handles NLP extraction, timezone chip management, clock format toggle,
and grid state verification.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class TimeCoordinatorPage:
    """
    Page Object for the Time Coordinator grid.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, browser: BrowserInterface):
        self.browser = browser

    # ==================== LOCATORS ====================

    PAGE_HEADING    = (By.XPATH, "//*[contains(text(), 'Global Time Coordinator')]")
    NLP_INPUT       = (By.CSS_SELECTOR, "input[placeholder*='Find 30m']")
    EXTRACT_BUTTON  = (By.XPATH, "//button[normalize-space()='Extract']")
    GRID_TABLE      = (By.CSS_SELECTOR, "table")
    FORMAT_24H      = (By.XPATH, "//button[normalize-space()='24h']")
    FORMAT_12H      = (By.XPATH, "//button[normalize-space()='12h']")
    ADD_ZONE_SELECT = (By.CSS_SELECTOR, "select")
    NEW_MEETING_BTN = (By.XPATH, "//a[contains(., 'New Meeting')]")

    def _zone_chip(self, label: str):
        return (By.XPATH, f"//*[contains(text(), '{label}')]")

    def _remove_zone_btn(self, label: str):
        return (By.XPATH, f"//*[contains(text(), '{label}')]/following-sibling::button")

    # ==================== NAVIGATION ====================

    def navigate(self, base_url: str) -> "TimeCoordinatorPage":
        self.browser.navigate(base_url + "/meetings")
        return self

    def wait_for_page_load(self, timeout: int = 15) -> "TimeCoordinatorPage":
        self.browser.wait_for_element_visible(*self.PAGE_HEADING, timeout=timeout)
        return self

    def wait_for_grid(self, timeout: int = 15) -> "TimeCoordinatorPage":
        self.browser.wait_for_element_visible(*self.GRID_TABLE, timeout=timeout)
        return self

    # ==================== ATOMIC METHODS ====================

    def enter_nlp_prompt(self, prompt: str) -> "TimeCoordinatorPage":
        self.browser.enter_text(*self.NLP_INPUT, prompt)
        return self

    def click_extract(self) -> "TimeCoordinatorPage":
        self.browser.click(*self.EXTRACT_BUTTON)
        return self

    def click_format_24h(self) -> "TimeCoordinatorPage":
        self.browser.click(*self.FORMAT_24H)
        return self

    def click_format_12h(self) -> "TimeCoordinatorPage":
        self.browser.click(*self.FORMAT_12H)
        return self

    def add_timezone(self, iana_value: str) -> "TimeCoordinatorPage":
        """Select a timezone from the Add Zone dropdown by IANA value."""
        select_el = self.browser.find_element(*self.ADD_ZONE_SELECT)
        from selenium.webdriver.support.ui import Select
        Select(select_el).select_by_value(iana_value)
        return self

    def click_new_meeting(self) -> "TimeCoordinatorPage":
        self.browser.click(*self.NEW_MEETING_BTN)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_page_loaded(self) -> bool:
        return self.browser.is_element_displayed(*self.PAGE_HEADING, timeout=10)

    def is_grid_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.GRID_TABLE, timeout=10)

    def is_zone_chip_visible(self, label: str) -> bool:
        return self.browser.is_element_displayed(*self._zone_chip(label), timeout=10)

    def is_24h_format_active(self) -> bool:
        """Return True if a cell containing ':00' in 24h format (e.g. '09:00') is visible."""
        locator = (By.XPATH, "//td[contains(text(), ':00') and string-length(text()) <= 6]")
        return self.browser.is_element_displayed(*locator, timeout=5)

    def is_12h_format_active(self) -> bool:
        """Return True if a cell containing AM/PM is visible."""
        locator = (By.XPATH, "//td[contains(text(), 'AM') or contains(text(), 'PM')]")
        return self.browser.is_element_displayed(*locator, timeout=5)

    def get_visible_timezone_labels(self) -> list:
        """Return the text of all visible timezone header cells."""
        headers = self.browser.find_elements(By.CSS_SELECTOR, "table th")
        return [h.text.strip() for h in headers if h.text.strip() and h.text.strip() != "UTC" and h.text.strip() != "Overlap"]
