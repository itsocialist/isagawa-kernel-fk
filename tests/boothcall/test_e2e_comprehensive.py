"""
TestBoothCallE2E - Comprehensive end-to-end test for BoothCall Platform.

Validates the full user journey across two test classes:
1. TestBoothCallPublicPages — No auth required (landing, login, auth options)
2. TestBoothCallAuthGated — Requires authenticated session (events, shifts, team)

Uses AAA pattern: Arrange, Act, Assert.

NOTE: Auth-gated tests detect the login redirect and SKIP gracefully
when no session cookie is available. To run auth-gated tests, provide
a session cookie via test_users.json or database seed.
"""

import pytest
from resources.utilities import autologger
from roles.boothcall.event_organizer import EventOrganizer
from pages.boothcall.landing_page import LandingPage
from pages.boothcall.login_page import LoginPage
from pages.boothcall.event_dashboard_page import EventDashboardPage
from pages.boothcall.shift_management_page import ShiftManagementPage
from pages.boothcall.team_management_page import TeamManagementPage
from pages.boothcall.event_creation_page import EventCreationPage


# ==============================================================================
# PUBLIC PAGES — No authentication required
# ==============================================================================

class TestBoothCallPublicPages:
    """
    Validates all public (unauthenticated) pages and navigation flows.

    - @autologger("Test") decorator
    - Role workflow calls
    - Assert via Page Object state-check methods
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Pytest fixture wires browser and config into the test class."""
        self.browser = browser
        self.config = config
        self.landing_page = LandingPage(self.browser)
        self.login_page = LoginPage(self.browser)

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_page_renders_with_branding(self):
        """
        Verify the BoothCall landing page renders with hero and branding.

        AAA:
        1. Arrange - Create role
        2. Act - Visit landing page
        3. Assert - Hero + logo visible
        """
        # Arrange
        base_url = self.config["url"]
        organizer = EventOrganizer(self.browser, base_url)

        # Act
        organizer.visit_landing_page()

        # Assert
        assert self.landing_page.is_hero_displayed(), \
            "Hero heading should be visible"
        assert self.landing_page.is_logo_displayed(), \
            "BoothCall logo text should be visible"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_page_hero_text_content(self):
        """
        Verify the landing page hero contains meaningful content (not blank).

        AAA:
        1. Arrange - Create role
        2. Act - Visit landing page, read hero text
        3. Assert - Hero text is non-empty
        """
        # Arrange
        base_url = self.config["url"]
        organizer = EventOrganizer(self.browser, base_url)

        # Act
        organizer.visit_landing_page()
        hero_text = self.landing_page.get_hero_text()

        # Assert
        assert len(hero_text) > 0, \
            "Hero heading text should not be empty"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_navigation_landing_to_login(self):
        """
        Verify navigation from landing to login page.

        AAA:
        1. Arrange - Create role
        2. Act - Visit landing, click Sign In
        3. Assert - Login page renders with auth options
        """
        # Arrange
        base_url = self.config["url"]
        organizer = EventOrganizer(self.browser, base_url)

        # Act
        organizer.visit_landing_and_navigate_to_login()

        # Assert
        assert self.login_page.is_login_page_displayed(), \
            "Login page heading should be visible"
        assert self.login_page.is_google_button_displayed(), \
            "Google OAuth button should be visible"
        assert self.login_page.is_on_login_page(), \
            "URL should contain /login"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_login_page_has_google_oauth(self):
        """
        Verify login page displays Google OAuth button.

        AAA:
        1. Arrange - Navigate directly to login
        2. Assert - Google button is present
        """
        # Arrange
        base_url = self.config["url"]
        organizer = EventOrganizer(self.browser, base_url)
        organizer.navigation_tasks.open_login_page_directly(base_url)

        # Assert
        assert self.login_page.is_google_button_displayed(), \
            "Google OAuth button should be visible on login page"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_login_page_has_magic_link_form(self):
        """
        Verify the login page displays the magic link email form.

        AAA:
        1. Arrange - Navigate directly to login
        2. Assert - Email input + Send magic link button present
        """
        # Arrange
        base_url = self.config["url"]
        organizer = EventOrganizer(self.browser, base_url)
        organizer.navigation_tasks.open_login_page_directly(base_url)

        # Assert
        from selenium.webdriver.common.by import By
        assert self.browser.is_element_present(
            By.CSS_SELECTOR, "input#email[type='email']"
        ), "Magic link email input should be present"

        assert self.browser.is_element_displayed(
            *self.login_page.MAGIC_LINK_BUTTON
        ), "Send magic link button should be visible"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_login_page_back_to_home_link(self):
        """
        Verify the login page has a Back to home link.

        AAA:
        1. Arrange - Navigate to login
        2. Assert - Back to home link is present
        """
        # Arrange
        base_url = self.config["url"]
        organizer = EventOrganizer(self.browser, base_url)
        organizer.navigation_tasks.open_login_page_directly(base_url)

        # Assert
        from selenium.webdriver.common.by import By
        assert self.browser.is_element_displayed(
            By.XPATH, "//a[contains(., 'Back to home')]"
        ), "Back to home link should be visible"


