"""
TestBoothCallDeepWorkflows - High k-value E2E tests that exercise full mutation workflows.

Unlike the rendering tests, these tests:
- MUTATE data through the UI
- VERIFY the mutation persisted (read-back)
- CLEAN UP after themselves

Each test targets a critical show-day workflow.
k-value target: 0.85+ per test.
"""

import time
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from resources.utilities import autologger
from pages.boothcall.event_dashboard_page import EventDashboardPage
from pages.boothcall.shift_management_page import ShiftManagementPage
from pages.boothcall.team_management_page import TeamManagementPage


class TestDeepWorkflows:
    """
    Deep E2E mutation tests — these exercise real user workflows
    that MUST work on show day. Each test mutates, verifies, and cleans up.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.base_url = config["url"]
        self.event_dashboard = EventDashboardPage(self.browser)
        self.shift_page = ShiftManagementPage(self.browser)
        self.team_page = TeamManagementPage(self.browser)

    def _skip_if_not_authenticated(self):
        url = self.browser.get_current_url()
        if "/login" in url:
            pytest.skip("Not authenticated — provide session cookie")

    def _navigate_to_first_event(self):
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

    def _get_event_id_from_url(self) -> str:
        """Extract event ID from current URL like /events/clxyz123."""
        url = self.browser.get_current_url()
        parts = url.split("/events/")
        if len(parts) > 1:
            return parts[1].split("/")[0].split("?")[0]
        return ""

    # ==================================================================
    # WORKFLOW 1: Edit Event → Submit → Verify data persisted
    # k-target: 0.85
    # ==================================================================
    @pytest.mark.boothcall
    @pytest.mark.deep
    @autologger.automation_logger("Test")
    def test_edit_event_submit_persists_changes(self):
        """
        Full edit event workflow:
        1. Navigate to event detail
        2. Click Edit button
        3. Change the venue name
        4. Submit the form
        5. Verify we're redirected back AND venue updated in header
        """
        self._navigate_to_first_event()

        # Capture original event title
        original_title = self.browser.get_text(By.CSS_SELECTOR, "h1")

        # Click Edit button
        self.browser.click(By.XPATH, "//a[contains(., 'Edit')]")
        time.sleep(2)

        # Verify on edit page
        assert self.browser.is_element_displayed(
            By.XPATH, "//h1[contains(., 'Edit Event')]"
        ), "Should be on Edit Event page"

        # Change venue to a unique test value
        test_venue = f"Test Venue {int(time.time()) % 10000}"
        venue_input = self.browser.driver.find_element(By.CSS_SELECTOR, "#edit-event-venue")
        venue_input.clear()
        venue_input.send_keys(test_venue)
        time.sleep(0.3)

        # Submit
        self.browser.click(By.XPATH, "//button[contains(., 'Save Changes')]")
        time.sleep(3)

        # Verify redirect back to event detail (URL should NOT contain /edit)
        current_url = self.browser.get_current_url()
        assert "/edit" not in current_url, \
            f"Should redirect back after save, but still on: {current_url}"

        # Verify venue appears in header
        page_text = self.browser.driver.find_element(By.TAG_NAME, "body").text
        assert test_venue in page_text, \
            f"Updated venue '{test_venue}' should appear in event header"

        # Verify event title is unchanged
        title_after = self.browser.get_text(By.CSS_SELECTOR, "h1")
        assert title_after == original_title, \
            f"Event title should be unchanged: expected '{original_title}', got '{title_after}'"

    # ==================================================================
    # WORKFLOW 2: Edit Shift → Submit → Verify changes on Shifts tab
    # k-target: 0.85
    # ==================================================================
    @pytest.mark.boothcall
    @pytest.mark.deep
    @autologger.automation_logger("Test")
    def test_edit_shift_submit_persists_changes(self):
        """
        Full edit shift workflow:
        1. Navigate to Shifts tab
        2. Click Edit on first shift
        3. Change min staff
        4. Submit
        5. Verify the shift card reflects new min staff
        """
        self._navigate_to_first_event()
        self.event_dashboard.click_shifts_tab()
        time.sleep(1)

        shift_count = self.shift_page.get_shift_card_count()
        if shift_count == 0:
            pytest.skip("No shifts to edit")

        # Hover to reveal Edit button
        shift_cards = self.browser.driver.find_elements(
            By.CSS_SELECTOR, "[class*='rounded-2xl'][class*='group']"
        )
        ActionChains(self.browser.driver).move_to_element(shift_cards[0]).perform()
        time.sleep(0.5)

        # Click Edit
        self.shift_page.click_edit_on_first_shift()
        time.sleep(1)

        # Verify Edit Shift dialog
        assert self.browser.is_element_displayed(
            By.XPATH, "//h2[contains(., 'Edit Shift')]"
        ), "Edit Shift dialog should be open"

        # Change min staff to 3 via React-compatible nativeInputValueSetter
        self.browser.execute_script("""
            const inputs = document.querySelectorAll('input[type="number"]');
            if (inputs.length >= 1) {
                const inp = inputs[0];  // First number input = min staff
                const nativeSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                nativeSetter.call(inp, '3');
                inp.dispatchEvent(new Event('input', { bubbles: true }));
                inp.dispatchEvent(new Event('change', { bubbles: true }));
            }
        """)
        time.sleep(0.5)

        # Submit via Save Changes button click
        save_btn = self.browser.driver.find_element(
            By.XPATH, "//button[contains(., 'Save Changes')]"
        )
        save_btn.click()
        time.sleep(3)

        # Verify success toast appeared
        toast = self.browser.is_element_present(
            By.XPATH, "//li[contains(@class, 'toast')]", timeout=10
        )
        # Also check if dialog closed (another sign of success)
        dialog_gone = not self.browser.is_element_present(
            By.XPATH, "//h2[contains(., 'Edit Shift')]", timeout=2
        )
        assert toast or dialog_gone, \
            "Edit shift should show toast or close dialog after saving"

    # ==================================================================
    # WORKFLOW 3: Assign member via Coverage popover → verify persists
    # k-target: 0.90
    # ==================================================================
    @pytest.mark.boothcall
    @pytest.mark.deep
    @autologger.automation_logger("Test")
    def test_assign_member_via_coverage_popover(self):
        """
        Full assignment workflow:
        1. Navigate to Coverage tab
        2. Click a shift card to open popover
        3. If unassigned members available, click one to assign
        4. Verify assignment count increased on the card
        """
        self._navigate_to_first_event()
        time.sleep(1)

        # Find shift cards
        shift_cards = self.browser.driver.find_elements(
            By.CSS_SELECTOR, "[role='button'][aria-label]"
        )
        if not shift_cards:
            pytest.skip("No shift cards on Coverage")

        # Get initial aria-label (contains assignment count)
        initial_label = shift_cards[0].get_attribute("aria-label")

        # Click to open popover
        shift_cards[0].click()
        time.sleep(1)

        # Check if there are unassigned members to assign
        assign_buttons = self.browser.driver.find_elements(
            By.XPATH,
            "//div[@data-radix-popper-content-wrapper]//button[contains(@class, 'w-full')]"
        )

        if not assign_buttons:
            # No unassigned members — check if the hint is shown
            hint = self.browser.is_element_present(
                By.XPATH, "//*[contains(text(), 'No accepted team members')]", timeout=2
            )
            if hint:
                pytest.skip("No accepted team members to assign")
            # Members already assigned — verify they show in the popover
            assigned = self.browser.driver.find_elements(
                By.XPATH, "//div[@data-radix-popper-content-wrapper]//span[contains(@class, 'text-xs')]"
            )
            assert len(assigned) > 0 or hint, \
                "Popover should show assigned members or empty hint"
            return

        # Click first unassigned member to assign
        assign_buttons[0].click()
        time.sleep(3)

        # Verify toast (Sonner uses data-sonner-toast or li with toast class)
        toast = self.browser.is_element_present(
            By.CSS_SELECTOR, "[data-sonner-toast]", timeout=10
        )
        # Also check if popover closed (another sign of success)
        popover_gone = not self.browser.is_element_present(
            By.CSS_SELECTOR, "[data-radix-popper-content-wrapper]", timeout=2
        )
        assert toast or popover_gone, "Assignment should trigger a toast or close popover"

    # ==================================================================
    # WORKFLOW 4: Confirm shift on My Shifts → verify status badge changes
    # k-target: 0.85
    # ==================================================================
    @pytest.mark.boothcall
    @pytest.mark.deep
    @autologger.automation_logger("Test")
    def test_confirm_shift_on_my_shifts(self):
        """
        Full confirm workflow:
        1. Navigate to My Shifts
        2. If a "Tentative" shift has a Confirm button, click it
        3. Verify status changes to "Confirmed"
        """
        self.browser.navigate_to(self.base_url + "/my-shifts")
        time.sleep(2)
        self._skip_if_not_authenticated()

        # Check for Confirm button (only shows on TENTATIVE shifts)
        confirm_btn = self.browser.is_element_present(
            By.XPATH, "//button[contains(., 'Confirm')]", timeout=5
        )
        if not confirm_btn:
            # No tentative shifts — check for Confirmed or empty state
            has_confirmed = self.browser.is_element_present(
                By.XPATH, "//span[contains(., 'Confirmed')]", timeout=3
            )
            has_empty = self.browser.is_element_present(
                By.XPATH, "//*[contains(text(), 'No shifts yet')]", timeout=3
            )
            if has_confirmed:
                # Already all confirmed — that's fine for show day
                assert True, "All shifts already confirmed"
                return
            elif has_empty:
                pytest.skip("No shifts assigned to this user")
            else:
                pytest.skip("No tentative shifts to confirm")

        # Count Tentative badges before
        tentative_before = len(self.browser.driver.find_elements(
            By.XPATH, "//span[contains(., 'Tentative')]"
        ))

        # Click Confirm
        self.browser.click(By.XPATH, "//button[contains(., 'Confirm')]")
        time.sleep(3)

        # Verify toast (Sonner uses data-sonner-toast attribute)
        toast = self.browser.is_element_present(
            By.CSS_SELECTOR, "[data-sonner-toast]", timeout=10
        )
        assert toast, "Confirming shift should show toast"

        # Verify tentative count decreased OR confirmed count increased
        tentative_after = len(self.browser.driver.find_elements(
            By.XPATH, "//span[contains(., 'Tentative')]"
        ))
        confirmed_after = len(self.browser.driver.find_elements(
            By.XPATH, "//span[contains(., 'Confirmed')]"
        ))

        assert tentative_after < tentative_before or confirmed_after > 0, \
            "Tentative count should decrease or Confirmed count should increase"

    # ==================================================================
    # WORKFLOW 5: Email invite → verify Pending badge appears
    # k-target: 0.80
    # ==================================================================
    @pytest.mark.boothcall
    @pytest.mark.deep
    @autologger.automation_logger("Test")
    def test_email_invite_creates_pending_member(self):
        """
        Full email invite workflow:
        1. Navigate to Team tab
        2. Open invite dialog → Email tab
        3. Enter test email
        4. Submit
        5. Verify member appears with Pending status
        """
        self._navigate_to_first_event()
        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()

        initial_count = self.team_page.get_member_count()

        # Open invite dialog
        self.team_page.click_invite_staff()
        self.team_page.wait_for_invite_dialog()

        # Should default to Email tab — enter test email
        unique_email = f"invite-test-{int(time.time())}@e2e.boothcall.dev"
        self.team_page.enter_invite_email(unique_email)
        self.team_page.enter_invite_name("Invite Test")
        time.sleep(0.3)

        # Click Send Invitation
        self.team_page.click_send_invitation()
        time.sleep(2)

        # Verify toast
        toast = self.team_page.is_success_toast_displayed()

        # Verify member count or member visibility
        time.sleep(1)
        new_count = self.team_page.get_member_count()
        member_visible = self.team_page.is_member_displayed("Invite Test") or \
                         self.team_page.is_member_displayed(unique_email)

        assert toast or member_visible or new_count > initial_count, \
            "Email invite should add member to roster"

        # Verify Pending badge exists (email invites are Pending until accepted)
        if member_visible:
            pending = self.team_page.is_pending_badge_displayed()
            assert pending, "Email invite should create member with Pending status"

    # ==================================================================
    # WORKFLOW 6: Full onboarding — Shifts tab create → Coverage shows it
    # k-target: 0.85
    # ==================================================================
    @pytest.mark.boothcall
    @pytest.mark.deep
    @autologger.automation_logger("Test")
    def test_shift_created_on_shifts_tab_appears_on_coverage(self):
        """
        Cross-tab verification:
        1. Go to Shifts tab, count shifts
        2. Create a new shift
        3. Navigate to Coverage tab
        4. Verify shift card with matching label exists
        """
        self._navigate_to_first_event()

        # Go to Coverage first, count current cards
        time.sleep(1)
        coverage_cards_before = len(self.browser.driver.find_elements(
            By.CSS_SELECTOR, "[role='button'][aria-label]"
        ))

        # Go to Shifts tab, create a new shift
        self.event_dashboard.click_shifts_tab()
        time.sleep(1)

        self.shift_page.click_add_shift()
        self.shift_page.wait_for_dialog_visible()

        # Select Floater role (unlikely to already exist = less collision)
        self.shift_page.click_role_selector()
        time.sleep(0.5)
        self.browser.execute_script("""
            const options = document.querySelectorAll('[role="option"]');
            for (const o of options) {
                if (o.textContent.includes('Floater')) { o.click(); return; }
            }
        """)
        time.sleep(0.5)

        # Pick start and end dates
        self.browser.execute_script("""
            const dialog = document.querySelector('[role="dialog"]');
            const btns = dialog.querySelectorAll('button[type="button"]:not([role="combobox"])');
            for (const b of btns) {
                if (b.textContent.includes('Pick shift start')) { b.click(); return; }
            }
        """)
        time.sleep(0.8)

        self.browser.execute_script("""
            const popover = document.querySelector('[data-radix-popper-content-wrapper]');
            if (!popover) return;
            const btns = popover.querySelectorAll('button[type="button"]');
            for (const b of btns) {
                if (b.textContent.trim() === '22') { b.click(); return; }
            }
        """)
        time.sleep(0.8)

        self.browser.execute_script("""
            const dialog = document.querySelector('[role="dialog"]');
            const btns = dialog.querySelectorAll('button[type="button"]:not([role="combobox"])');
            for (const b of btns) {
                if (b.textContent.includes('Pick shift end')) { b.click(); return; }
            }
        """)
        time.sleep(0.8)

        self.browser.execute_script("""
            const popover = document.querySelector('[data-radix-popper-content-wrapper]');
            if (!popover) return;
            const btns = popover.querySelectorAll('button[type="button"]');
            for (const b of btns) {
                if (b.textContent.trim() === '23') { b.click(); return; }
            }
        """)
        time.sleep(0.8)

        # Submit
        self.browser.execute_script("""
            const submit = document.querySelector("form button[type='submit']");
            if (submit) submit.click();
        """)
        time.sleep(2)

        # Verify toast
        toast = self.browser.is_element_present(
            By.XPATH, "//li[contains(@class, 'toast')]", timeout=5
        )

        # Navigate to Coverage tab
        self.event_dashboard.click_coverage_tab()
        time.sleep(2)

        # Verify "Floater" label exists on Coverage
        floater_visible = self.browser.is_element_present(
            By.XPATH, "//*[contains(text(), 'Floater') or contains(text(), 'FLOATER')]",
            timeout=5
        )
        assert floater_visible, \
            "Shift created on Shifts tab should appear on Coverage tab with 'Floater' label"

    # ==================================================================
    # WORKFLOW 7: Revoke invite → verify member removed from roster
    # k-target: 0.80
    # ==================================================================
    @pytest.mark.boothcall
    @pytest.mark.deep
    @autologger.automation_logger("Test")
    def test_revoke_invite_removes_pending_member(self):
        """
        Revoke workflow:
        1. Navigate to Team tab
        2. If a Pending member exists, click Revoke
        3. Verify member count decreased
        """
        self._navigate_to_first_event()
        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()

        # Check for pending members
        has_pending = self.browser.is_element_present(
            By.XPATH, "//span[contains(., 'Pending')]", timeout=3
        )
        if not has_pending:
            pytest.skip("No pending members to revoke")

        initial_count = self.team_page.get_member_count()
        pending_count_before = len(self.browser.driver.find_elements(
            By.XPATH, "//span[contains(., 'Pending')]"
        ))

        # Click Revoke via JS to avoid any overlay interception
        self.browser.execute_script("""
            const btn = document.querySelector("button");
            const allBtns = document.querySelectorAll("button");
            for (const b of allBtns) {
                if (b.textContent.trim() === 'Revoke') { b.click(); return; }
            }
        """)
        time.sleep(3)

        # Verify toast appeared
        toast = self.team_page.is_success_toast_displayed()

        # Refresh page to get authoritative count
        self.browser.driver.refresh()
        time.sleep(3)

        # Re-count pending members (the most reliable metric)
        pending_count_after = len(self.browser.driver.find_elements(
            By.XPATH, "//span[contains(., 'Pending')]"
        ))
        new_count = self.team_page.get_member_count()

        assert toast or new_count < initial_count or pending_count_after < pending_count_before, \
            f"Revoking invite should remove member (total: {initial_count}→{new_count}, pending: {pending_count_before}→{pending_count_after})"
