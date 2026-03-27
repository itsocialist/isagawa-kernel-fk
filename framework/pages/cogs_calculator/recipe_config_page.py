"""
RecipeConfigPage - Page Object Model

Page Object for the ROLOS KITCHEN COGS Calculator recipe configuration section.
Handles product name, batch volume, labor rate, labor hours, and fulfillment inputs.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class RecipeConfigPage:
    """
    Page Object for the Recipe Configuration section.

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

    PRODUCT_NAME_INPUT = (By.XPATH, "//label[contains(text(),'Product Name')]/..//input")
    BATCH_VOLUME_INPUT = (By.XPATH, "//label[contains(text(),'Batch Volume')]/..//input")
    LABOR_RATE_INPUT = (By.XPATH, "//label[contains(text(),'Labor Rate')]/..//input")
    LABOR_HOURS_INPUT = (By.XPATH, "//label[contains(text(),'Labor Hours')]/..//input")
    FULFILLMENT_INPUT = (By.XPATH, "//label[contains(text(),'Fulfillment')]/..//input")

    # ==================== ATOMIC METHODS ====================

    def _set_input_value(self, by, value, text: str) -> None:
        """Clear and set input value using JS focus/select for React compatibility."""
        element = self.browser.find_element(by, value)
        self.browser.scroll_to_element(by, value)
        self.browser.execute_script(
            "arguments[0].focus(); arguments[0].select();", element
        )
        element.send_keys(text)

    def set_product_name(self, name: str) -> "RecipeConfigPage":
        """Set the product name."""
        self._set_input_value(*self.PRODUCT_NAME_INPUT, name)
        return self

    def set_batch_volume(self, volume: str) -> "RecipeConfigPage":
        """Set the batch volume."""
        self._set_input_value(*self.BATCH_VOLUME_INPUT, volume)
        return self

    def set_labor_rate(self, rate: str) -> "RecipeConfigPage":
        """Set the labor rate."""
        self._set_input_value(*self.LABOR_RATE_INPUT, rate)
        return self

    def set_labor_hours(self, hours: str) -> "RecipeConfigPage":
        """Set the labor hours."""
        self._set_input_value(*self.LABOR_HOURS_INPUT, hours)
        return self

    def set_fulfillment(self, cost: str) -> "RecipeConfigPage":
        """Set the fulfillment cost."""
        self._set_input_value(*self.FULFILLMENT_INPUT, cost)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def get_product_name(self) -> str:
        """Get the current product name value."""
        return self.browser.get_attribute(*self.PRODUCT_NAME_INPUT, "value")

    def get_batch_volume(self) -> str:
        """Get the current batch volume value."""
        return self.browser.get_attribute(*self.BATCH_VOLUME_INPUT, "value")

    def get_labor_rate(self) -> str:
        """Get the current labor rate value."""
        return self.browser.get_attribute(*self.LABOR_RATE_INPUT, "value")

    def get_labor_hours(self) -> str:
        """Get the current labor hours value."""
        return self.browser.get_attribute(*self.LABOR_HOURS_INPUT, "value")

    def get_fulfillment(self) -> str:
        """Get the current fulfillment cost value."""
        return self.browser.get_attribute(*self.FULFILLMENT_INPUT, "value")

    def is_product_name_displayed(self) -> bool:
        """Check if product name input is displayed."""
        return self.browser.is_element_displayed(*self.PRODUCT_NAME_INPUT)

    def is_batch_volume_displayed(self) -> bool:
        """Check if batch volume input is displayed."""
        return self.browser.is_element_displayed(*self.BATCH_VOLUME_INPUT)
