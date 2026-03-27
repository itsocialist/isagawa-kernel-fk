"""
FormulatorRole - Role module

Represents a formulator who authenticates and uses the COGS Calculator.
"""

from interfaces.browser_interface import BrowserInterface
from resources.utilities import autologger
from tasks.cogs_calculator.auth_tasks import CogsCalculatorAuthTasks
from tasks.cogs_calculator.recipe_config_tasks import RecipeConfigTasks
from tasks.cogs_calculator.ingredients_manifest_tasks import IngredientsManifestTasks
from pages.cogs_calculator.passphrase_page import PassphrasePage
from pages.cogs_calculator.calculator_page import CalculatorPage


class FormulatorRole:
    """
    Formulator role — authenticates and accesses the COGS Calculator.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - NO return values
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, browser: BrowserInterface, url: str, passphrase: str):
        self.browser = browser
        self.url = url
        self.passphrase = passphrase
        self.auth_tasks = CogsCalculatorAuthTasks(browser)
        self.recipe_tasks = RecipeConfigTasks(browser)
        self.manifest_tasks = IngredientsManifestTasks(browser)
        self.passphrase_page = PassphrasePage(browser)
        self.calculator_page = CalculatorPage(browser)

    @autologger.automation_logger("Role")
    def authenticate(self) -> None:
        """Navigate to app and authenticate with passphrase."""
        self.auth_tasks.navigate_to_app(self.url)
        self.auth_tasks.enter_passphrase_and_submit(self.passphrase)
        self.auth_tasks.wait_for_app_after_auth()

    @autologger.automation_logger("Role")
    def attempt_wrong_passphrase(self, wrong_passphrase: str) -> None:
        """Navigate to app and submit an incorrect passphrase."""
        self.auth_tasks.navigate_to_app(self.url)
        (self.passphrase_page
            .wait_for_passphrase_gate()
            .enter_passphrase(wrong_passphrase)
            .click_submit())

    @autologger.automation_logger("Role")
    def authenticate_and_update_recipe(self, **kwargs) -> None:
        """Authenticate and update recipe configuration fields."""
        self.authenticate()
        if "product_name" in kwargs:
            self.recipe_tasks.update_product_name(kwargs["product_name"])
        if "batch_volume" in kwargs:
            self.recipe_tasks.update_batch_volume(kwargs["batch_volume"])
        if "labor_rate" in kwargs:
            self.recipe_tasks.update_labor_rate(kwargs["labor_rate"])
        if "labor_hours" in kwargs:
            self.recipe_tasks.update_labor_hours(kwargs["labor_hours"])
        if "fulfillment" in kwargs:
            self.recipe_tasks.update_fulfillment_cost(kwargs["fulfillment"])

    @autologger.automation_logger("Role")
    def authenticate_and_export_ingredients(self) -> None:
        """Authenticate and export the ingredients manifest."""
        self.authenticate()
        self.manifest_tasks.export_ingredients()
