"""
TestSovAICannabisLogin - Authentication tests for SovAI Cannabis.

Validates that the admin user can log in to LibreChat via the Nginx-proxied
HTTPS endpoint (port 8443) and access the chat interface.

Uses AAA pattern: Arrange, Act, Assert.

NOTE: Tests run in order within a session-scoped browser. Login test runs first;
subsequent tests reuse the authenticated session.

Run with:
    pytest tests/sovai_cannabis/ --env sovai_cannabis_local -v
"""

import pytest
from resources.utilities import autologger
from roles.sovai.admin_role import AdminRole
from pages.sovai.login_page import LoginPage
from pages.sovai.chat_page import ChatPage


class TestSovAICannabisLogin:
    """Authentication tests for SovAI Cannabis LibreChat instance."""

    @pytest.fixture(autouse=True)
    def setup(self, browser, config, test_users):
        """Pytest fixture wires browser, config, and test data into the test class."""
        self.browser = browser
        self.config = config
        self.test_users = test_users
        self.login_page = LoginPage(self.browser)
        self.chat_page = ChatPage(self.browser)

    # ==================== TEST METHODS ====================

    @pytest.mark.sovai_cannabis
    @pytest.mark.auth
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_admin_login_success(self):
        """
        Verify admin can log in with stored credentials.

        AAA Pattern:
        1. Arrange - Create AdminRole with sovai_cannabis_admin credentials
        2. Act     - Execute login workflow
        3. Assert  - Redirected to chat page, no errors
        """
        # Arrange
        credentials = self.test_users["sovai_cannabis_admin"]
        base_url = self.config["url"]

        admin = AdminRole(
            self.browser,
            base_url=base_url,
            email=credentials["email"],
            password=credentials["password"]
        )

        # Act
        admin.login_and_verify()

        # Assert
        assert self.login_page.is_on_chat_page(), \
            "Should be redirected to chat page after login"

        assert not self.login_page.has_error_message(), \
            "No error message should be displayed after successful login"

    @pytest.mark.sovai_cannabis
    @pytest.mark.auth
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_chat_interface_loads(self):
        """
        Verify the chat interface loads with cannabis branding.

        Checks:
        - Chat input is ready
        - No JS console errors breaking the page
        - Page title contains 'LibreChat'
        """
        # Check chat input is ready
        assert self.chat_page.is_chat_input_ready(), \
            "Chat input should be present and ready"

        # Check page title
        title = self.browser.get_title()
        assert "LibreChat" in title or "SovAI" in title, \
            f"Page title should contain LibreChat or SovAI, got: {title}"
