"""
Living Decks — Phase 2 Slide Editing Tests

BDD Acceptance Criteria:
- GIVEN a presentation is open in the editor
  WHEN the user clicks the Edit button (or presses 'e')
  THEN the slide editor modal opens with text fields for the current slide

- GIVEN the edit modal is open
  WHEN the user edits a text field and clicks Apply Changes
  THEN the preview iframe updates to show the new content

- GIVEN an edit has been applied (setDirty triggered)
  WHEN 1500ms auto-save debounce elapses
  THEN save-status shows 'Saved' confirming PUT /api/presentations/:filename succeeded

- GIVEN a presentation was edited and auto-saved
  WHEN the editor is reloaded with the same filename
  THEN the edited content persists in the slide
"""

import time
import pytest
from roles.living_decks.editor_role import EditorRole
from pages.living_decks.editor_page import EditorPage


class TestEditModalOpens:
    """Edit modal launches from the toolbar Edit button."""

    def test_edit_button_opens_modal(self, browser, test_presentation_filename):
        """GIVEN a presentation is open in the editor
        WHEN the user clicks the Edit button
        THEN the edit modal appears with text fields"""
        page = EditorPage(browser)
        page.navigate(test_presentation_filename)
        page.click_edit_button()

        assert page.is_edit_modal_visible(), \
            "Edit modal must open when the Edit button is clicked"

    def test_modal_has_editable_fields(self, browser, test_presentation_filename):
        """GIVEN the edit modal is open
        WHEN the Content tab is active
        THEN at least one textarea field is present for editing"""
        page = EditorPage(browser)
        page.navigate(test_presentation_filename)
        page.click_edit_button()

        fields = browser.find_elements(*page.EDIT_FIELDS)
        assert len(fields) > 0, \
            "Edit modal must contain textarea fields for the slide content"


class TestApplyEditsUpdatesPreview:
    """Apply Changes reflects edits in the preview iframe."""

    def test_apply_changes_closes_modal(self, browser, test_presentation_filename):
        """GIVEN the edit modal is open
        WHEN the user clicks Apply Changes
        THEN the modal closes"""
        page = EditorPage(browser)
        page.navigate(test_presentation_filename)
        page.click_edit_button()
        page.edit_first_field("Modal Apply Test Content")
        page.click_apply_edits()

        assert not page.is_edit_modal_visible(), \
            "Edit modal must close after Apply Changes is clicked"

    def test_applied_edit_appears_in_preview(self, browser, test_presentation_filename):
        """GIVEN the user edits a field and clicks Apply
        WHEN the preview iframe updates (via srcdoc)
        THEN the new text is present in the iframe body"""
        page = EditorPage(browser)
        page.navigate(test_presentation_filename)
        page.click_edit_button()
        page.edit_first_field("Preview Update Test Content")
        page.click_apply_edits()

        page.switch_to_preview_iframe()
        try:
            body_text = browser.driver.find_element_by_tag_name("body").text
        finally:
            page.switch_to_main_content()

        assert "Preview Update Test Content" in body_text, \
            "Preview iframe must show edited content immediately after Apply Changes"


class TestAutoSave:
    """Auto-save fires after edits and persists content."""

    def test_auto_save_fires_after_edit(self, browser, test_presentation_filename):
        """GIVEN an edit was applied (isDirty = true)
        WHEN 1500ms auto-save debounce elapses
        THEN save-status shows 'Saved'"""
        page = EditorPage(browser)
        page.navigate(test_presentation_filename)
        page.click_edit_button()
        page.edit_first_field("Auto-Save Trigger Test")
        page.click_apply_edits()
        page.wait_for_auto_save(2000)

        assert page.is_save_status_saved(), \
            "Save status must show 'Saved' after auto-save debounce — PUT /api/presentations/:filename"

    def test_edited_content_persists_after_reload(self, browser, test_presentation_filename):
        """GIVEN a block was edited, Apply clicked, and auto-save completed
        WHEN the editor page is reloaded with the same filename
        THEN the edited content is still present"""
        edited_text = "Persisted Content After Reload"
        role = EditorRole(browser)
        role.open_and_edit_first_field(test_presentation_filename, edited_text)

        page = EditorPage(browser)
        page.navigate(test_presentation_filename)
        page.click_edit_button()
        fields = browser.find_elements(*page.EDIT_FIELDS)
        field_values = [f.get_attribute("value") or f.text for f in fields]
        page.close_edit_modal()

        assert any(edited_text in v for v in field_values), \
            f"Edited content '{edited_text}' must persist after reload and auto-save"
