"""
KpiDashboardPage - Page Object Model

Page Object for the ROLOS KITCHEN COGS Calculator KPI dashboard cards.
Handles reading Unit Cost, Batch Profit, and Gross Margin values.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class KpiDashboardPage:
    """
    Page Object for the KPI Dashboard cards.

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

    UNIT_COST_CARD = (By.XPATH, "//*[contains(text(),'Unit Cost')]/../..")
    BATCH_PROFIT_CARD = (By.XPATH, "//*[contains(text(),'Batch Profit')]/../..")
    GROSS_MARGIN_CARD = (By.XPATH, "//*[contains(text(),'Gross Margin')]/../..")
    COGS_VALUE = (By.XPATH, "//*[contains(text(),'COGS')]/..")

    # ==================== STATE-CHECK METHODS ====================

    def get_unit_cost_text(self) -> str:
        """Get the full Unit Cost card text."""
        return self.browser.get_text(*self.UNIT_COST_CARD)

    def get_unit_cost_value(self) -> str:
        """Extract the dollar value from Unit Cost card (e.g. '$18.01')."""
        text = self.get_unit_cost_text()
        for line in text.split("\n"):
            if line.startswith("$"):
                return line
        return ""

    def get_unit_cost_breakdown(self) -> str:
        """Get the Mfg + Dist breakdown line from Unit Cost card."""
        text = self.get_unit_cost_text()
        for line in text.split("\n"):
            if "Mfg" in line:
                return line
        return ""

    def get_batch_profit_text(self) -> str:
        """Get the full Batch Profit card text."""
        return self.browser.get_text(*self.BATCH_PROFIT_CARD)

    def get_batch_profit_value(self) -> str:
        """Extract the dollar value from Batch Profit card."""
        text = self.get_batch_profit_text()
        for line in text.split("\n"):
            if line.startswith("$"):
                return line
        return ""

    def get_gross_margin_text(self) -> str:
        """Get the full Gross Margin card text."""
        return self.browser.get_text(*self.GROSS_MARGIN_CARD)

    def get_gross_margin_value(self) -> str:
        """Extract the percentage from Gross Margin card."""
        text = self.get_gross_margin_text()
        for line in text.split("\n"):
            if "%" in line and "rev" not in line:
                return line
        return ""

    def is_unit_cost_displayed(self) -> bool:
        """Check if Unit Cost card is displayed."""
        return self.browser.is_element_displayed(*self.UNIT_COST_CARD)

    def is_batch_profit_displayed(self) -> bool:
        """Check if Batch Profit card is displayed."""
        return self.browser.is_element_displayed(*self.BATCH_PROFIT_CARD)

    def is_gross_margin_displayed(self) -> bool:
        """Check if Gross Margin card is displayed."""
        return self.browser.is_element_displayed(*self.GROSS_MARGIN_CARD)
