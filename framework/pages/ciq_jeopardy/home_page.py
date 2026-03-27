"""
HomePage - CIQ Jeopardy landing page.

Handles navigation to host/join flows and verifies page loaded correctly.
All locators live here. No business logic.

Locator notes (no IDs on elements - using CSS class + text XPath):
  - Heading: h1 (text "CIQ Jeopardy")
  - Host button: <a> with class 'btn btn-primary'
  - Join button: <a> with class 'btn btn-gold'
"""

from selenium.webdriver.common.by import By
from resources.utilities import autologger


class HomePage:
    """
    Page Object for the CIQ Jeopardy home / landing page (/).

    Locators:
        TITLE_HEADING - Main h1 heading
        HOST_GAME_BTN - 'Host a Game' anchor link (btn-primary class)
        JOIN_GAME_BTN - 'Join as Player' anchor link (btn-gold class)
    """

    # Locators
    TITLE_HEADING = (By.CSS_SELECTOR, "h1")
    HOST_GAME_BTN = (By.XPATH, "//a[contains(text(),'Host')]")
    JOIN_GAME_BTN = (By.XPATH, "//a[contains(text(),'Join')]")
    NAV_LINKS     = (By.CSS_SELECTOR, "a.btn, a.nav-link")

    def __init__(self, browser):
        self.browser = browser

    # ── Navigation ────────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def navigate(self):
        """Navigate to the home page."""
        self.browser.navigate_to(self.browser.config["url"])

    # ── Actions ───────────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def click_host_game(self):
        """Click the 'Host a Game' link."""
        self.browser.click(*self.HOST_GAME_BTN)

    @autologger.automation_logger("Page")
    def click_join_game(self):
        """Click the 'Join as Player' link."""
        self.browser.click(*self.JOIN_GAME_BTN)

    # ── State checks ─────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def is_loaded(self) -> bool:
        """Return True if the main h1 heading is visible."""
        return self.browser.is_element_displayed(*self.TITLE_HEADING)

    @autologger.automation_logger("Page")
    def is_host_button_visible(self) -> bool:
        """Return True if the Host Game link is present."""
        return self.browser.is_element_displayed(*self.HOST_GAME_BTN)

    @autologger.automation_logger("Page")
    def is_join_button_visible(self) -> bool:
        """Return True if the Join as Player link is present."""
        return self.browser.is_element_displayed(*self.JOIN_GAME_BTN)

    @autologger.automation_logger("Page")
    def get_page_heading(self) -> str:
        """Return the text of the main h1 heading."""
        return self.browser.get_text(*self.TITLE_HEADING)
