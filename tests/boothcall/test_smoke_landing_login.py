"""
TestBoothCallSmoke - Smoke test for BoothCall Landing & Login.

End-to-end smoke test that validates:
1. Landing page loads correctly with hero content and branding
2. Navigation from landing page to login page works
3. Login page renders with Google OAuth and magic link options

Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.boothcall.event_organizer import EventOrganizer
from pages.boothcall.landing_page import LandingPage
from pages.boothcall.login_page import LoginPage


class TestBoothCallSmoke:
    """
    Smoke test - BoothCall landing and login page validation.

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

    # ==================== HELPERS ====================

    def _skip_if_authenticated(self):
        """Skip when authenticated — landing/login redirect to /events."""
        self.browser.navigate_to(self.config["url"])
        import time
        time.sleep(1)
        if "/events" in self.browser.get_current_url():
            pytest.skip("Authenticated session active — public pages redirect")

    # ==================== TEST METHODS ====================

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_page_loads(self):
        """
        Smoke test: Verify the BoothCall landing page renders correctly.

        AAA Pattern:
        1. Arrange - Create EventOrganizer role with base URL
        2. Act - Visit the landing page
        3. Assert - Verify hero section and logo are displayed
        """
        self._skip_if_authenticated()

        # Arrange
        base_url = self.config["url"]
        organizer = EventOrganizer(self.browser, base_url)

        # Act
        organizer.visit_landing_page()

        # Assert
        assert self.landing_page.is_hero_displayed(), \
            "Hero heading should be visible on the landing page"

        assert self.landing_page.is_logo_displayed(), \
            "BoothCall logo text should be visible"

    @pytest.mark.boothcall
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_to_login_navigation(self):
        """
        Smoke test: Verify navigation from landing page to login page.

        AAA Pattern:
        1. Arrange - Create EventOrganizer role with base URL
        2. Act - Visit landing page, then navigate to login
        3. Assert - Verify login page is displayed with Google OAuth button
        """
        self._skip_if_authenticated()

        # Arrange
        base_url = self.config["url"]
        organizer = EventOrganizer(self.browser, base_url)

        # Act
        organizer.visit_landing_and_navigate_to_login()

        # Assert
        assert self.login_page.is_login_page_displayed(), \
            "Login page heading should be visible after clicking Sign In"

        assert self.login_page.is_google_button_displayed(), \
            "Google OAuth button should be visible on the login page"

        assert self.login_page.is_on_login_page(), \
            "URL should contain /login after navigation"
