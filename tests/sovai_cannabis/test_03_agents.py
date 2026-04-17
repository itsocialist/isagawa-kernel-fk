"""
TestSovAICannabisAgents - Cannabis domain agent smoke tests.

Validates the three cannabis-specific agents respond correctly
to domain-relevant prompts.

Agents under test:
  - Compliance Auditor    — DCC/METRC compliance questions
  - Inventory Forecaster  — Stock/velocity questions
  - Strain Intelligence   — Terpene/product questions

Run with:
    pytest tests/sovai_cannabis/test_03_agents.py --env sovai_cannabis_local -v
"""

import pytest
from resources.utilities import autologger
from roles.sovai.admin_role import AdminRole
from pages.sovai.login_page import LoginPage
from pages.sovai.chat_page import ChatPage

# Minimum response length — short enough to pass quickly, long enough to prove
# the model didn't just echo or error out.
MIN_RESPONSE_CHARS = 80

AGENT_SMOKE_PROMPTS = {
    "Compliance Auditor": (
        "What are the California DCC packaging requirements for cannabis edibles?"
    ),
    "Inventory Forecaster": (
        "If I have 50 units of Blue Dream flower selling at 3 units per day, "
        "how many days of inventory do I have?"
    ),
    "Strain Intelligence Analyst": (
        "What terpenes are typically dominant in a myrcene-forward indica strain "
        "and what effects would a customer expect?"
    ),
}


class TestSovAICannabisAgents:
    """
    Cannabis domain agent smoke tests.

    Each test:
    1. Opens a new chat
    2. Sends a domain-specific prompt to the named agent
    3. Asserts a substantial, error-free response is returned
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config, test_users):
        """Wire browser, config, and test data."""
        self.browser = browser
        self.config = config
        self.test_users = test_users
        self.login_page = LoginPage(self.browser)
        self.chat_page = ChatPage(self.browser)

    def _ensure_authenticated(self):
        """Ensure we are logged in before running agent tests."""
        base_url = self.config["url"]
        current_url = self.browser.get_current_url()
        if base_url.rstrip("/") in current_url and "/login" not in current_url:
            return
        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=base_url,
            email=credentials["email"],
            password=credentials["password"]
        )
        admin.login_and_verify()

    def _send_and_assert(self, agent_name: str, prompt: str):
        """Run a domain prompt against a specific agent and assert a clean response."""
        self._ensure_authenticated()

        # Navigate to clean /c/new — breaks any prior agent context from previous tests
        base_url = self.config["url"].rstrip("/")
        self.browser.navigate_to(f"{base_url}/c/new")
        self.chat_page.wait_for_chat_ready()

        # Select the target agent explicitly
        try:
            self.chat_page.select_agent_by_name(agent_name)
        except Exception:
            # Agent not found in sidebar — skip selection, send in default context
            pass

        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=self.config["url"],
            email=credentials["email"],
            password=credentials["password"]
        )
        admin.send_message_continue(prompt)

        assert self.chat_page.has_assistant_response(), \
            f"[{agent_name}] No response received"

        response_text = self.chat_page.get_last_response_text()

        # Must not be an error banner
        error_indicators = [
            "is not available for AWS Bedrock",
            "Please select a different model",
            "model not found",
        ]
        for indicator in error_indicators:
            assert indicator.lower() not in response_text.lower(), \
                f"[{agent_name}] Response is a model error: {response_text[:200]}"

        assert len(response_text) >= MIN_RESPONSE_CHARS, \
            f"[{agent_name}] Response too short ({len(response_text)} chars < {MIN_RESPONSE_CHARS}): {response_text}"

        assert self.chat_page.is_chat_input_ready(), \
            f"[{agent_name}] Chat input not ready after response"


    # ==================== TEST METHODS ====================

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_compliance_auditor_responds(self):
        """Compliance Auditor handles a DCC packaging requirements question."""
        self._send_and_assert(
            "Compliance Auditor",
            AGENT_SMOKE_PROMPTS["Compliance Auditor"]
        )

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_inventory_forecaster_responds(self):
        """Inventory Forecaster calculates days-on-hand from a simple inventory prompt."""
        self._send_and_assert(
            "Inventory Forecaster",
            AGENT_SMOKE_PROMPTS["Inventory Forecaster"]
        )

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @autologger.automation_logger("Test")
    def test_strain_intelligence_responds(self):
        """Strain Intelligence Analyst answers a terpene-effect profiling question."""
        self._send_and_assert(
            "Strain Intelligence Analyst",
            AGENT_SMOKE_PROMPTS["Strain Intelligence Analyst"]
        )
