"""
GalleryTasks - Task module

Orchestrates gallery browsing, sharing, and navigation in Living Decks.
"""

from interfaces.browser_interface import BrowserInterface
from pages.living_decks.gallery_page import GalleryPage
from resources.utilities import autologger


class GalleryTasks:
    """
    Task module for gallery interactions.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.gallery_page = GalleryPage(browser)

    @autologger.automation_logger("Task")
    def navigate_to_gallery(self) -> None:
        self.gallery_page.navigate()

    @autologger.automation_logger("Task")
    def open_share_dialog_for_presentation(self, card_index: int = 0) -> None:
        """Click Share on the nth presentation card to surface the share link."""
        self.gallery_page.click_share_on_card(card_index)

    @autologger.automation_logger("Task")
    def copy_share_link(self) -> None:
        """Click the copy button once share dialog is open."""
        self.gallery_page.click_copy_link()

    @autologger.automation_logger("Task")
    def navigate_to_editor_from_gallery(self, card_index: int = 0) -> None:
        self.gallery_page.click_edit_on_card(card_index)

    @autologger.automation_logger("Task")
    def present_from_gallery(self, card_index: int = 0) -> None:
        self.gallery_page.click_present_on_card(card_index)
