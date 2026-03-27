"""
IngredientsManifestTasks - Task module

Orchestrates ingredients manifest operations for the COGS Calculator.
"""

from interfaces.browser_interface import BrowserInterface
from pages.cogs_calculator.ingredients_manifest_page import IngredientsManifestPage
from resources.utilities import autologger


class IngredientsManifestTasks:
    """
    Task module for Ingredients Manifest.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.manifest_page = IngredientsManifestPage(browser)

    @autologger.automation_logger("Task")
    def export_ingredients(self) -> None:
        """Click the export button on the ingredients manifest."""
        self.manifest_page.click_export()
