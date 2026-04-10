"""
NqlAssistantPage - Page Object Model

Page Object for the NQL Assistant panel on RevOp Intelligence.
Handles expanding the panel, entering queries, and reading responses.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class NqlAssistantPage:
    """
    Page Object for NQL Assistant Panel.

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

    NQL_PANEL = (By.ID, "nql-chat-panel")
    NQL_INPUT = (By.ID, "nql-input")
    NQL_SEND_BUTTON = (By.ID, "nql-send")
    NQL_MIC_BUTTON = (By.ID, "nql-mic")
    USER_MESSAGE = (By.CSS_SELECTOR, ".nql-message.user")
    ASSISTANT_MESSAGE = (By.CSS_SELECTOR, ".nql-message.assistant")
    LAST_ASSISTANT_MESSAGE = (By.CSS_SELECTOR, ".nql-message.assistant:last-of-type")
    MESSAGES_CONTAINER = (By.CSS_SELECTOR, ".nql-messages")
    VISIBLE_KPI = (By.XPATH, "//div[contains(text(),'Visible')]/preceding-sibling::div")

    # ==================== NAVIGATION ====================

    def navigate(self, url: str) -> "NqlAssistantPage":
        """Navigate to the RevOp Intelligence page."""
        self.browser.navigate_to(url)
        return self

    # ==================== PANEL METHODS ====================

    def expand_nql_panel(self) -> "NqlAssistantPage":
        """Expand the NQL panel if collapsed."""
        self.browser.execute_script(
            "const p = document.getElementById('nql-chat-panel');"
            "if (p && p.classList.contains('collapsed')) {"
            "  p.classList.remove('collapsed');"
            "  const body = p.querySelector('.nql-body');"
            "  if (body) body.style.display = '';"
            "}"
        )
        return self

    def wait_for_nql_input_visible(self, timeout: int = 15) -> "NqlAssistantPage":
        """Wait for the NQL input field to be visible."""
        self.browser.wait_for_element_visible(*self.NQL_INPUT, timeout=timeout)
        return self

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_query(self, query: str) -> "NqlAssistantPage":
        """Enter a query into the NQL input field."""
        self.browser.type(*self.NQL_INPUT, query)
        return self

    def click_send(self) -> "NqlAssistantPage":
        """Click the send button to submit the query."""
        self.browser.click(*self.NQL_SEND_BUTTON)
        return self

    def wait_for_assistant_response(self, timeout: int = 30) -> "NqlAssistantPage":
        """Wait for an assistant response message to appear."""
        self.browser.wait_for_element_visible(*self.ASSISTANT_MESSAGE, timeout=timeout)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_nql_input_visible(self) -> bool:
        """Check if the NQL input field is visible."""
        return self.browser.is_element_displayed(*self.NQL_INPUT)

    def has_assistant_response(self) -> bool:
        """Check if at least one assistant response message is displayed."""
        return self.browser.is_element_displayed(*self.ASSISTANT_MESSAGE)

    def get_last_assistant_response_text(self) -> str:
        """Get the text of the most recent assistant response."""
        return self.browser.get_text(*self.LAST_ASSISTANT_MESSAGE)

    def has_query_results_visible(self) -> bool:
        """Check if query results are visible (assistant responded)."""
        return self.browser.is_element_displayed(*self.ASSISTANT_MESSAGE)

    def get_visible_kpi_count(self) -> str:
        """Get the current 'Visible' KPI value from the header."""
        return self.browser.get_text(*self.VISIBLE_KPI)
