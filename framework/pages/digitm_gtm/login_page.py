"""
LoginPage - Page Object Model

Page Object for the Digitm GTM login page (/login).
Handles Google OAuth sign-in button and page state checks.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class LoginPage:

    def __init__(self, browser: BrowserInterface):
        self.browser = browser

    # ==================== LOCATORS ====================

    HEADING = (By.XPATH, "//h1[contains(., 'Digitm GTM')]")
    SUBTEXT = (By.XPATH, "//p[contains(., 'AI-powered go-to-market pipeline')]")
    GOOGLE_BUTTON = (By.XPATH, "//button[contains(., 'Sign in with Google')]")

    # ==================== NAVIGATION ====================

    def navigate(self, url: str) -> "LoginPage":
        self.browser.navigate_to(url)
        return self

    def wait_for_page_loaded(self, timeout: int = 15) -> "LoginPage":
        self.browser.wait_for_element_visible(*self.HEADING, timeout=timeout)
        return self

    # ==================== ATOMIC METHODS ====================

    def click_google_sign_in(self) -> "LoginPage":
        self.browser.click(*self.GOOGLE_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_login_page_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.HEADING)

    def is_google_button_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.GOOGLE_BUTTON)

    def is_on_login_page(self) -> bool:
        return "/login" in self.browser.get_current_url()
