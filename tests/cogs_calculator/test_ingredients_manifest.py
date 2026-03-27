"""
TestIngredientsManifest - Ingredients manifest tests for ROLOS KITCHEN COGS Calculator.

Tests the ingredients table rendering, types, totals, and export functionality.
Uses AAA pattern: Arrange, Act, Assert.

Run dev:  pytest tests/cogs_calculator/test_ingredients_manifest.py --env=cogs_calculator_dev -v
Run prod: pytest tests/cogs_calculator/test_ingredients_manifest.py --env=cogs_calculator_prod -v
"""

import pytest
from resources.utilities import autologger
from roles.cogs_calculator.formulator_role import FormulatorRole
from pages.cogs_calculator.ingredients_manifest_page import IngredientsManifestPage
from pages.cogs_calculator.passphrase_page import PassphrasePage


EXPECTED_INGREDIENTS = [
    {"name": "CBD Isolate", "type": "ACTIVE"},
    {"name": "CBG Distillate", "type": "ACTIVE"},
    {"name": "Organic Shea Butter", "type": "BASE"},
    {"name": "Beeswax Pellets", "type": "BASE"},
    {"name": "MCT Oil", "type": "CARRIER"},
    {"name": "Menthol Crystals", "type": "TERPENE"},
    {"name": "Lavender Essential Oil", "type": "TERPENE"},
]


class TestIngredientsManifest:
    """
    Ingredients manifest tests.

    Validates:
    - All 7 ingredients render with correct names
    - Each ingredient has the correct type (ACTIVE, BASE, CARRIER, TERPENE)
    - Totals row calculates correctly (weight, volume, cost)
    - Export button is present and clickable
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser and config into test class. Reset auth state before each test."""
        self.browser = browser
        self.config = config
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
    def test_all_ingredients_render(self):
        """
        Verify all 7 ingredients are displayed in the manifest table.

        AAA:
        - Arrange: Authenticate to access the calculator
        - Act: Read ingredient names from the table
        - Assert: All 7 expected ingredients are present
        """
        # Arrange
        self._authenticate()

        # Act
        names = self.manifest_page.get_ingredient_names()

        # Assert
        assert len(names) == 7, \
            f"Expected 7 ingredients, got {len(names)}: {names}"
        for expected in EXPECTED_INGREDIENTS:
            assert expected["name"] in names, \
                f"Ingredient '{expected['name']}' should be in the manifest table"

    @autologger.automation_logger("Test")
    def test_ingredient_types_are_correct(self):
        """
        Verify each ingredient has the correct type classification.

        AAA:
        - Arrange: Authenticate to access the calculator
        - Act: Read ingredient data from the table
        - Assert: Each ingredient has the expected type (ACTIVE, BASE, CARRIER, TERPENE)
        """
        # Arrange
        self._authenticate()

        # Act & Assert
        for expected in EXPECTED_INGREDIENTS:
            row_data = self.manifest_page.get_ingredient_row_data(expected["name"])
            assert row_data, \
                f"Ingredient '{expected['name']}' should exist in the table"
            assert row_data["type"] == expected["type"], \
                f"Ingredient '{expected['name']}' should be type '{expected['type']}', got '{row_data['type']}'"

    @autologger.automation_logger("Test")
    def test_totals_row_has_values(self):
        """
        Verify the totals row displays calculated weight, volume, and cost.

        AAA:
        - Arrange: Authenticate to access the calculator
        - Act: Read the totals row
        - Assert: Weight, volume, and cost are non-empty and contain expected units
        """
        # Arrange
        self._authenticate()

        # Act
        totals = self.manifest_page.get_totals_row()

        # Assert
        assert totals["label"] == "TOTAL", \
            f"Totals row label should be 'TOTAL', got '{totals['label']}'"
        assert "g" in totals["total_weight"], \
            f"Total weight should contain 'g', got '{totals['total_weight']}'"
        assert "ml" in totals["total_volume"], \
            f"Total volume should contain 'ml', got '{totals['total_volume']}'"
        assert "$" in totals["cost"], \
            f"Total cost should contain '$', got '{totals['cost']}'"
        assert totals["per_unit"] != "", \
            "Total per-unit weight should not be empty"

    @autologger.automation_logger("Test")
    def test_totals_weight_is_sum_of_ingredients(self):
        """
        Verify the totals row weight is the sum of individual ingredient weights.

        AAA:
        - Arrange: Authenticate and read all ingredient weights
        - Act: Sum individual weights and compare to totals row
        - Assert: Totals weight matches sum of ingredient weights (within rounding)
        """
        # Arrange
        self._authenticate()

        # Act
        total_weight = 0.0
        for expected in EXPECTED_INGREDIENTS:
            row = self.manifest_page.get_ingredient_row_data(expected["name"])
            weight_str = row["total_weight"].replace(",", "").replace("g", "")
            total_weight += float(weight_str)

        totals = self.manifest_page.get_totals_row()
        totals_weight = float(totals["total_weight"].replace(",", "").replace("g", ""))

        # Assert — allow 0.01g tolerance for floating point
        assert abs(totals_weight - total_weight) < 0.01, \
            f"Totals weight ({totals_weight}g) should equal sum of ingredients ({total_weight:.3f}g)"

    @autologger.automation_logger("Test")
    def test_totals_cost_is_sum_of_ingredients(self):
        """
        Verify the totals row cost is the sum of individual ingredient costs.

        AAA:
        - Arrange: Authenticate and read all ingredient costs
        - Act: Sum individual costs and compare to totals row
        - Assert: Totals cost matches sum of ingredient costs (within rounding)
        """
        # Arrange
        self._authenticate()

        # Act
        total_cost = 0.0
        for expected in EXPECTED_INGREDIENTS:
            row = self.manifest_page.get_ingredient_row_data(expected["name"])
            cost_str = row["cost"].replace("$", "").replace(",", "")
            total_cost += float(cost_str)

        totals = self.manifest_page.get_totals_row()
        totals_cost = float(totals["cost"].replace("$", "").replace(",", ""))

        # Assert — allow $0.02 tolerance for rounding
        assert abs(totals_cost - total_cost) < 0.02, \
            f"Totals cost (${totals_cost}) should equal sum of ingredients (${total_cost:.2f})"

    @autologger.automation_logger("Test")
    def test_export_button_is_displayed(self):
        """
        Verify the Export button is visible in the ingredients manifest section.

        AAA:
        - Arrange: Authenticate to access the calculator
        - Act: Check for Export button
        - Assert: Export button is visible and clickable
        """
        # Arrange
        self._authenticate()

        # Assert
        assert self.manifest_page.is_export_button_displayed(), \
            "Export button should be visible in the ingredients manifest section"
