"""
LandingPage - Page Object Model

Page Object for the BoothCall landing page (unauthenticated root /).
Handles the hero section, navigation to login, and basic page state checks.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class LandingPage:
    """
    Page Object for BoothCall Landing Page.

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

    SIGN_IN_BUTTON = (By.CSS_SELECTOR, "header a[href='/login'] button")
    HERO_HEADING = (By.CSS_SELECTOR, "section h1")
    GET_STARTED_BUTTON = (By.CSS_SELECTOR, "section a[href='/login'] button")
    BOOTHCALL_LOGO_TEXT = (By.XPATH, "//span[text()='BoothCall']")

    # ==================== NAVIGATION ====================

    def navigate(self, url: str) -> "LandingPage":
        """Navigate to the landing page."""
        self.browser.navigate_to(url)
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def wait_for_page_loaded(self, timeout: int = 15) -> "LandingPage":
        """Wait for the hero heading to be visible."""
        self.browser.wait_for_element_visible(*self.HERO_HEADING, timeout=timeout)
        return self

    def click_sign_in(self) -> "LandingPage":
        """Click the Sign In button in the header."""
        self.browser.click(*self.SIGN_IN_BUTTON)
        return self

    def click_get_started(self) -> "LandingPage":
        """Click the Get Started Free button in the hero section."""
        self.browser.click(*self.GET_STARTED_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_hero_displayed(self) -> bool:
        """Check if the hero heading is visible."""
        return self.browser.is_element_displayed(*self.HERO_HEADING)

    def is_logo_displayed(self) -> bool:
        """Check if the BoothCall logo text is visible."""
        return self.browser.is_element_displayed(*self.BOOTHCALL_LOGO_TEXT)

    def get_hero_text(self) -> str:
        """Get the hero heading text content."""
        return self.browser.get_text(*self.HERO_HEADING)

    def is_on_login_page(self) -> bool:
        """Check if navigated to the login page."""
        return "/login" in self.browser.get_current_url()
