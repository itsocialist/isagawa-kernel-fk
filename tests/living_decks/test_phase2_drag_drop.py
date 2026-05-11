"""
Living Decks — Phase 2 Drag-and-Drop Slide Reordering Tests

BDD Acceptance Criteria:
- GIVEN the editor has 5 slides
  WHEN the user drags slide at index 2 to index 0
  THEN the DOM order updates immediately to reflect the new position

- GIVEN a slide has been dragged to a new position
  WHEN the editor auto-saves
  THEN reloading the editor shows the new slide order (persisted)

- GIVEN the editor is in default state
  WHEN the user hovers over a slide
  THEN a drag handle becomes visible (not permanently shown)

- GIVEN a drag-and-drop reorder was performed
  WHEN the user clicks Undo
  THEN the slides return to their previous order
"""

import pytest
from roles.living_decks.editor_role import EditorRole
from pages.living_decks.editor_page import EditorPage


class TestDragDropReorder:
    """Drag-and-drop slide reordering behavior."""

    def test_drag_changes_slide_dom_order(self, browser, test_presentation_filename):
        """GIVEN the editor has multiple slides
        WHEN the user drags slide index 2 to index 0
        THEN the DOM order reflects the new position immediately"""
        page = EditorPage(browser)
        page.navigate(test_presentation_filename)

        original_order = page.get_slide_order()
        assert len(original_order) >= 3, "Need at least 3 slides to test reorder"

        slide_that_moves = original_order[2]
        page.drag_slide_to_position(from_index=2, to_index=0)

        new_order = page.get_slide_order()
        assert new_order[0] == slide_that_moves, \
            f"Slide '{slide_that_moves}' should be at position 0 after drag, got: {new_order}"

    def test_reorder_persists_after_save_and_reload(self, browser, test_presentation_filename):
        """GIVEN a slide has been dragged to a new position and auto-saved
        WHEN the editor reloads
        THEN the new order is preserved"""
        page = EditorPage(browser)
        page.navigate(test_presentation_filename)

        original_order = page.get_slide_order()
        assert len(original_order) >= 3

        slide_that_moves = original_order[2]
        page.drag_slide_to_position(from_index=2, to_index=0)
        page.wait_for_auto_save(1200)

        # Reload and verify
        page.navigate(test_presentation_filename)
        new_order = page.get_slide_order()
        assert new_order[0] == slide_that_moves, \
            f"Reorder must persist after reload — expected '{slide_that_moves}' at 0, got: {new_order}"


class TestDragHandleAffordance:
    """Drag handle UX — hover-reveal, not always-on."""

    def test_drag_handle_hidden_by_default(self, browser, test_presentation_filename):
        """GIVEN the editor is loaded
        WHEN no slide thumbnail is hovered
        THEN drag handles have opacity 0 (CSS hover-reveal pattern)"""
        page = EditorPage(browser)
        page.navigate(test_presentation_filename)

        # Move mouse away from slide nav to clear any hover state
        browser.driver.execute_script(
            "document.getElementById('editor-select').focus();"
        )

        assert not page.is_drag_handle_visible_on_slide(0), \
            "Drag handles must be hidden by default — revealed only on hover"

    def test_drag_handle_appears_on_hover(self, browser, test_presentation_filename):
        """GIVEN the editor is loaded
        WHEN the user hovers over a slide
        THEN the drag handle becomes visible"""
        from tasks.living_decks.editing_tasks import EditingTasks
        tasks = EditingTasks(browser)
        page = EditorPage(browser)

        page.navigate(test_presentation_filename)
        tasks.hover_slide_to_reveal_drag_handle(0)

        assert page.is_drag_handle_visible_on_slide(0), \
            "Drag handle must appear on hover (CSS :hover or JS mouseenter)"


class TestDragDropUndo:
    """Undo after drag-and-drop."""

    def test_undo_restores_slide_order(self, browser, test_presentation_filename):
        """GIVEN slides were reordered by drag-and-drop
        WHEN the user clicks Undo
        THEN the slide order returns to its state before the drag"""
        page = EditorPage(browser)
        page.navigate(test_presentation_filename)

        original_order = page.get_slide_order()
        assert len(original_order) >= 3

        page.drag_slide_to_position(from_index=2, to_index=0)
        assert page.is_undo_available(), "Undo button must appear after a reorder action"

        # Click undo via JS if no direct method (undo button may be keyboard shortcut)
        browser.driver.find_element_by_css_selector(
            ".undo-btn, [data-action='undo']"
        ).click()

        restored_order = page.get_slide_order()
        assert restored_order == original_order, \
            f"Undo must restore original order. Expected: {original_order}, got: {restored_order}"
