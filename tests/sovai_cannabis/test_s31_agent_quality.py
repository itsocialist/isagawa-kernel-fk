"""
TestS31AgentQuality - Smoke tests for Sprint 31 Agents in the Cannabis domain.

Agents under test:
  - Labor & Shift Optimizer (B-05, Agent #18)
  - Menu Intelligence (B-09, Agent #19)

Run with:
    pytest tests/sovai_cannabis/test_s31_agent_quality.py --env sovai_cannabis_local -v --headless
"""

import pytest
import time
from resources.utilities import autologger
from roles.sovai.admin_role import AdminRole
from pages.sovai.login_page import LoginPage
from pages.sovai.chat_page import ChatPage

class TestS31AgentQuality:
    """
    Automated verification of the Sprint 29/30 Cannabis Agents (tested in S31).
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config, test_users):
        """Wire up the browser, configuration, and test users."""
        self.browser = browser
        self.config = config
        self.test_users = test_users
        
        self.base_url = self.config["url"].rstrip("/")
        self.login_page = LoginPage(self.browser)
        self.chat_page = ChatPage(self.browser)

    def _ensure_authenticated_and_ready(self):
        """Ensure we are logged in and onboarding is dismissed."""
        current_url = self.browser.get_current_url()
        if self.base_url in current_url and "/login" not in current_url:
            self._bypass_onboarding()
            return
            
        self.browser.navigate_to(f"{self.base_url}/login")
        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=self.base_url,
            email=credentials["email"],
            password=credentials["password"]
        )
        admin.login_and_verify()
        
        # Wait for SPA to settle
        time.sleep(3)
        self._bypass_onboarding()

    def _bypass_onboarding(self):
        """Bypass the Liquid Glass onboarding wizard using the memory API."""
        self.browser.execute_script("""
            if (!window.__sovaiTestFetchDone) {
                window.__sovaiTestFetchDone = false;
                fetch('/api/memory/', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key: 'onboarding_complete', value: 'true', confidence: 1.0 })
                })
                .then(r => { window.__sovaiTestFetchDone = true; })
                .catch(err => { window.__sovaiTestFetchDone = true; });
            }
        """)
        
        # Wait for the async fetch to hit the network
        for _ in range(20):
            if self.browser.execute_script("return window.__sovaiTestFetchDone;"):
                break
            time.sleep(0.2)
            
        # Refresh to ensure overlay is gone
        self.browser.driver.refresh()
        self.chat_page.wait_for_chat_ready()
        
        # Force remove any lingering overlays that intercept clicks
        self.browser.execute_script("document.getElementById('sovai-onboarding-overlay')?.remove();")
        self.browser.execute_script("document.querySelectorAll('[data-testid=\"banner\"]').forEach(e => e.remove());")

    def _send_and_get_response(self, agent_name: str, prompt: str) -> str:
        """Helper to navigate to new chat, address agent, send prompt, and capture string response."""
        self._ensure_authenticated_and_ready()
        
        self.browser.navigate_to(f"{self.base_url}/c/new")
        self.chat_page.wait_for_chat_ready()

        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=self.base_url,
            email=credentials["email"],
            password=credentials["password"]
        )
        
        # Use the built-in role method to select the agent from the UI and send
        admin.select_agent_and_send(agent_name, prompt)

        assert self.chat_page.has_assistant_response(), \
            f"[{agent_name}] No response received"

        response_text = self.chat_page.get_last_response_text()

        # Must not be an error banner
        error_indicators = [
            "is not available",
            "Please select a different model",
            "model not found",
        ]
        for indicator in error_indicators:
            assert indicator.lower() not in response_text.lower(), \
                f"[{agent_name}] Response is an error: {response_text[:200]}"
                
        return response_text

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.s31
    @autologger.automation_logger("Test")
    def test_agent_18_labor_shift_optimizer(self):
        """
        Agent 18: Labor & Shift Optimizer
        Should analyze labor data and determine §280E COGS deductibility.
        """
        response = self._send_and_get_response(
            "Labor & Shift Optimizer",
            "Please analyze my labor timesheet: 40 hours receiving inventory, 40 hours budtending."
        )
        
        response_lower = response.lower()
        assert "280e" in response_lower, "Agent did not mention 280E as expected."
        assert "cogs" in response_lower or "deductible" in response_lower, "Agent did not analyze deductibility."
        
    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.s31
    @autologger.automation_logger("Test")
    def test_agent_19_menu_intelligence(self):
        """
        Agent 19: Menu Intelligence
        Should analyze SKU velocity and margin and produce recommendations.
        """
        response = self._send_and_get_response(
            "Menu Intelligence",
            "I have a SKU 'Blue Dream 1/8th' with 50 units sold per day at a 15% margin. Another SKU 'Stale Gummies' has 0 sales in 20 days. Provide recommendations."
        )
        
        response_lower = response.lower()
        assert "dead stock" in response_lower or "markdown" in response_lower, "Agent did not identify dead stock."
        assert "margin" in response_lower and "velocity" in response_lower, "Agent did not analyze velocity/margin."
