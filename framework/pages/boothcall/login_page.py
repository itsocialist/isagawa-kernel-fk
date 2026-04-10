"""
LoginPage - Page Object Model

Page Object for the BoothCall login page (/login).
Handles Google OAuth button, magic link form, and login state checks.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class LoginPage:
    """
    Page Object for BoothCall Login Page.

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

    SIGN_IN_HEADING = (By.CSS_SELECTOR, "h1")
    GOOGLE_BUTTON = (By.XPATH, "//button[contains(., 'Continue with Google')]")
    EMAIL_INPUT = (By.CSS_SELECTOR, "input#email[type='email']")
    MAGIC_LINK_BUTTON = (By.XPATH, "//button[contains(., 'Send magic link')]")
    BACK_TO_HOME_LINK = (By.XPATH, "//a[contains(., 'Back to home')]")
    EMAIL_SENT_CONFIRMATION = (By.XPATH, "//p[contains(., 'Check your email')]")

    # ==================== NAVIGATION ====================

    def navigate(self, url: str) -> "LoginPage":
        """Navigate to the login page."""
        self.browser.navigate_to(url)
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def wait_for_page_loaded(self, timeout: int = 15) -> "LoginPage":
        """Wait for the sign-in heading to be visible."""
        self.browser.wait_for_element_visible(*self.SIGN_IN_HEADING, timeout=timeout)
        return self

    def click_google_sign_in(self) -> "LoginPage":
        """Click the Continue with Google button."""
        self.browser.click(*self.GOOGLE_BUTTON)
        return self

    def enter_email(self, email: str) -> "LoginPage":
        """Enter email address into the magic link field."""
        self.browser.type(*self.EMAIL_INPUT, email)
        return self

    def click_send_magic_link(self) -> "LoginPage":
        """Click the Send magic link button."""
        self.browser.click(*self.MAGIC_LINK_BUTTON)
        return self

    def click_back_to_home(self) -> "LoginPage":
        """Click the Back to home link."""
        self.browser.click(*self.BACK_TO_HOME_LINK)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_login_page_displayed(self) -> bool:
        """Check if the login page heading is visible."""
        return self.browser.is_element_displayed(*self.SIGN_IN_HEADING)

    def is_google_button_displayed(self) -> bool:
        """Check if the Google sign-in button is visible."""
        return self.browser.is_element_displayed(*self.GOOGLE_BUTTON)

    def is_email_sent_confirmation_displayed(self) -> bool:
        """Check if the email sent confirmation message is visible."""
        return self.browser.is_element_displayed(*self.EMAIL_SENT_CONFIRMATION, timeout=10)

    def is_on_login_page(self) -> bool:
        """Check if URL contains /login."""
        return "/login" in self.browser.get_current_url()
