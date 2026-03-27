"""
CalculatorPage - Page Object Model

Page Object for the ROLOS KITCHEN COGS Calculator main app.
Handles navigation tabs, KPI display, and Actions dropdown.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class CalculatorPage:
    """
    Page Object for the COGS Calculator main app.

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

    MANUFACTURING_TAB = (By.XPATH, "//button[.//span[contains(text(),'Manufacturing')]]")
    LOGISTICS_TAB = (By.XPATH, "//button[.//span[contains(text(),'Logistics')]]")
    ANALYTICS_TAB = (By.XPATH, "//button[.//span[contains(text(),'Analytics')]]")
    ACTIONS_BUTTON = (By.XPATH, "//button[contains(text(),'Actions')]")
    UNIT_COST_KPI = (By.XPATH, "//*[contains(text(),'UNIT COST') or contains(text(),'Unit Cost')]")
    BATCH_PROFIT_KPI = (By.XPATH, "//*[contains(text(),'BATCH PROFIT') or contains(text(),'Batch Profit')]")
    GROSS_MARGIN_KPI = (By.XPATH, "//*[contains(text(),'GROSS MARGIN') or contains(text(),'Gross Margin')]")
    UPLOAD_COA_BUTTON = (By.XPATH, "//button[contains(text(),'Upload CoA')]")
    ACTIVE_INGREDIENTS_SECTION = (By.XPATH, "//*[contains(text(),'ACTIVE INGREDIENTS')]")

    # ==================== ATOMIC METHODS ====================

    def wait_for_app_loaded(self, timeout: int = 20) -> "CalculatorPage":
        """Wait for the main app to load."""
        self.browser.wait_for_element_visible(*self.MANUFACTURING_TAB, timeout=timeout)
        return self

    def click_actions(self) -> "CalculatorPage":
        """Click the Actions dropdown button."""
        self.browser.click(*self.ACTIONS_BUTTON)
        return self

    def wait_for_upload_coa_visible(self, timeout: int = 5) -> "CalculatorPage":
        """Wait for Upload CoA option to appear in dropdown."""
        self.browser.wait_for_element_visible(*self.UPLOAD_COA_BUTTON, timeout=timeout)
        return self

    def click_upload_coa(self) -> "CalculatorPage":
        """Click the Upload CoA menu item."""
        self.browser.click(*self.UPLOAD_COA_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_app_loaded(self) -> bool:
        """Check if the main calculator app is loaded."""
        return self.browser.is_element_displayed(*self.MANUFACTURING_TAB, timeout=10)

    def is_unit_cost_displayed(self) -> bool:
        """Check if Unit Cost KPI is displayed."""
        return self.browser.is_element_displayed(*self.UNIT_COST_KPI, timeout=5)

    def is_actions_button_displayed(self) -> bool:
        """Check if Actions button is displayed."""
        return self.browser.is_element_displayed(*self.ACTIONS_BUTTON, timeout=5)

    def is_upload_coa_in_dropdown(self) -> bool:
        """Check if Upload CoA option is in the Actions dropdown."""
        return self.browser.is_element_displayed(*self.UPLOAD_COA_BUTTON, timeout=5)