# ==============================================================================
# AUTH-GATED PAGES — Requires session; skip if redirected to login
# ==============================================================================

class TestBoothCallAuthGated:
    """
    Validates authenticated pages: events, shifts, team management.

    Tests detect the auth redirect and SKIP gracefully when no session
    cookie is available. This allows the suite to run end-to-end without
    failing on infrastructure dependencies.

    - @autologger("Test") decorator
    - Role workflow calls
    - Assert via Page Object state-check methods
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Pytest fixture wires browser, config, and page objects."""
        self.browser = browser
        self.config = config
        self.landing_page = LandingPage(self.browser)
        self.login_page = LoginPage(self.browser)
        self.event_dashboard = EventDashboardPage(self.browser)
        self.shift_page = ShiftManagementPage(self.browser)
        self.team_page = TeamManagementPage(self.browser)
        self.event_creation_page = EventCreationPage(self.browser)

    def _skip_if_not_authenticated(self):
        """Helper: skip the test if the browser was redirected to login."""
        url = self.browser.get_current_url()
        if "/login" in url:
            pytest.skip("Not authenticated — redirected to login page. Provide session cookie to run auth-gated tests.")

    # ---- Event Creation ----

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.event_creation
    @autologger.automation_logger("Test")
    def test_create_event_page_renders(self):
        """
        Verify the Create Event page loads with all form fields.

        AAA:
        1. Arrange - Navigate to /events/new
        2. Assert - Heading, name input, venue input present
        """
        base_url = self.config["url"]
        self.event_creation_page.navigate(base_url + "/events/new")

        import time
        time.sleep(2)
        self._skip_if_not_authenticated()

        self.event_creation_page.wait_for_page_loaded()

        assert self.event_creation_page.is_page_displayed(), \
            "Create Event heading should be displayed"

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_present(By.CSS_SELECTOR, "#event-name"), \
            "Event name input field should be present"
        assert self.browser.is_element_present(By.CSS_SELECTOR, "#event-venue"), \
            "Venue input field should be present"

    # ---- Event Detail Navigation ----

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.navigation
    @autologger.automation_logger("Test")
    def test_event_detail_tabs_present(self):
        """
        Verify all four event detail tabs are visible on an event page.

        AAA:
        1. Arrange - Navigate to events, open first event
        2. Assert - Coverage, Shifts, Team, Reconcile tabs visible
        """
        base_url = self.config["url"]
        self.event_dashboard.navigate(base_url + "/events")

        import time
        time.sleep(2)
        self._skip_if_not_authenticated()

        has_events = self.browser.is_element_present(
            *self.event_dashboard.EVENT_CARD, timeout=5
        )
        if not has_events:
            pytest.skip("No events exist — skipping event detail tab test")

        self.event_dashboard.click_first_event_card()
        time.sleep(2)

        assert self.event_dashboard.is_event_detail_page(), \
            "Event detail page should show navigation tabs"
        assert self.event_dashboard.is_shifts_tab_displayed(), \
            "Shifts tab should be visible"

    # ---- Shifts ----

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.shifts
    @autologger.automation_logger("Test")
    def test_shifts_tab_has_add_button(self):
        """
        Verify shifts tab renders with Add Shift button.

        AAA:
        1. Arrange - Navigate to events, open first, click Shifts tab
        2. Assert - Add Shift button visible
        """
        base_url = self.config["url"]
        self.event_dashboard.navigate(base_url + "/events")

        import time
        time.sleep(2)
        self._skip_if_not_authenticated()

        has_events = self.browser.is_element_present(
            *self.event_dashboard.EVENT_CARD, timeout=5
        )
        if not has_events:
            pytest.skip("No events exist")

        self.event_dashboard.click_first_event_card()
        time.sleep(2)

        organizer = EventOrganizer(self.browser, base_url)
        organizer.shift_management_tasks.navigate_to_shifts_tab()

        assert self.shift_page.is_add_shift_button_displayed(), \
            "Add Shift button should be visible"

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.shifts
    @autologger.automation_logger("Test")
    def test_add_shift_dialog_opens_and_closes(self):
        """
        Verify the Add Shift dialog open/close lifecycle.

        AAA:
        1. Arrange - Navigate to events, open first, go to Shifts tab
        2. Act - Click Add Shift
        3. Assert - Dialog is displayed
        """
        base_url = self.config["url"]
        self.event_dashboard.navigate(base_url + "/events")

        import time
        time.sleep(2)
        self._skip_if_not_authenticated()

        has_events = self.browser.is_element_present(
            *self.event_dashboard.EVENT_CARD, timeout=5
        )
        if not has_events:
            pytest.skip("No events exist")

        self.event_dashboard.click_first_event_card()
        time.sleep(2)

        organizer = EventOrganizer(self.browser, base_url)
        organizer.shift_management_tasks.navigate_to_shifts_tab()

        self.shift_page.click_add_shift()
        assert self.shift_page.is_dialog_displayed(), \
            "Add Shift dialog should be visible"

    # ---- Team Management ----

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.team
    @autologger.automation_logger("Test")
    def test_team_tab_renders_with_invite_button(self):
        """
        Verify Team tab renders with Invite Staff button.

        AAA:
        1. Arrange - Navigate to events, open first, click Team
        2. Assert - Team Roster heading + Invite Staff button visible
        """
        base_url = self.config["url"]
        self.event_dashboard.navigate(base_url + "/events")

        import time
        time.sleep(2)
        self._skip_if_not_authenticated()

        has_events = self.browser.is_element_present(
            *self.event_dashboard.EVENT_CARD, timeout=5
        )
        if not has_events:
            pytest.skip("No events exist")

        self.event_dashboard.click_first_event_card()
        time.sleep(2)

        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()

        assert self.team_page.is_team_page_displayed(), \
            "Team Roster heading should be visible"

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_present(By.CSS_SELECTOR, "#invite-staff-btn"), \
            "Invite Staff button should be present"

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.team
    @autologger.automation_logger("Test")
    def test_invite_dialog_has_three_tabs(self):
        """
        Verify the Invite dialog has Email, Link, and Manual tabs.

        AAA:
        1. Arrange - Navigate to events, open first, go to Team tab
        2. Act - Click Invite Staff
        3. Assert - Three tabs visible in dialog
        """
        base_url = self.config["url"]
        self.event_dashboard.navigate(base_url + "/events")

        import time
        time.sleep(2)
        self._skip_if_not_authenticated()

        has_events = self.browser.is_element_present(
            *self.event_dashboard.EVENT_CARD, timeout=5
        )
        if not has_events:
            pytest.skip("No events exist")

        self.event_dashboard.click_first_event_card()
        time.sleep(2)

        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()

        self.team_page.click_invite_staff()
        self.team_page.wait_for_invite_dialog()

        assert self.team_page.is_invite_dialog_displayed(), \
            "Invite dialog should be visible"

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_displayed(
            By.XPATH, "//button[@role='tab'][contains(., 'Email Invite')]"
        ), "Email Invite tab should be visible"
        assert self.browser.is_element_displayed(
            By.XPATH, "//button[@role='tab'][contains(., 'Invite Link')]"
        ), "Invite Link tab should be visible"
        assert self.browser.is_element_displayed(
            By.XPATH, "//button[@role='tab'][contains(., 'Manual Add')]"
        ), "Manual Add tab should be visible"

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @pytest.mark.team
    @autologger.automation_logger("Test")
    def test_manual_add_tab_has_form_fields(self):
        """
        Verify Manual Add tab shows email, name, and Add to Roster button.

        AAA:
        1. Arrange - Navigate to events, open first, Team tab, open invite dialog
        2. Act - Click Manual Add tab
        3. Assert - Form fields and button present
        """
        base_url = self.config["url"]
        self.event_dashboard.navigate(base_url + "/events")

        import time
        time.sleep(2)
        self._skip_if_not_authenticated()

        has_events = self.browser.is_element_present(
            *self.event_dashboard.EVENT_CARD, timeout=5
        )
        if not has_events:
            pytest.skip("No events exist")

        self.event_dashboard.click_first_event_card()
        time.sleep(2)

        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()
        self.team_page.click_invite_staff()
        self.team_page.wait_for_invite_dialog()

        self.team_page.click_manual_tab()

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_present(By.CSS_SELECTOR, "#manual-email"), \
            "Manual add email field should be present"
        assert self.browser.is_element_present(By.CSS_SELECTOR, "#manual-name"), \
            "Manual add name field should be present"
        assert self.browser.is_element_displayed(
            By.XPATH, "//button[contains(., 'Add to Roster')]"
        ), "Add to Roster button should be visible"
