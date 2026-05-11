"""
EditingTasks - Task module

Orchestrates modal-based slide editing, drag-and-drop slide reordering,
and real-time preview interactions in the Living Decks editor.
"""

from interfaces.browser_interface import BrowserInterface
from pages.living_decks.editor_page import EditorPage
from resources.utilities import autologger


class EditingTasks:
    """
    Task module for presentation editing.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.editor_page = EditorPage(browser)

    @autologger.automation_logger("Task")
    def open_presentation_in_editor(self, filename: str) -> None:
        self.editor_page.navigate(filename)

    @autologger.automation_logger("Task")
    def edit_first_field_in_modal(self, new_text: str) -> None:
        """Open edit modal, replace first textarea content, apply changes, wait for auto-save."""
        (self.editor_page
            .click_edit_button()
            .edit_first_field(new_text)
            .click_apply_edits()
            .wait_for_auto_save())

    @autologger.automation_logger("Task")
    def reorder_slide(self, from_index: int, to_index: int) -> None:
        """Drag a slide thumbnail from one position to another."""
        self.editor_page.drag_slide_to_position(from_index, to_index)

    @autologger.automation_logger("Task")
    def wait_for_preview_to_reflect_edit(self) -> None:
        """Wait for the live preview iframe to reflect changes after apply."""
        self.editor_page.wait_for_preview_refresh()

    @autologger.automation_logger("Task")
    def regenerate_slide_with_ai(self, instruction: str) -> None:
        """Open edit modal, switch to Regenerate tab, enter instruction, confirm."""
        (self.editor_page
            .click_edit_button()
            .open_regen_tab()
            .enter_regen_prompt(instruction)
            .confirm_regeneration())

    @autologger.automation_logger("Task")
    def hover_slide_to_reveal_drag_handle(self, slide_index: int) -> None:
        """Hover over a slide thumbnail to trigger drag handle visibility."""
        thumbs = self.browser.find_elements(*self.editor_page.SLIDE_THUMBS)
        self.browser.hover_over(thumbs[slide_index])
