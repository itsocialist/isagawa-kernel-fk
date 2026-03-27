"""
CogsCalculatorAuthTasks - Task module

Orchestrates passphrase authentication for the ROLOS KITCHEN COGS Calculator.
"""

from interfaces.browser_interface import BrowserInterface
from pages.cogs_calculator.passphrase_page import PassphrasePage
from pages.cogs_calculator.calculator_page import CalculatorPage
from resources.utilities import autologger


class CogsCalculatorAuthTasks:
    """
    Task module for COGS Calculator authentication.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.passphrase_page = PassphrasePage(browser)
        self.calculator_page = CalculatorPage(browser)

    @autologger.automation_logger("Task")
    def navigate_to_app(self, url: str) -> None:
        """Navigate to the app URL."""
        self.passphrase_page.navigate(url)

    @autologger.automation_logger("Task")
    def enter_passphrase_and_submit(self, passphrase: str) -> None:
        """Enter passphrase and submit the gate form."""
        (self.passphrase_page
            .wait_for_passphrase_gate()
            .enter_passphrase(passphrase)
            .click_submit())

    @autologger.automation_logger("Task")
    def wait_for_app_after_auth(self) -> None:
        """Wait for the main app to load after successful authentication."""
        self.calculator_page.wait_for_app_loaded()
