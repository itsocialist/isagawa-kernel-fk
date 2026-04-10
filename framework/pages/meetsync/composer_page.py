"""
ComposerPage - Page Object Model

Page Object for the MeetSync Living Composer (/meetings/new and /schedule).
Handles NLP input, submission, thinking state, proposal card, and error states.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class ComposerPage:
    """
    Page Object for the Meeting Composer.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, browser: BrowserInterface):
        self.browser = browser

    # ==================== LOCATORS ====================

    PROMPT_TEXTAREA     = (By.CSS_SELECTOR, "textarea[placeholder*='30 min']")
    COMPOSE_BUTTON      = (By.XPATH, "//button[contains(text(), 'Compose')]")
    COMPOSING_BUTTON    = (By.XPATH, "//button[contains(text(), 'Composing')]")
    ERROR_MESSAGE       = (By.CSS_SELECTOR, "p.text-red-400, p.text-xs.text-red-400")
    AUTH_BANNER         = (By.XPATH, "//*[contains(text(), 'Sign in to compose')]")
    SIGN_IN_LINK        = (By.XPATH, "//a[contains(text(), 'Sign in')]")
    PROPOSAL_TITLE      = (By.CSS_SELECTOR, "[data-testid='proposal-title'], h2")
    SEND_BUTTON         = (By.XPATH, "//button[contains(text(), 'Send it')]")
    START_OVER_BUTTON   = (By.XPATH, "//button[contains(text(), 'Start over')]")
    TIMEZONE_CARD       = (By.CSS_SELECTOR, "[class*='timezone'], [data-testid*='timezone']")

    # ==================== NAVIGATION ====================

    def navigate_new(self, base_url: str) -> "ComposerPage":
        self.browser.navigate(base_url + "/meetings/new")
        return self

    def navigate_schedule(self, base_url: str) -> "ComposerPage":
        self.browser.navigate(base_url + "/schedule")
        return self

    def wait_for_composer(self, timeout: int = 15) -> "ComposerPage":
        self.browser.wait_for_element_visible(*self.PROMPT_TEXTAREA, timeout=timeout)
        return self

    # ==================== ATOMIC METHODS ====================

    def enter_prompt(self, text: str) -> "ComposerPage":
        self.browser.enter_text(*self.PROMPT_TEXTAREA, text)
        return self

    def click_compose(self) -> "ComposerPage":
        self.browser.click(*self.COMPOSE_BUTTON)
        return self

    def wait_for_thinking_state(self, timeout: int = 10) -> "ComposerPage":
        """Wait for the 'Composing…' button state that indicates AI is processing."""
        self.browser.wait_for_element_visible(*self.COMPOSING_BUTTON, timeout=timeout)
        return self

    def wait_for_proposal(self, timeout: int = 60) -> "ComposerPage":
        """Wait for AI to return a proposal. Generous timeout for real AI calls."""
        self.browser.wait_for_element_visible(*self.SEND_BUTTON, timeout=timeout)
        return self

    def wait_for_error_or_auth_banner(self, timeout: int = 60) -> "ComposerPage":
        """Wait for either an error message or auth banner to appear."""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        driver = self.browser.driver
        WebDriverWait(driver, timeout).until(
            EC.any_of(
                EC.visibility_of_element_located(self.ERROR_MESSAGE),
                EC.visibility_of_element_located(self.AUTH_BANNER),
                EC.visibility_of_element_located(self.SEND_BUTTON),
            )
        )
        return self

    def click_start_over(self) -> "ComposerPage":
        self.browser.click(*self.START_OVER_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_composer_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.PROMPT_TEXTAREA, timeout=10)

    def is_compose_button_enabled(self) -> bool:
        btn = self.browser.find_element(*self.COMPOSE_BUTTON)
        return btn.is_enabled() if btn else False

    def is_compose_button_disabled(self) -> bool:
        btn = self.browser.find_element(*self.COMPOSE_BUTTON)
        return not btn.is_enabled() if btn else True

    def is_thinking_state_active(self) -> bool:
        return self.browser.is_element_displayed(*self.COMPOSING_BUTTON, timeout=5)

    def is_proposal_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.SEND_BUTTON, timeout=5)

    def is_error_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.ERROR_MESSAGE, timeout=5)

    def is_auth_banner_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.AUTH_BANNER, timeout=5)

    def get_error_text(self) -> str:
        el = self.browser.find_element(*self.ERROR_MESSAGE)
        return el.text if el else ""

    def get_prompt_value(self) -> str:
        el = self.browser.find_element(*self.PROMPT_TEXTAREA)
        return el.get_attribute("value") if el else ""
