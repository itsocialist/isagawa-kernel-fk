"""
GeneratePage - Page Object Model

Page Object for the Living Decks AI generation UI (/generate).
Handles prompt input, theme selection, quality mode, and generation progress.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class GeneratePage:
    """
    Page Object for the generation interface.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    BASE_URL = "http://localhost:5550"

    # ==================== LOCATORS ====================

    PROMPT_TEXTAREA       = (By.ID, "prompt")
    GENERATE_BUTTON       = (By.CSS_SELECTOR, "button[type='submit'], .generate-btn, #generate-btn")
    PROGRESS_BAR          = (By.CSS_SELECTOR, ".progress-bar, .progress, [class*='progress']")
    PROGRESS_MESSAGE      = (By.CSS_SELECTOR, ".progress-message, [class*='progress-msg']")
    SUCCESS_LINK          = (By.CSS_SELECTOR, "a[href*='/docs/presentations'], .result-link, [class*='result']")
    ERROR_MESSAGE         = (By.CSS_SELECTOR, ".error, .error-message, [class*='error']")
    THEME_CARDS           = (By.CSS_SELECTOR, ".theme-card, [class*='theme-card']")
    QUALITY_BOSS_TOGGLE   = (By.CSS_SELECTOR, "[data-quality='boss'], .quality-boss, #quality-boss")
    PDF_IMPORT_INPUT      = (By.CSS_SELECTOR, "input[type='file']")
    GUIDE_PROMPT_TEXTAREA = (By.CSS_SELECTOR, "#guide-prompt, [name='guidePrompt']")
    NAV_GALLERY           = (By.CSS_SELECTOR, "a[href='/gallery']")
    NAV_EDITOR            = (By.CSS_SELECTOR, "a[href='/editor']")

    def __init__(self, browser: BrowserInterface):
        """Compose BrowserInterface — NO inheritance."""
        self.browser = browser

    # ==================== NAVIGATION ====================

    def navigate(self) -> "GeneratePage":
        self.browser.navigate_to(f"{self.BASE_URL}/generate")
        return self

    # ==================== ACTIONS ====================

    def enter_prompt(self, text: str) -> "GeneratePage":
        self.browser.clear_and_type(*self.PROMPT_TEXTAREA, text)
        return self

    def select_theme(self, theme_name: str) -> "GeneratePage":
        """Click the theme card matching theme_name (case-insensitive partial match)."""
        cards = self.browser.find_elements(*self.THEME_CARDS)
        for card in cards:
            if theme_name.lower() in card.text.lower():
                card.click()
                break
        return self

    def enable_boss_mode(self) -> "GeneratePage":
        self.browser.click(*self.QUALITY_BOSS_TOGGLE)
        return self

    def click_generate(self) -> "GeneratePage":
        self.browser.click(*self.GENERATE_BUTTON)
        return self

    def attach_pdf(self, file_path: str) -> "GeneratePage":
        self.browser.find_element(*self.PDF_IMPORT_INPUT).send_keys(file_path)
        return self

    def enter_guide_prompt(self, text: str) -> "GeneratePage":
        self.browser.clear_and_type(*self.GUIDE_PROMPT_TEXTAREA, text)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_progress_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.PROGRESS_BAR)

    def get_progress_message(self) -> str:
        return self.browser.get_text(*self.PROGRESS_MESSAGE)

    def is_generation_complete(self) -> bool:
        return self.browser.is_element_displayed(*self.SUCCESS_LINK)

    def get_result_href(self) -> str:
        return self.browser.get_attribute(*self.SUCCESS_LINK, attribute="href")

    def is_error_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.ERROR_MESSAGE)

    def get_error_text(self) -> str:
        return self.browser.get_text(*self.ERROR_MESSAGE)

    def count_theme_options(self) -> int:
        return len(self.browser.find_elements(*self.THEME_CARDS))
