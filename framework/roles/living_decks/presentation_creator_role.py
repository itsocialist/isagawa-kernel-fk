"""
PresentationCreatorRole - Role module

Represents a user who generates and shares presentations in Living Decks.
"""

from interfaces.browser_interface import BrowserInterface
from resources.utilities import autologger
from tasks.living_decks.generation_tasks import GenerationTasks
from tasks.living_decks.gallery_tasks import GalleryTasks
from pages.living_decks.generate_page import GeneratePage
from pages.living_decks.gallery_page import GalleryPage


class PresentationCreatorRole:
    """
    Presentation creator — generates decks and shares them.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - NO return values
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.generation_tasks = GenerationTasks(browser)
        self.gallery_tasks = GalleryTasks(browser)
        self.generate_page = GeneratePage(browser)
        self.gallery_page = GalleryPage(browser)

    @autologger.automation_logger("Role")
    def generate_and_wait(self, prompt: str, theme: str = "technical-dark") -> None:
        """Generate a deck from prompt and wait for completion."""
        self.generation_tasks.generate_deck_from_prompt(prompt, theme)
        self.generation_tasks.wait_for_generation_complete()

    @autologger.automation_logger("Role")
    def generate_boss_mode_and_wait(self, prompt: str) -> None:
        """Generate a Boss Mode deck and wait for completion."""
        self.generation_tasks.generate_boss_mode_deck(prompt)
        self.generation_tasks.wait_for_generation_complete()

    @autologger.automation_logger("Role")
    def import_pdf_generate_and_wait(self, pdf_path: str, guide_prompt: str = "") -> None:
        """Import a PDF, generate a deck, and wait for completion."""
        self.generation_tasks.import_pdf_and_generate(pdf_path, guide_prompt)
        self.generation_tasks.wait_for_generation_complete()

    @autologger.automation_logger("Role")
    def generate_then_share(self, prompt: str) -> None:
        """Generate a deck, navigate to gallery, and open the share dialog."""
        self.generate_and_wait(prompt)
        self.gallery_tasks.navigate_to_gallery()
        self.gallery_tasks.open_share_dialog_for_presentation(0)
