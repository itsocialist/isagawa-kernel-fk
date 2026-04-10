"""
NavigationTasks - Task module

Orchestrates page objects for BoothCall navigation workflows.
Handles landing page access, login page navigation, and authenticated routing.
"""

from interfaces.browser_interface import BrowserInterface
from pages.boothcall.landing_page import LandingPage
from pages.boothcall.login_page import LoginPage
from pages.boothcall.event_dashboard_page import EventDashboardPage
from resources.utilities import autologger


class NavigationTasks:
    """
    Task module for BoothCall navigation workflow.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        """
        Compose Page Objects — NO decorator on constructor.

        Args:
            browser: BrowserInterface instance
        """
        self.browser = browser
        self.landing_page = LandingPage(browser)
        self.login_page = LoginPage(browser)
        self.event_dashboard_page = EventDashboardPage(browser)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def open_landing_page(self, base_url: str) -> None:
        """
        Navigate to the BoothCall landing page and wait for it to load.

        Args:
            base_url: Base URL of the BoothCall application
        """
        (self.landing_page
            .navigate(base_url)
            .wait_for_page_loaded())

    @autologger.automation_logger("Task")
    def navigate_to_login_from_landing(self) -> None:
        """
        Click the Sign In button on the landing page to reach the login page.
        """
        self.landing_page.click_sign_in()
        self.login_page.wait_for_page_loaded()

    @autologger.automation_logger("Task")
    def open_login_page_directly(self, base_url: str) -> None:
        """
        Navigate directly to the login page URL.

        Args:
            base_url: Base URL of the BoothCall application
        """
        (self.login_page
            .navigate(base_url + "/login")
            .wait_for_page_loaded())
