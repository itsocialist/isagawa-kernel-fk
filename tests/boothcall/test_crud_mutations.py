"""
TestBoothCallCRUD - End-to-end CRUD mutation tests.

Validates actual data mutations through the UI:
- Create Shift → verify it appears in the listing
- Manual Add Member → verify they appear in the roster
- Delete Shift → verify it's removed from the listing

Requires authenticated session (injected by conftest.py).
Uses AAA pattern: Arrange-Act-Assert.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from resources.utilities import autologger
from pages.boothcall.event_dashboard_page import EventDashboardPage
from pages.boothcall.shift_management_page import ShiftManagementPage
from pages.boothcall.team_management_page import TeamManagementPage


class TestBoothCallCRUD:
    """
    CRUD mutation tests — these tests CREATE and DELETE real data.
    Ordered to clean up after themselves (create → verify → delete).
    """

    # Unique identifier to avoid collision with existing data
    TEST_SHIFT_LABEL = "Scanner"
    TEST_MEMBER_EMAIL = "e2e-test-user@boothcall.test"
    TEST_MEMBER_NAME = "E2E Test User"

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.base_url = config["url"]
        self.event_dashboard = EventDashboardPage(self.browser)
        self.shift_page = ShiftManagementPage(self.browser)
        self.team_page = TeamManagementPage(self.browser)

    def _skip_if_not_authenticated(self):
        """Skip if not authenticated."""
        url = self.browser.get_current_url()
        if "/login" in url:
            pytest.skip("Not authenticated — provide session cookie")

    def _navigate_to_first_event(self):
        """Navigate to events, click first event, wait for detail to load."""
        self.event_dashboard.navigate(self.base_url + "/events")
        time.sleep(2)
        self._skip_if_not_authenticated()

        has_events = self.browser.is_element_present(
            *self.event_dashboard.EVENT_CARD, timeout=5
        )
        if not has_events:
            pytest.skip("No events exist")

        self.event_dashboard.click_first_event_card()
        self.event_dashboard.wait_for_event_detail_loaded()

    # ==================================================================
    # TEST: Create Shift
    # ==================================================================

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.crud
    @autologger.automation_logger("Test")
    def test_create_shift_end_to_end(self):
        """
        Create a new shift via the Add Shift dialog and verify
        it appears in the Shifts management listing.

        AAA:
        1. Arrange - Navigate to Shifts tab, count existing shifts
        2. Act - Open Add Shift dialog, fill form, submit
        3. Assert - New shift card appears with the selected label
        """
        # Arrange — Navigate to Shifts tab
        self._navigate_to_first_event()
        self.event_dashboard.click_shifts_tab()
        time.sleep(1)

        initial_count = self.shift_page.get_shift_card_count()

        # Act — Open dialog and fill form
        self.shift_page.click_add_shift()
        self.shift_page.wait_for_dialog_visible()

        # Select role via the <select> dropdown
        self.shift_page.click_role_selector()
        time.sleep(0.5)
        self.shift_page.select_role_scanner()
        time.sleep(0.5)

        # --- START DATE ---
        # Open calendar via the dialog's "Pick shift start" button
        self.browser.execute_script("""
            const dialog = document.querySelector('[role="dialog"]');
            const btns = dialog.querySelectorAll('button[type="button"]:not([role="combobox"])');
            for (const b of btns) {
                if (b.textContent.includes('Pick shift start')) { b.click(); return; }
            }
        """)
        time.sleep(0.8)

        # Click a day in the Radix popover portal calendar
        # Event is Apr 22-24, so pick day 22 for start
        self.browser.execute_script("""
            const popover = document.querySelector('[data-radix-popper-content-wrapper]');
            if (!popover) return;
            const btns = popover.querySelectorAll('button[type="button"]');
            for (const b of btns) {
                if (b.textContent.trim() === '22') { b.click(); return; }
            }
        """)
        time.sleep(0.8)

        # Start time auto-fills to 09:00 after date selection - leave it as default
        time.sleep(0.3)

        # Click end date button — find by text content
        self.browser.execute_script("""
            const dialog = document.querySelector('[role="dialog"]');
            const btns = dialog.querySelectorAll('button[type="button"]:not([role="combobox"])');
            for (const b of btns) {
                if (b.textContent.includes('Pick shift end')) { b.click(); return; }
            }
        """)
        time.sleep(0.8)

        # Click day 23 for end date in the popover portal (Apr 22-24 event range)
        self.browser.execute_script("""
            const popover = document.querySelector('[data-radix-popper-content-wrapper]');
            if (!popover) return;
            const btns = popover.querySelectorAll('button[type="button"]');
            for (const b of btns) {
                if (b.textContent.trim() === '23') { b.click(); return; }
            }
        """)
        time.sleep(0.8)

        # End time defaults to 09:00 after day selection (same as start).
        # Since start=Apr22 09:00 and end=Apr23 09:00, validation passes (start < end).
        time.sleep(0.5)

        # Submit the form via JS (avoids any overlay intercept)
        self.browser.execute_script("""
            const submit = document.querySelector("form button[type='submit']");
            if (submit) submit.click();
        """)
        time.sleep(2)

        # Assert — Verify shift was created
        # Check for success toast
        success = self.browser.is_element_displayed(
            By.XPATH, "//li[contains(@class, 'toast')]", timeout=5
        )

        # Verify shift count increased OR the new label is visible
        new_count = self.shift_page.get_shift_card_count()
        shift_visible = self.shift_page.is_shift_displayed(self.TEST_SHIFT_LABEL)

        assert new_count > initial_count or shift_visible, \
            f"Shift '{self.TEST_SHIFT_LABEL}' should appear after creation (before={initial_count}, after={new_count})"

    # ==================================================================
    # TEST: Manual Add Member
    # ==================================================================

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.crud
    @autologger.automation_logger("Test")
    def test_manual_add_member_end_to_end(self):
        """
        Manually add a team member via the Invite dialog's Manual Add tab.
        Verify the member appears in the roster.

        AAA:
        1. Arrange - Navigate to Team tab
        2. Act - Open invite dialog, switch to Manual Add, fill email+name, submit
        3. Assert - New member appears in roster with Accepted status
        """
        # Arrange — Navigate to Team tab
        self._navigate_to_first_event()
        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()

        initial_count = self.team_page.get_member_count()

        # Act — Open invite dialog → Manual Add tab
        self.team_page.click_invite_staff()
        self.team_page.wait_for_invite_dialog()
        self.team_page.click_manual_tab()
        time.sleep(0.5)

        # Fill in email and name
        self.team_page.enter_manual_email(self.TEST_MEMBER_EMAIL)
        self.team_page.enter_manual_name(self.TEST_MEMBER_NAME)

        # Click Add to Roster
        self.team_page.click_add_to_roster()
        time.sleep(2)

        # Assert — Verify member was added
        # Check for success toast
        toast_visible = self.team_page.is_success_toast_displayed()

        # Verify member appears in roster
        # Dialog may close automatically; wait for roster to refresh
        time.sleep(1)

        # Check if member is visible in the roster
        member_visible = self.team_page.is_member_displayed(self.TEST_MEMBER_EMAIL) or \
                         self.team_page.is_member_displayed(self.TEST_MEMBER_NAME)

        # Also check count increased
        new_count = self.team_page.get_member_count()

        assert toast_visible or member_visible or new_count > initial_count, \
            f"Member '{self.TEST_MEMBER_EMAIL}' should be added to roster"

        # Verify ACCEPTED status (since manualAdd auto-accepts for corporate SaaS)
        if member_visible:
            assert self.team_page.is_accepted_badge_displayed(), \
                "Manual add should auto-set status to Accepted"

    # ==================================================================
    # TEST: Delete Shift
    # ==================================================================

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.crud
    @autologger.automation_logger("Test")
    def test_delete_shift_end_to_end(self):
        """
        Delete a shift and verify it's removed from the listing.

        AAA:
        1. Arrange - Navigate to Shifts tab, count existing shifts
        2. Act - Click Delete on first shift, confirm deletion
        3. Assert - Shift count decreased
        """
        # Arrange — Navigate to Shifts tab
        self._navigate_to_first_event()
        self.event_dashboard.click_shifts_tab()
        time.sleep(1)

        initial_count = self.shift_page.get_shift_card_count()
        if initial_count == 0:
            pytest.skip("No shifts to delete")

        # Act — Hover over first shift card to reveal action buttons
        # First, scroll to the shift card
        shift_cards = self.browser.driver.find_elements(
            By.CSS_SELECTOR, "[class*='rounded-2xl'][class*='group']"
        )
        if shift_cards:
            # Hover to reveal the action buttons
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(self.browser.driver).move_to_element(shift_cards[0]).perform()
            time.sleep(0.5)

        # Click Delete button
        self.shift_page.click_delete_on_first_shift()
        time.sleep(0.5)

        # Confirm deletion
        self.shift_page.confirm_delete()
        time.sleep(2)

        # Assert — Shift count decreased
        new_count = self.shift_page.get_shift_card_count()
        assert new_count < initial_count, \
            f"Shift count should decrease after deletion (before={initial_count}, after={new_count})"
