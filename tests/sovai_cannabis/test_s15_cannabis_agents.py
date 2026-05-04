"""
TestS15CannabisAgents - Smoke tests for Sprint 15 Agents in the Cannabis domain.

Agents under test:
  - SovAI Orchestrator
  - Compliant Marketing Advisor
  - Formulation Assistant
  - COA Interpreter

Run with:
    pytest tests/sovai_cannabis/test_s15_cannabis_agents.py --env sovai_cannabis_local -v --headless
"""

import pytest
from resources.utilities import autologger
from roles.sovai.admin_role import AdminRole
from pages.sovai.login_page import LoginPage
from pages.sovai.chat_page import ChatPage

MIN_RESPONSE_CHARS = 80

STATIC_AGENT_IDS = {} # Deprecated in favor of UI automation

class TestS15CannabisAgents:
    """
    Automated verification of the Sprint 15 Cannabis Agents.
    Uses Isagawa-QA 5-Layer architecture.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config, test_users):
        """Wire up the browser, configuration, and test users."""
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
            
        self.browser.navigate_to(f"{base_url}/login")
        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=base_url,
            email=credentials["email"],
            password=credentials["password"]
        )
        admin.login_and_verify()

    def _send_and_get_response(self, agent_name: str, prompt: str, min_length: int = 80) -> str:
        """Helper to navigate to agent, send prompt, and capture string response."""
        self._ensure_authenticated()

        base_url = self.config["url"].rstrip("/")
        
        # Hardcoded IDs to avoid MongoDB connectivity issues from Isagawa container
        agent_id_map = {
            "SovAI Orchestrator": "agent_aTcvjUswLsusIWXeeffxl",
            "Compliant Marketing Advisor": "agent_b4RRmoAoXhKj0VALYFI7p"
        }
        agent_id = agent_id_map.get(agent_name)
        
        if agent_id:
            self.browser.navigate_to(f"{base_url}/c/new?models={agent_id}")
        else:
            self.browser.navigate_to(f"{base_url}/c/new")
            
        self.chat_page.wait_for_chat_ready()

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

        if min_length > 0:
            assert len(self.chat_page.get_last_response_text()) >= min_length, \
                f"[{agent_name}] Response too short ({len(self.chat_page.get_last_response_text())} chars < {min_length}): {response_text}"

        assert self.chat_page.is_chat_input_ready(), \
            f"[{agent_name}] Chat input not ready after response"

        return response_text


    # ==================== TEST METHODS ====================

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_orchestrator_routing_csv(self):
        """SovAI Orchestrator routes CSV ingestion question to Inventory Forecaster."""
        qa = self._send_and_get_response(
            "SovAI Orchestrator",
            "I just downloaded my Dutchie sales report and want to predict my stockouts and dead stock. What should I do with it?"
        ).lower()
        
        assert "inventory forecaster" in qa, "Did not mention Inventory Forecaster"
        assert "chatgpt" not in qa and "openai" not in qa, "Mentioned generic AI incorrectly"


    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_compliant_marketing_copy_review(self):
        """Compliant Marketing Advisor flags incorrect health claims."""
        qa = self._send_and_get_response(
            "Compliant Marketing Advisor",
            "Can I post this on Instagram? 'Our Blue Dream helps with anxiety and stress relief. 20% off this weekend only! DM us to order.'"
        ).lower()
        
        assert "non-compliant" in qa or "fail" in qa or "caution" in qa or "no" in qa, "Did not appropriately flag copy"
        assert "anxiety" in qa or "stress" in qa or "health" in qa, "Did not identify health claim"


    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_formulation_dosing(self):
        """Formulation Assistant properly calculates THC dosing logic."""
        qa = self._send_and_get_response(
            "Formulation Assistant",
            "I'm making 100 gummies and want 10mg THC each. My distillate is 85% THC. How much do I add?"
        ).lower()
        
        # 100 * 10mg = 1000mg THC. 1000 / 0.85 = 1176mg distillate = 1.176g
        assert "1.17" in qa or "1.18" in qa or "117" in qa, "Did not calculate correctly"
        assert "/" in qa or "divided" in qa or "10" in qa, "Did not show formula"


    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_coa_interpretation(self):
        """COA Interpreter computes total THC and reports pass/fail."""
        qa = self._send_and_get_response(
            "COA Interpreter",
            "Interpret this COA: THCA 22.4%, D9-THC 0.8%, CBD 0.1%, Myrcene 0.8%, Limonene 0.4%, Caryophyllene 0.3%. Pesticides: all ND. Microbials: PASS."
        ).lower()
        
        # 22.4 * 0.877 + 0.8 = 20.444
        assert "20.4" in qa, "Did not calculate Total THC correctly (≈20.4%)"
        assert "pass" in qa, "Did not include PASS rating"

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_artifact_jsx_compilation(self):
        """Validates that artifacts generate strictly valid JSX without Sandpack unterminated string crashes."""
        qa = self._send_and_get_response(
            "Compliant Marketing Advisor",
            "Generate a React dashboard artifact detailing rules for Digital Age-Gating, Promotional Offers, and Social Media. For each rule, include a very long multi-sentence description. Use the Recharts library if needed.",
            min_length=0
        )

        import re
        import subprocess
        # Extract code block
        match = re.search(r'```(?:jsx|tsx?|javascript)\n([\s\S]*?)\n```', qa)
        assert match, "Did not generate a code artifact"
        code = match.group(1)

        # Basic RegEx check for the exact Unterminated String bug:
        # A newline inside a double quote or single quote attribute like `detail="Line1\nLine2"`
        # This typically looks like an equals sign, a quote, some text, a newline, more text, and a closing quote
        
        # Test compiler with Babel via a quick node script
        node_script = f"""
const babel = require('@babel/core');
try {{
    babel.transformSync(`{code.replace('`', '\\`').replace('$', '\\$')}`, {{
        presets: ['@babel/preset-react'],
        filename: 'App.tsx'
    }});
    console.log('SUCCESS');
}} catch (e) {{
    console.error('COMPILE_ERROR: ' + e.message);
    process.exit(1);
}}
"""
        with open("/tmp/test_compile.js", "w") as f:
            f.write(node_script)
            
        import os
        env = os.environ.copy()
        env["PATH"] += ":/usr/local/bin:/opt/homebrew/bin:~/.orbstack/bin"
        
        result = subprocess.run(["node", "/tmp/test_compile.js"], capture_output=True, text=True, cwd="/tmp", env=env)
        if result.returncode != 0:
            assert False, f"JSX Compilation Failed (Regression): {result.stderr}"

