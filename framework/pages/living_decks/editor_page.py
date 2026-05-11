"""
EditorPage - Page Object Model

Page Object for the Living Decks presentation editor (/editor).
Handles: modal-based slide editing, drag-and-drop slide reordering (thumbnail nav),
real-time preview iframe, and auto-save status.
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from interfaces.browser_interface import BrowserInterface


class EditorPage:
    """
    Page Object for the editor interface.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    BASE_URL = "http://localhost:5550"

    # ==================== LOCATORS ====================

    # Slide thumbnail nav (drag-and-drop target)
    SLIDE_THUMBS          = (By.CSS_SELECTOR, ".slide-thumb")
    DRAG_HANDLES          = (By.CSS_SELECTOR, ".slide-thumb-drag")

    # Preview iframe
    PREVIEW_IFRAME        = (By.CSS_SELECTOR, "#preview-frame, iframe.preview")

    # Save state
    SAVE_STATUS           = (By.CSS_SELECTOR, "#save-status, .save-status")

    # Modal-based editing
    EDIT_BUTTON           = (By.CSS_SELECTOR, "#edit-btn")
    EDIT_MODAL            = (By.CSS_SELECTOR, "#edit-modal, .edit-overlay")
    EDIT_FIELDS           = (By.CSS_SELECTOR, "#edit-modal .edit-field textarea, .edit-overlay .edit-field textarea")
    APPLY_BUTTON          = (By.CSS_SELECTOR, "#edit-modal .toolbar-btn.primary, .edit-overlay .toolbar-btn.primary")
    CLOSE_MODAL_BUTTON    = (By.CSS_SELECTOR, "#edit-modal .edit-panel-close, .edit-overlay .edit-panel-close")

    # AI regeneration (inside modal)
    REGEN_TAB             = (By.CSS_SELECTOR, ".edit-tab[data-tab='regenerate']")
    REGEN_PROMPT_INPUT    = (By.CSS_SELECTOR, "#regenerate-prompt")
    REGEN_CONFIRM_BUTTON  = (By.CSS_SELECTOR, "#regenerate-btn")

    UNDO_BUTTON           = (By.CSS_SELECTOR, ".undo-btn, [data-action='undo'], button[title*='Undo']")

    def __init__(self, browser: BrowserInterface):
        """Compose BrowserInterface — NO inheritance."""
        self.browser = browser

    # ==================== NAVIGATION ====================

    def navigate(self, filename: str = "") -> "EditorPage":
        url = f"{self.BASE_URL}/editor"
        if filename:
            url += f"?file={filename}"
        self.browser.navigate_to(url)
        return self

    # ==================== MODAL EDITING ====================

    def click_edit_button(self) -> "EditorPage":
        """Click the Edit toolbar button to open the slide editor modal."""
        self.browser.click(*self.EDIT_BUTTON)
        return self

    def edit_first_field(self, text: str) -> "EditorPage":
        """Clear the first textarea in the edit modal and type new text."""
        fields = self.browser.find_elements(*self.EDIT_FIELDS)
        field = fields[0]
        field.clear()
        field.send_keys(text)
        return self

    def edit_field(self, field_index: int, text: str) -> "EditorPage":
        """Clear a textarea at field_index in the edit modal and type new text."""
        fields = self.browser.find_elements(*self.EDIT_FIELDS)
        field = fields[field_index]
        field.clear()
        field.send_keys(text)
        return self

    def click_apply_edits(self) -> "EditorPage":
        """Click Apply Changes in the edit modal."""
        self.browser.click(*self.APPLY_BUTTON)
        return self

    def close_edit_modal(self) -> "EditorPage":
        """Click the × close button in the edit modal."""
        self.browser.click(*self.CLOSE_MODAL_BUTTON)
        return self

    # ==================== DRAG-AND-DROP REORDERING ====================

    def drag_slide_to_position(self, from_index: int, to_index: int) -> "EditorPage":
        """Drag slide thumbnail at from_index to to_index position."""
        thumbs = self.browser.find_elements(*self.SLIDE_THUMBS)
        source = thumbs[from_index]
        target = thumbs[to_index]
        ActionChains(self.browser.driver)\
            .click_and_hold(source)\
            .move_to_element(target)\
            .release()\
            .perform()
        return self

    def get_slide_order(self) -> list:
        """Return list of slide title identifiers in current thumbnail DOM order."""
        thumbs = self.browser.find_elements(*self.SLIDE_THUMBS)
        order = []
        for thumb in thumbs:
            title = thumb.get_attribute("data-slide-title")
            if title:
                order.append(title)
            else:
                order.append(thumb.get_attribute("data-index") or "unknown")
        return order

    def wait_for_auto_save(self, timeout_ms: int = 2000) -> "EditorPage":
        """Wait for auto-save debounce (1500ms) plus buffer to complete."""
        time.sleep(timeout_ms / 1000)
        return self

    # ==================== LIVE PREVIEW ====================

    def wait_for_preview_refresh(self, debounce_ms: int = 800, extra_ms: int = 500) -> "EditorPage":
        """Wait for the preview iframe to reflect changes after debounce."""
        time.sleep((debounce_ms + extra_ms) / 1000)
        return self

    def get_preview_iframe_src(self) -> str:
        return self.browser.get_attribute(*self.PREVIEW_IFRAME, attribute="src")

    def switch_to_preview_iframe(self) -> "EditorPage":
        iframe = self.browser.find_element(*self.PREVIEW_IFRAME)
        self.browser.driver.switch_to.frame(iframe)
        return self

    def switch_to_main_content(self) -> "EditorPage":
        self.browser.driver.switch_to.default_content()
        return self

    # ==================== AI REGENERATION ====================

    def open_regen_tab(self) -> "EditorPage":
        """Switch to the Regenerate tab inside the edit modal."""
        self.browser.click(*self.REGEN_TAB)
        return self

    def enter_regen_prompt(self, instruction: str) -> "EditorPage":
        self.browser.clear_and_type(*self.REGEN_PROMPT_INPUT, instruction)
        return self

    def confirm_regeneration(self) -> "EditorPage":
        self.browser.click(*self.REGEN_CONFIRM_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def count_slides(self) -> int:
        return len(self.browser.find_elements(*self.SLIDE_THUMBS))

    def is_edit_modal_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.EDIT_MODAL)

    def is_save_status_saved(self) -> bool:
        text = self.browser.get_text(*self.SAVE_STATUS).lower()
        return "saved" in text

    def is_save_status_saving(self) -> bool:
        text = self.browser.get_text(*self.SAVE_STATUS).lower()
        return "saving" in text

    def is_preview_iframe_present(self) -> bool:
        return self.browser.is_element_displayed(*self.PREVIEW_IFRAME)

    def is_drag_handle_visible_on_slide(self, slide_index: int = 0) -> bool:
        """Check drag handle visibility via computed CSS opacity (not display)."""
        thumbs = self.browser.find_elements(*self.SLIDE_THUMBS)
        try:
            handle = thumbs[slide_index].find_element(By.CSS_SELECTOR, ".slide-thumb-drag")
            opacity = self.browser.execute_script(
                "return window.getComputedStyle(arguments[0]).opacity", handle
            )
            return float(opacity) > 0.1
        except Exception:
            return False

    def is_undo_available(self) -> bool:
        return self.browser.is_element_displayed(*self.UNDO_BUTTON)
