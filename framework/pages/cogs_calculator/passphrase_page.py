"""
PassphrasePage - Page Object Model

Page Object for the ROLOS KITCHEN passphrase gate screen.
Handles passphrase entry and submission.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class PassphrasePage:
    """
    Page Object for the Passphrase Gate screen.

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

    BRAND_HEADER = (By.XPATH, "//h1[contains(text(),'ROLOS KITCHEN')]")
    PASSPHRASE_INPUT = (By.XPATH, "//input[@type='password']")
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")
    ERROR_MESSAGE = (By.XPATH, "//*[contains(text(),'Incorrect passphrase') or contains(text(),'Please enter')]")

    # ==================== NAVIGATION ====================

    def navigate(self, url: str) -> "PassphrasePage":
        """Navigate to the app URL."""
        self.browser.navigate_to(url)
        return self

    # ==================== ATOMIC METHODS ====================

    def wait_for_passphrase_gate(self, timeout: int = 15) -> "PassphrasePage":
        """Wait for the passphrase gate to be visible."""
        self.browser.wait_for_element_visible(*self.PASSPHRASE_INPUT, timeout=timeout)
        return self

    def enter_passphrase(self, passphrase: str) -> "PassphrasePage":
        """Enter the passphrase."""
        self.browser.type(*self.PASSPHRASE_INPUT, passphrase)
        return self

    def click_submit(self) -> "PassphrasePage":
        """Click the submit button."""
        self.browser.click(*self.SUBMIT_BUTTON)
        return self

    def wait_for_error(self, timeout: int = 5) -> "PassphrasePage":
        """Wait for an error message to appear."""
        self.browser.wait_for_element_visible(*self.ERROR_MESSAGE, timeout=timeout)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_passphrase_gate_displayed(self) -> bool:
        """Check if the passphrase gate is displayed."""
        return self.browser.is_element_displayed(*self.PASSPHRASE_INPUT, timeout=10)

    def is_brand_header_displayed(self) -> bool:
        """Check if ROLOS KITCHEN brand header is visible."""
        return self.browser.is_element_displayed(*self.BRAND_HEADER, timeout=10)

    def is_error_displayed(self) -> bool:
        """Check if an error message is displayed."""
        return self.browser.is_element_displayed(*self.ERROR_MESSAGE, timeout=5)

    def is_app_accessible(self) -> bool:
        """Check if the main app is accessible (passphrase accepted)."""
        return not self.browser.is_element_displayed(*self.PASSPHRASE_INPUT, timeout=5)
