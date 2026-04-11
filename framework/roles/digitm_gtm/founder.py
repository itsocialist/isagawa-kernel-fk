"""
Founder - Role class for Digitm GTM.

Represents a solo founder using the GTM pipeline.
Phase A: Single user, no auth required.
"""

from interfaces.browser_interface import BrowserInterface
from tasks.digitm_gtm.navigation_tasks import NavigationTasks
from tasks.digitm_gtm.product_tasks import ProductTasks
from resources.utilities import autologger


class Founder:

    def __init__(self, browser: BrowserInterface, base_url: str):
        self.browser = browser
        self.base_url = base_url
        self.navigation = NavigationTasks(browser)
        self.product = ProductTasks(browser)

    @autologger.automation_logger("Role")
    def visit_landing_page(self) -> None:
        self.navigation.open_landing_page(self.base_url)

    @autologger.automation_logger("Role")
    def visit_dashboard(self) -> None:
        self.navigation.open_dashboard(self.base_url)

    @autologger.automation_logger("Role")
    def visit_landing_and_go_to_dashboard(self) -> None:
        self.navigation.open_landing_page(self.base_url)
        # In Phase A, skip login — navigate directly
        self.navigation.open_dashboard(self.base_url)

    @autologger.automation_logger("Role")
    def create_product(self, name: str, description: str, audience: str) -> None:
        self.product.create_product(self.base_url, name, description, audience)

    @autologger.automation_logger("Role")
    def trigger_pipeline_run(self) -> None:
        self.product.trigger_pipeline()
