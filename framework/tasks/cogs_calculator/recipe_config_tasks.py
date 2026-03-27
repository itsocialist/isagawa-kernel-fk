"""
RecipeConfigTasks - Task module

Orchestrates recipe configuration operations for the COGS Calculator.
"""

from interfaces.browser_interface import BrowserInterface
from pages.cogs_calculator.recipe_config_page import RecipeConfigPage
from pages.cogs_calculator.kpi_dashboard_page import KpiDashboardPage
from resources.utilities import autologger


class RecipeConfigTasks:
    """
    Task module for Recipe Configuration.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.recipe_page = RecipeConfigPage(browser)
        self.kpi_page = KpiDashboardPage(browser)

    @autologger.automation_logger("Task")
    def update_product_name(self, name: str) -> None:
        """Update the product name field."""
        self.recipe_page.set_product_name(name)

    @autologger.automation_logger("Task")
    def update_batch_volume(self, volume: str) -> None:
        """Update the batch volume field."""
        self.recipe_page.set_batch_volume(volume)

    @autologger.automation_logger("Task")
    def update_labor_rate(self, rate: str) -> None:
        """Update the labor rate field."""
        self.recipe_page.set_labor_rate(rate)

    @autologger.automation_logger("Task")
    def update_labor_hours(self, hours: str) -> None:
        """Update the labor hours field."""
        self.recipe_page.set_labor_hours(hours)

    @autologger.automation_logger("Task")
    def update_fulfillment_cost(self, cost: str) -> None:
        """Update the fulfillment cost field."""
        self.recipe_page.set_fulfillment(cost)
