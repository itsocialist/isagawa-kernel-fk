"""
MarketingLead - Role module

Represents a marketing lead persona who uses the NQL assistant
to query RevOp Intelligence data.
"""

from interfaces.browser_interface import BrowserInterface
from resources.utilities import autologger
from tasks.revop_intelligence.nql_query_tasks import NqlQueryTasks


class MarketingLead:
    """
    MarketingLead role - orchestrates NQL query workflows.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, browser_interface: BrowserInterface, base_url: str):
        """
        Initialize and compose Task modules.

        Args:
            browser_interface: BrowserInterface instance
            base_url: Base URL for the RevOp Intelligence page
        """
        self.browser = browser_interface
        self.base_url = base_url
        self.nql_query_tasks = NqlQueryTasks(browser_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def search_mqls_via_nql(self, query: str) -> None:
        """
        Complete workflow: Navigate to RevOp Intelligence and query for MQLs.

        Orchestrates MULTIPLE task operations:
        1. Navigate and prepare the NQL panel
        2. Submit the NQL query
        """
        self.nql_query_tasks.navigate_and_prepare_nql(self.base_url)
        self.nql_query_tasks.submit_nql_query(query)
