"""
EditorRole - Role module

Represents a user who opens an existing presentation and edits it in Living Decks.
"""

from interfaces.browser_interface import BrowserInterface
from resources.utilities import autologger
from tasks.living_decks.editing_tasks import EditingTasks
from tasks.living_decks.gallery_tasks import GalleryTasks
from pages.living_decks.editor_page import EditorPage


class EditorRole:
    """
    Editor — opens existing presentations and edits slide content via the modal editor.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - NO return values
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.editing_tasks = EditingTasks(browser)
        self.gallery_tasks = GalleryTasks(browser)
        self.editor_page = EditorPage(browser)

    @autologger.automation_logger("Role")
    def open_and_edit_first_field(self, filename: str, new_text: str) -> None:
        """Open a presentation in the editor and edit the first field in the modal."""
        self.editing_tasks.open_presentation_in_editor(filename)
        self.editing_tasks.edit_first_field_in_modal(new_text)

    @autologger.automation_logger("Role")
    def open_and_reorder_slides(self, filename: str, from_index: int, to_index: int) -> None:
        """Open a presentation and drag a slide thumbnail to a new position."""
        self.editing_tasks.open_presentation_in_editor(filename)
        self.editing_tasks.reorder_slide(from_index, to_index)

    @autologger.automation_logger("Role")
    def edit_and_verify_live_preview(self, filename: str, new_text: str) -> None:
        """Edit the first field and wait for the live preview iframe to reflect the change."""
        self.editing_tasks.open_presentation_in_editor(filename)
        self.editing_tasks.edit_first_field_in_modal(new_text)
        self.editing_tasks.wait_for_preview_to_reflect_edit()

    @autologger.automation_logger("Role")
    def open_from_gallery_and_edit(self, card_index: int, new_text: str) -> None:
        """Navigate via gallery → editor → edit the first field."""
        self.gallery_tasks.navigate_to_gallery()
        self.gallery_tasks.navigate_to_editor_from_gallery(card_index)
        self.editing_tasks.edit_first_field_in_modal(new_text)
