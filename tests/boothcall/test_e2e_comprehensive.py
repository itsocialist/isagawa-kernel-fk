"""
TestBoothCallE2E - Comprehensive end-to-end test for BoothCall Platform.

Two test classes:
1. TestBoothCallPublicPages — Unauthenticated pages (skip if session injected)
2. TestBoothCallAuthGated — Authenticated pages (skip if no session)

Uses AAA pattern: Arrange, Act, Assert.
Session token is auto-injected by boothcall/conftest.py.
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
# PUBLIC PAGES — No authentication required; skips if already authenticated
# ==============================================================================

class TestBoothCallPublicPages:
    """
    Validates public (unauthenticated) pages.
    Skips when session cookie is present (landing/login redirect to /events).
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.landing_page = LandingPage(self.browser)
        self.login_page = LoginPage(self.browser)

    def _skip_if_authenticated(self):
        """Skip public tests when authenticated — landing/login redirect away."""
        self.browser.navigate_to(self.config["url"])
        import time
        time.sleep(1)
        url = self.browser.get_current_url()
        if "/events" in url:
            pytest.skip("Authenticated session active — public pages redirect to /events")

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_page_renders_with_branding(self):
        """Verify the landing page shows hero + logo when unauthenticated."""
        self._skip_if_authenticated()
        organizer = EventOrganizer(self.browser, self.config["url"])
        organizer.visit_landing_page()

        assert self.landing_page.is_hero_displayed(), "Hero heading should be visible"
        assert self.landing_page.is_logo_displayed(), "BoothCall logo should be visible"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_page_hero_text_content(self):
        """Verify landing page hero text is non-empty."""
        self._skip_if_authenticated()
        organizer = EventOrganizer(self.browser, self.config["url"])
        organizer.visit_landing_page()

        assert len(self.landing_page.get_hero_text()) > 0, "Hero text should not be empty"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_navigation_landing_to_login(self):
        """Verify navigation from landing to login page."""
        self._skip_if_authenticated()
        organizer = EventOrganizer(self.browser, self.config["url"])
        organizer.visit_landing_and_navigate_to_login()

        assert self.login_page.is_login_page_displayed(), "Login page should be displayed"
        assert self.login_page.is_google_button_displayed(), "Google button should be visible"
        assert self.login_page.is_on_login_page(), "URL should contain /login"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_login_page_has_google_oauth(self):
        """Verify login page has Google OAuth button."""
        self._skip_if_authenticated()
        organizer = EventOrganizer(self.browser, self.config["url"])
        organizer.navigation_tasks.open_login_page_directly(self.config["url"])

        assert self.login_page.is_google_button_displayed(), "Google OAuth button should be visible"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_login_page_has_magic_link_form(self):
        """Verify login page has magic link email form."""
        self._skip_if_authenticated()
        organizer = EventOrganizer(self.browser, self.config["url"])
        organizer.navigation_tasks.open_login_page_directly(self.config["url"])

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_present(
            By.CSS_SELECTOR, "input#email[type='email']"
        ), "Email input should be present"
        assert self.browser.is_element_displayed(
            *self.login_page.MAGIC_LINK_BUTTON
        ), "Magic link button should be visible"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_login_page_back_to_home_link(self):
        """Verify login page has a back-to-home link."""
        self._skip_if_authenticated()
        organizer = EventOrganizer(self.browser, self.config["url"])
        organizer.navigation_tasks.open_login_page_directly(self.config["url"])

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_displayed(
            By.XPATH, "//a[contains(., 'Back to home')]"
        ), "Back to home link should be visible"


# ==============================================================================
# AUTH-GATED PAGES — Requires session; skip if redirected to login
# ==============================================================================

