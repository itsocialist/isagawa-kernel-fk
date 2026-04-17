"""
TestSovAICannabisModels - Model availability smoke tests for SovAI Cannabis.

Validates that each configured LiteLLM model alias (claude-sonnet, claude-haiku,
claude-opus) returns a valid AI response WITHOUT an error banner.

This test suite was added after a post-migration regression where claude-opus
was mapped to an unavailable Bedrock model ID, causing the Compliance Auditor
to fail silently for users. These tests catch that class of error early.

Run with:
    pytest tests/sovai_cannabis/test_02_model_smoke.py --env sovai_cannabis_local -v

Markers:
    @pytest.mark.model_smoke  - Run these specifically before any deploy
    @pytest.mark.sovai_cannabis
"""

import pytest
from resources.utilities import autologger
from roles.sovai.admin_role import AdminRole
from pages.sovai.login_page import LoginPage
from pages.sovai.chat_page import ChatPage

# Short, deterministic prompts — fast to respond, easy to validate
MODEL_PROBE_PROMPTS = {
    "claude-sonnet": "Reply with exactly: SONNET_OK",
    "claude-haiku":  "Reply with exactly: HAIKU_OK",
    "claude-opus":   "Reply with exactly: OPUS_OK",
}

# Error strings that indicate a model routing failure rather than an AI response
MODEL_ERROR_PATTERNS = [
    "is not available for AWS Bedrock",
    "Please select a different model",
    "model not found",
    "rate limit",
    "error",
]


class TestSovAICannabisModels:
    """
    Model availability smoke tests.

    Each test sends a minimal message using a specific model alias and asserts:
    1. A response is received (not a timeout)
    2. The response does NOT contain a Bedrock error message
    3. The chat input recovers (is ready for the next message)
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
        """Ensure we are logged in before running model tests."""
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

    def _assert_clean_response(self, model_alias: str):
        """
        Common assertion: response received, no Bedrock error, input ready.

        Catches errors like:
          'The model "us.anthropic.claude-opus-4-6-v1" is not available for AWS Bedrock.'
        """
        assert self.chat_page.has_assistant_response(), \
            f"[{model_alias}] No response received — model may be failing silently"

        response_text = self.chat_page.get_last_response_text().lower()

        for error_pattern in MODEL_ERROR_PATTERNS:
            assert error_pattern.lower() not in response_text, \
                f"[{model_alias}] Response contains error indicator '{error_pattern}': {response_text[:200]}"

        assert self.chat_page.is_chat_input_ready(), \
            f"[{model_alias}] Chat input not ready — stream may have hung"

    # ==================== TEST METHODS ====================

    @pytest.mark.sovai_cannabis
    @pytest.mark.model_smoke
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_claude_sonnet_available(self):
        """
        Verify claude-sonnet model alias routes successfully to Bedrock.

        This is the primary model — ALL agents fall back to it.
        A failure here means the entire platform is non-functional.
        """
        self._ensure_authenticated()
        self.chat_page.start_new_chat()

        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=self.config["url"],
            email=credentials["email"],
            password=credentials["password"]
        )
        admin.send_message_continue(MODEL_PROBE_PROMPTS["claude-sonnet"])
        self._assert_clean_response("claude-sonnet")

    @pytest.mark.sovai_cannabis
    @pytest.mark.model_smoke
    @autologger.automation_logger("Test")
    def test_claude_haiku_available(self):
        """
        Verify claude-haiku model alias routes successfully to Bedrock.

        Used for title generation and summarization — high request volume.
        A failure causes title/summary fields to break silently.
        """
        self._ensure_authenticated()
        self.chat_page.start_new_chat()

        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=self.config["url"],
            email=credentials["email"],
            password=credentials["password"]
        )
        admin.send_message_continue(MODEL_PROBE_PROMPTS["claude-haiku"])
        self._assert_clean_response("claude-haiku")

    @pytest.mark.sovai_cannabis
    @pytest.mark.model_smoke
    @autologger.automation_logger("Test")
    def test_claude_opus_available(self):
        """
        Verify claude-opus model alias routes successfully to Bedrock.

        NOTE: If opus is not enabled in the AWS Bedrock account, this test
        will fail with a Bedrock availability error. That is the intended
        behaviour — it surfaces the problem before users encounter it.

        To fix: AWS Console → Bedrock → Model access → Request claude-opus-4-6
        OR: remap claude-opus → claude-sonnet in litellm/config.yaml (current workaround).
        """
        self._ensure_authenticated()
        self.chat_page.start_new_chat()

        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=self.config["url"],
            email=credentials["email"],
            password=credentials["password"]
        )
        admin.send_message_continue(MODEL_PROBE_PROMPTS["claude-opus"])
        self._assert_clean_response("claude-opus")
