"""
GenerationTasks - Task module

Orchestrates AI presentation generation in Living Decks.
"""

from interfaces.browser_interface import BrowserInterface
from pages.living_decks.generate_page import GeneratePage
from resources.utilities import autologger


class GenerationTasks:
    """
    Task module for presentation generation.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.generate_page = GeneratePage(browser)

    @autologger.automation_logger("Task")
    def navigate_to_generator(self) -> None:
        self.generate_page.navigate()

    @autologger.automation_logger("Task")
    def generate_deck_from_prompt(self, prompt: str, theme: str = "technical-dark") -> None:
        """Navigate to generate, enter prompt, select theme, and submit."""
        (self.generate_page
            .navigate()
            .enter_prompt(prompt)
            .select_theme(theme)
            .click_generate())

    @autologger.automation_logger("Task")
    def generate_boss_mode_deck(self, prompt: str) -> None:
        """Generate with Boss Mode quality enabled."""
        (self.generate_page
            .navigate()
            .enter_prompt(prompt)
            .enable_boss_mode()
            .click_generate())

    @autologger.automation_logger("Task")
    def import_pdf_and_generate(self, pdf_path: str, guide_prompt: str = "") -> None:
        """Upload a PDF and optionally add a guiding prompt before generating."""
        self.generate_page.navigate().attach_pdf(pdf_path)
        if guide_prompt:
            self.generate_page.enter_guide_prompt(guide_prompt)
        self.generate_page.click_generate()

    @autologger.automation_logger("Task")
    def wait_for_generation_complete(self, timeout_seconds: int = 120) -> None:
        """Poll until the success link appears or timeout."""
        self.browser.wait_for_element_visible(
            *self.generate_page.SUCCESS_LINK,
            timeout=timeout_seconds
        )
