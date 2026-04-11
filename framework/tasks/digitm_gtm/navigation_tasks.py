"""
NavigationTasks - Task module for Digitm GTM navigation workflows.

Phase A: Single user, no auth required. Navigate directly to pages.
"""

from interfaces.browser_interface import BrowserInterface
from pages.digitm_gtm.landing_page import LandingPage
from pages.digitm_gtm.dashboard_page import DashboardPage
from resources.utilities import autologger


class NavigationTasks:

    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.landing_page = LandingPage(browser)
        self.dashboard_page = DashboardPage(browser)

    @autologger.automation_logger("Task")
    def open_landing_page(self, base_url: str) -> None:
        (self.landing_page
            .navigate(base_url)
            .wait_for_page_loaded())

    @autologger.automation_logger("Task")
    def open_dashboard(self, base_url: str) -> None:
        """Navigate directly to dashboard. Phase A: no auth required."""
        (self.dashboard_page
            .navigate(base_url)
            .wait_for_page_loaded())

    @autologger.automation_logger("Task")
    def navigate_to_products_from_sidebar(self) -> None:
        self.dashboard_page.click_nav_products()
