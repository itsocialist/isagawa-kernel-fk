"""
TestPassphraseAuth - Passphrase gate authentication tests for ROLOS KITCHEN COGS Calculator.

Tests both dev (localhost:5200) and prod (cogs-calculator.vercel.app) environments.
Uses AAA pattern: Arrange, Act, Assert.

Run dev:  pytest tests/cogs_calculator/test_passphrase_auth.py --env=cogs_calculator_dev -v
Run prod: pytest tests/cogs_calculator/test_passphrase_auth.py --env=cogs_calculator_prod -v
"""

import pytest
from resources.utilities import autologger
from roles.cogs_calculator.formulator_role import FormulatorRole
from pages.cogs_calculator.passphrase_page import PassphrasePage
from pages.cogs_calculator.calculator_page import CalculatorPage


class TestPassphraseAuth:
    """
    Passphrase gate authentication tests.

    Validates:
    - Passphrase gate is shown on load
    - Correct passphrase grants access to the app
    - Incorrect passphrase shows error and blocks access
    - Brand header is visible on the gate screen
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser and config into test class. Reset auth state before each test."""
        self.browser = browser
        self.config = config
        self.passphrase_page = PassphrasePage(self.browser)
        self.calculator_page = CalculatorPage(self.browser)
        # Navigate to app first so storage is accessible, then clear auth state
        browser.navigate_to(config["url"])
        browser.execute_script("localStorage.clear(); sessionStorage.clear();")
        browser.driver.delete_all_cookies()

    @autologger.automation_logger("Test")
    def test_passphrase_gate_is_displayed_on_load(self):
        """
        Verify the passphrase gate screen is shown when navigating to the app.

        AAA:
        - Arrange: Create formulator role with app URL
        - Act: Navigate to app URL only (no auth)
        - Assert: Passphrase input and brand header are visible
        """
        # Arrange
        url = self.config["url"]

        # Act
        self.passphrase_page.navigate(url)
        self.passphrase_page.wait_for_passphrase_gate()

        # Assert
        assert self.passphrase_page.is_passphrase_gate_displayed(), \
            "Passphrase input should be visible on initial load"
        assert self.passphrase_page.is_brand_header_displayed(), \
            "ROLOS KITCHEN brand header should be visible on the gate screen"

    @autologger.automation_logger("Test")
    def test_correct_passphrase_grants_access(self):
        """
        Verify that the correct passphrase grants access to the main app.

        AAA:
        - Arrange: Create formulator role with correct passphrase
        - Act: Authenticate with correct passphrase
        - Assert: Main app is loaded, passphrase gate is gone
        """
        # Arrange
        formulator = FormulatorRole(
            browser=self.browser,
            url=self.config["url"],
            passphrase="black50"
        )

        # Act
        formulator.authenticate()

        # Assert
        assert self.calculator_page.is_app_loaded(), \
            "Main calculator app should be loaded after correct passphrase"
        assert self.passphrase_page.is_app_accessible(), \
            "Passphrase gate should no longer be visible after authentication"

    @autologger.automation_logger("Test")
    def test_incorrect_passphrase_shows_error(self):
        """
        Verify that an incorrect passphrase shows an error and blocks access.

        AAA:
        - Arrange: Create formulator role with wrong passphrase
        - Act: Submit wrong passphrase
        - Assert: Error message shown, app not accessible
        """
        # Arrange
        formulator = FormulatorRole(
            browser=self.browser,
            url=self.config["url"],
            passphrase="wrongpassword"
        )

        # Act
        formulator.attempt_wrong_passphrase("wrongpassword")
        self.passphrase_page.wait_for_error()

        # Assert
        assert self.passphrase_page.is_error_displayed(), \
            "Error message should be displayed after incorrect passphrase"
        assert not self.calculator_page.is_app_loaded(), \
            "Main app should NOT be accessible after incorrect passphrase"

    @autologger.automation_logger("Test")
    def test_app_has_actions_dropdown_after_auth(self):
        """
        Verify the Actions dropdown is present after authentication.

        AAA:
        - Arrange: Authenticate with correct passphrase
        - Act: Check for Actions button
        - Assert: Actions button is visible in the app
        """
        # Arrange
        formulator = FormulatorRole(
            browser=self.browser,
            url=self.config["url"],
            passphrase="black50"
        )

        # Act
        formulator.authenticate()

        # Assert
        assert self.calculator_page.is_actions_button_displayed(), \
            "Actions dropdown button should be visible in the main app"
