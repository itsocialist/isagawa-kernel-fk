"""
NqlQueryTasks - Task module

Orchestrates NqlAssistantPage to accomplish NQL query workflows.
Handles submitting queries and waiting for responses.
"""

from interfaces.browser_interface import BrowserInterface
from pages.revop_intelligence.nql_assistant_page import NqlAssistantPage
from resources.utilities import autologger


class NqlQueryTasks:
    """
    Task module for NQL Query workflow.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        """
        Compose Page Objects — NO decorator on constructor.

        Args:
            browser: BrowserInterface instance
        """
        self.browser = browser
        self.nql_page = NqlAssistantPage(browser)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def navigate_and_prepare_nql(self, url: str) -> None:
        """
        Navigate to RevOp Intelligence and expand the NQL panel.

        Args:
            url: Target URL for the RevOp Intelligence page
        """
        (self.nql_page
            .navigate(url)
            .expand_nql_panel()
            .wait_for_nql_input_visible())

    @autologger.automation_logger("Task")
    def submit_nql_query(self, query: str) -> None:
        """
        Enter and submit an NQL query, then wait for response.

        Args:
            query: Natural language query to submit
        """
        (self.nql_page
            .enter_query(query)
            .click_send()
            .wait_for_assistant_response())