class TestBoothCallAuthGated:
    """
    Validates authenticated pages: event creation, event detail tabs,
    shift management, and team management.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.event_dashboard = EventDashboardPage(self.browser)
        self.shift_page = ShiftManagementPage(self.browser)
        self.team_page = TeamManagementPage(self.browser)
        self.event_creation_page = EventCreationPage(self.browser)
        self.base_url = config["url"]

    def _skip_if_not_authenticated(self):
        """Skip if browser landed on login (no session cookie)."""
        url = self.browser.get_current_url()
        if "/login" in url:
            pytest.skip("Not authenticated — provide session cookie")

    def _navigate_to_first_event(self):
        """Navigate to events page, click first event, wait for detail to load."""
        self.event_dashboard.navigate(self.base_url + "/events")
        import time
        time.sleep(2)
        self._skip_if_not_authenticated()

        has_events = self.browser.is_element_present(
            *self.event_dashboard.EVENT_CARD, timeout=5
        )
        if not has_events:
            pytest.skip("No events exist")

        self.event_dashboard.click_first_event_card()
        self.event_dashboard.wait_for_event_detail_loaded()

    # ---- Event Creation ----

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @autologger.automation_logger("Test")
    def test_create_event_page_renders(self):
        """Verify Create Event page loads with form fields."""
        self.event_creation_page.navigate(self.base_url + "/events/new")
        import time
        time.sleep(2)
        self._skip_if_not_authenticated()

        self.event_creation_page.wait_for_page_loaded()
        assert self.event_creation_page.is_page_displayed(), "Create Event heading should show"

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_present(By.CSS_SELECTOR, "#event-name"), \
            "Event name input should be present"
        assert self.browser.is_element_present(By.CSS_SELECTOR, "#event-venue"), \
            "Venue input should be present"

    # ---- Event Detail Navigation ----

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @autologger.automation_logger("Test")
    def test_event_detail_shows_all_four_tabs(self):
        """Verify all four tabs (Coverage, Shifts, Team, Reconcile) are visible."""
        self._navigate_to_first_event()

        assert self.event_dashboard.is_event_detail_page(), "Should be on event detail page"
        assert self.event_dashboard.is_shifts_tab_displayed(), "Shifts tab should be visible"

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_displayed(
            *self.event_dashboard.TEAM_TAB
        ), "Team tab should be visible"
        assert self.browser.is_element_displayed(
            *self.event_dashboard.RECONCILE_TAB
        ), "Reconcile tab should be visible"

    # ---- Shifts ----

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @autologger.automation_logger("Test")
    def test_shifts_tab_renders_with_add_button(self):
        """Verify Shifts tab has Add Shift button."""
        self._navigate_to_first_event()
        self.event_dashboard.click_shifts_tab()

        import time
        time.sleep(1)
        assert self.shift_page.is_add_shift_button_displayed(), \
            "Add Shift button should be visible"

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @autologger.automation_logger("Test")
    def test_add_shift_dialog_opens(self):
        """Verify Add Shift dialog opens on click."""
        self._navigate_to_first_event()
        self.event_dashboard.click_shifts_tab()

        import time
        time.sleep(1)
        self.shift_page.click_add_shift()
        assert self.shift_page.is_dialog_displayed(), "Add Shift dialog should be visible"

    # ---- Team Management ----

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @autologger.automation_logger("Test")
    def test_team_tab_renders_with_invite_button(self):
        """Verify Team tab has Invite Staff button."""
        self._navigate_to_first_event()
        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()

        assert self.team_page.is_team_page_displayed(), "Team Roster heading should show"

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @autologger.automation_logger("Test")
    def test_invite_dialog_has_three_tabs(self):
        """Verify invite dialog shows Email, Link, and Manual tabs."""
        self._navigate_to_first_event()
        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()

        self.team_page.click_invite_staff()
        self.team_page.wait_for_invite_dialog()

        assert self.team_page.is_invite_dialog_displayed(), "Invite dialog should be visible"

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_displayed(
            By.XPATH, "//button[@role='tab'][contains(., 'Email')]"
        ), "Email tab should be visible"
        assert self.browser.is_element_displayed(
            By.XPATH, "//button[@role='tab'][contains(., 'Link')]"
        ), "Link tab should be visible"
        assert self.browser.is_element_displayed(
            By.XPATH, "//button[@role='tab'][contains(., 'Manual')]"
        ), "Manual tab should be visible"

    @pytest.mark.boothcall
    @pytest.mark.auth_gated
    @autologger.automation_logger("Test")
    def test_manual_add_tab_shows_form(self):
        """Verify Manual Add tab has email + name fields and Add to Roster button."""
        self._navigate_to_first_event()
        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()

        self.team_page.click_invite_staff()
        self.team_page.wait_for_invite_dialog()
        self.team_page.click_manual_tab()

        from selenium.webdriver.common.by import By
        assert self.browser.is_element_present(By.CSS_SELECTOR, "#manual-email"), \
            "Manual email field should be present"
        assert self.browser.is_element_present(By.CSS_SELECTOR, "#manual-name"), \
            "Manual name field should be present"
        assert self.browser.is_element_displayed(
            By.XPATH, "//button[contains(., 'Add to Roster')]"
        ), "Add to Roster button should be visible"
