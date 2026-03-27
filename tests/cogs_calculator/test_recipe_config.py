"""
TestRecipeConfig - Recipe configuration tests for ROLOS KITCHEN COGS Calculator.

Tests recipe configuration inputs and their impact on KPI calculations.
Uses AAA pattern: Arrange, Act, Assert.

Run dev:  pytest tests/cogs_calculator/test_recipe_config.py --env=cogs_calculator_dev -v
Run prod: pytest tests/cogs_calculator/test_recipe_config.py --env=cogs_calculator_prod -v
"""

import time
import pytest
from resources.utilities import autologger
from roles.cogs_calculator.formulator_role import FormulatorRole
from pages.cogs_calculator.recipe_config_page import RecipeConfigPage
from pages.cogs_calculator.kpi_dashboard_page import KpiDashboardPage
from pages.cogs_calculator.ingredients_manifest_page import IngredientsManifestPage
from pages.cogs_calculator.passphrase_page import PassphrasePage


class TestRecipeConfig:
    """
    Recipe configuration tests.

    Validates:
    - Product name can be edited and reflects in the input
    - Batch volume changes update ingredients totals
    - Labor rate/hours changes update Unit Cost KPI
    - Fulfillment cost changes update distribution cost in Unit Cost KPI
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser and config into test class. Reset auth state before each test."""
        self.browser = browser
        self.config = config
        self.recipe_page = RecipeConfigPage(self.browser)
        self.kpi_page = KpiDashboardPage(self.browser)
        self.manifest_page = IngredientsManifestPage(self.browser)
        self.passphrase_page = PassphrasePage(self.browser)
        # Clear stored auth state so each test starts fresh
        browser.navigate_to(config["url"])
        browser.execute_script("localStorage.clear(); sessionStorage.clear();")
        browser.driver.delete_all_cookies()

    def _authenticate(self):
        """Helper to authenticate before each test."""
        formulator = FormulatorRole(
            browser=self.browser,
            url=self.config["url"],
            passphrase="black50"
        )
        formulator.authenticate()

    @autologger.automation_logger("Test")
    def test_edit_product_name(self):
        """
        Verify the product name can be edited and the new value is reflected.

        AAA:
        - Arrange: Authenticate and note default product name
        - Act: Change product name to a new value
        - Assert: Input reflects the new product name
        """
        # Arrange
        self._authenticate()
        original_name = self.recipe_page.get_product_name()

        # Act
        self.recipe_page.set_product_name("Lavender Relief Balm")
        time.sleep(0.5)

        # Assert
        new_name = self.recipe_page.get_product_name()
        assert new_name == "Lavender Relief Balm", \
            f"Product name should be 'Lavender Relief Balm', got '{new_name}'"
        assert new_name != original_name, \
            "Product name should have changed from the original"

    @autologger.automation_logger("Test")
    def test_batch_volume_change_updates_kpis(self):
        """
        Verify that changing batch volume recalculates ingredient totals.

        AAA:
        - Arrange: Authenticate and capture initial ingredients totals
        - Act: Double the batch volume
        - Assert: Ingredients total weight and cost scale accordingly
        """
        # Arrange
        self._authenticate()
        initial_totals = self.manifest_page.get_totals_row()
        initial_weight = float(initial_totals["total_weight"].replace(",", "").replace("g", ""))
        initial_cost = float(initial_totals["cost"].replace("$", "").replace(",", ""))

        # Act
        self.recipe_page.set_batch_volume("20")
        time.sleep(1)

        # Assert
        updated_totals = self.manifest_page.get_totals_row()
        updated_weight = float(updated_totals["total_weight"].replace(",", "").replace("g", ""))
        updated_cost = float(updated_totals["cost"].replace("$", "").replace(",", ""))

        assert updated_weight > initial_weight, \
            f"Total weight should increase when batch volume doubles. Before: {initial_weight}g, After: {updated_weight}g"
        assert updated_cost > initial_cost, \
            f"Total cost should increase when batch volume doubles. Before: ${initial_cost}, After: ${updated_cost}"

    @autologger.automation_logger("Test")
    def test_labor_rate_change_updates_unit_cost(self):
        """
        Verify that changing labor rate updates the Unit Cost KPI.

        AAA:
        - Arrange: Authenticate and capture initial Unit Cost
        - Act: Increase labor rate
        - Assert: Unit Cost increases (higher labor = higher cost)
        """
        # Arrange
        self._authenticate()
        initial_cost = self.kpi_page.get_unit_cost_value()

        # Act
        self.recipe_page.set_labor_rate("50")
        time.sleep(1)

        # Assert
        updated_cost = self.kpi_page.get_unit_cost_value()
        assert updated_cost != initial_cost, \
            f"Unit Cost should change when labor rate changes. Before: '{initial_cost}', After: '{updated_cost}'"

    @autologger.automation_logger("Test")
    def test_labor_hours_change_updates_unit_cost(self):
        """
        Verify that changing labor hours updates the Unit Cost KPI.

        AAA:
        - Arrange: Authenticate and capture initial Unit Cost
        - Act: Increase labor hours
        - Assert: Unit Cost increases (more hours = higher cost)
        """
        # Arrange
        self._authenticate()
        initial_cost = self.kpi_page.get_unit_cost_value()

        # Act
        self.recipe_page.set_labor_hours("12")
        time.sleep(1)

        # Assert
        updated_cost = self.kpi_page.get_unit_cost_value()
        assert updated_cost != initial_cost, \
            f"Unit Cost should change when labor hours change. Before: '{initial_cost}', After: '{updated_cost}'"

    @autologger.automation_logger("Test")
    def test_fulfillment_cost_updates_distribution(self):
        """
        Verify that changing fulfillment cost updates the distribution portion of Unit Cost.

        AAA:
        - Arrange: Authenticate and capture initial Unit Cost breakdown
        - Act: Change fulfillment cost
        - Assert: Distribution cost in Unit Cost breakdown changes
        """
        # Arrange
        self._authenticate()
        initial_breakdown = self.kpi_page.get_unit_cost_breakdown()

        # Act
        self.recipe_page.set_fulfillment("5")
        time.sleep(1)

        # Assert
        updated_breakdown = self.kpi_page.get_unit_cost_breakdown()
        assert updated_breakdown != initial_breakdown, \
            f"Unit Cost breakdown should change when fulfillment changes. Before: '{initial_breakdown}', After: '{updated_breakdown}'"
