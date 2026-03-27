"""
IngredientsManifestPage - Page Object Model

Page Object for the ROLOS KITCHEN COGS Calculator ingredients manifest table.
Handles reading ingredient rows, totals, and export functionality.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class IngredientsManifestPage:
    """
    Page Object for the Ingredients Manifest table.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, browser: BrowserInterface):
        """Compose BrowserInterface — NO inheritance."""
        self.browser = browser

    # ==================== LOCATORS (Class Constants) ====================

    INGREDIENTS_TABLE = (By.XPATH, "//table")
    HEADER_ROW = (By.XPATH, "//table//thead//tr")
    INGREDIENT_ROWS = (By.XPATH, "//table//tbody//tr[not(.//td[contains(text(),'TOTAL')])]")
    TOTALS_ROW = (By.XPATH, "//tr[.//td[contains(text(),'TOTAL')]]")
    EXPORT_BUTTON = (By.XPATH, "//button[contains(text(),'Export')]")
    MANIFEST_HEADER = (By.XPATH, "//*[contains(text(),'Ingredients Manifest') or contains(text(),'INGREDIENTS MANIFEST')]")

    # ==================== ATOMIC METHODS ====================

    def click_export(self) -> "IngredientsManifestPage":
        """Click the Export button in the ingredients manifest section."""
        self.browser.click(*self.EXPORT_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def get_ingredient_count(self) -> int:
        """Get the number of ingredient rows (excluding totals)."""
        elements = self.browser.find_elements(*self.INGREDIENT_ROWS)
        return len(elements)

    def get_ingredient_names(self) -> list:
        """Get list of ingredient names from the table."""
        rows = self.browser.find_elements(*self.INGREDIENT_ROWS)
        names = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                names.append(cells[0].text)
        return names

    def get_ingredient_types(self) -> list:
        """Get list of ingredient types from the table."""
        rows = self.browser.find_elements(*self.INGREDIENT_ROWS)
        types = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) > 1:
                types.append(cells[1].text)
        return types

    def get_ingredient_row_data(self, ingredient_name: str) -> dict:
        """Get all data for a specific ingredient row."""
        rows = self.browser.find_elements(*self.INGREDIENT_ROWS)
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells and ingredient_name in cells[0].text:
                return {
                    "name": cells[0].text,
                    "type": cells[1].text if len(cells) > 1 else "",
                    "per_unit": cells[2].text if len(cells) > 2 else "",
                    "cost_per_unit": cells[3].text if len(cells) > 3 else "",
                    "total_weight": cells[4].text if len(cells) > 4 else "",
                    "total_volume": cells[5].text if len(cells) > 5 else "",
                    "cost": cells[6].text if len(cells) > 6 else "",
                }
        return {}

    def get_totals_row(self) -> dict:
        """Get the totals row data."""
        row = self.browser.find_element(*self.TOTALS_ROW)
        cells = row.find_elements(By.TAG_NAME, "td")
        return {
            "label": cells[0].text if len(cells) > 0 else "",
            "type": cells[1].text if len(cells) > 1 else "",
            "per_unit": cells[2].text if len(cells) > 2 else "",
            "cost_per_unit": cells[3].text if len(cells) > 3 else "",
            "total_weight": cells[4].text if len(cells) > 4 else "",
            "total_volume": cells[5].text if len(cells) > 5 else "",
            "cost": cells[6].text if len(cells) > 6 else "",
        }

    def is_table_displayed(self) -> bool:
        """Check if the ingredients table is displayed."""
        return self.browser.is_element_displayed(*self.INGREDIENTS_TABLE)

    def is_export_button_displayed(self) -> bool:
        """Check if the Export button is displayed."""
        return self.browser.is_element_displayed(*self.EXPORT_BUTTON)

    def get_column_headers(self) -> list:
        """Get the column header texts."""
        row = self.browser.find_element(*self.HEADER_ROW)
        cells = row.find_elements(By.TAG_NAME, "th")
        return [c.text for c in cells]
