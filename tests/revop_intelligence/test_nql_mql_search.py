"""
TestNqlMqlSearch - NQL Assistant MQL query test.

Validates that a marketing lead can use the NQL assistant to
find all MQLs in 2026 on the RevOp Intelligence dashboard.

Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
from roles.revop_intelligence.marketing_lead import MarketingLead
from pages.revop_intelligence.nql_assistant_page import NqlAssistantPage


class TestNqlMqlSearch:
    """
    Test NQL Assistant MQL search workflow.

    - @autologger("Test") decorator
    - Role workflow calls for Act
    - Assert via POM state-check methods
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Pytest fixture wires browser and config into the test class."""
        self.browser = browser
        self.config = config
        self.nql_page = NqlAssistantPage(self.browser)

    # ==================== TEST METHODS ====================

    @pytest.mark.revop_intelligence
    @pytest.mark.nql_assistant
    @autologger.automation_logger("Test")
    def test_nql_find_all_mqls_in_2026(self):
        """
        Test: Marketing lead queries NQL assistant for all MQLs in 2026.

        AAA Pattern:
        1. Arrange - Create MarketingLead role with target URL
        2. Act - Execute NQL query via role workflow
        3. Assert - Verify NQL input visible, assistant responded with MQL data
        """
        # Arrange
        target_url = self.config["url"] + "/src/viz/simple-dots-modmin.html"
        query = "find all MQLs in 2026"

        marketing_lead = MarketingLead(
            self.browser,
            base_url=target_url
        )

        # Act
        marketing_lead.search_mqls_via_nql(query)

        # Assert
        assert self.nql_page.is_nql_input_visible(), \
            "NQL input should be visible after panel expansion"

        assert self.nql_page.has_query_results_visible(), \
            "Assistant should display a response after submitting NQL query"

        response_text = self.nql_page.get_last_assistant_response_text()
        assert "MQL" in response_text.upper(), \
            f"Assistant response should reference MQL data, got: '{response_text}'"
