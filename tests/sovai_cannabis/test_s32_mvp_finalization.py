"""
TestS32MVPFinalization - TDD Baseline tests for Sprint 32 P0 features.

Features under test:
  - P0: Inventory Forecast Report Artifact (Inventory Forecaster agent)
  - P0: Vault Door Login Page (sovereignty branding on auth screen)
  - P0: Upload-First Workflow (CSV/file upload prioritized in chat chrome)

Run with:
    pytest tests/sovai_cannabis/test_s32_mvp_finalization.py --env sovai_cannabis_local -v --headless
"""

import pytest
import time
from resources.utilities import autologger
from roles.sovai.admin_role import AdminRole
from pages.sovai.login_page import LoginPage
from pages.sovai.chat_page import ChatPage


class TestS32MVPFinalization:
    """
    TDD baseline suite for Sprint 32 — MVP Finalization & UI Parity.
    These tests MUST fail before feature implementation and PASS after.
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

    # =========================================================================
    # P0: Inventory Forecast Report Artifact
    # =========================================================================

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.s32
    @autologger.automation_logger("Test")
    def test_inventory_forecaster_generates_artifact(self):
        """
        P0: Inventory Forecast Report Artifact
        The Inventory Forecaster agent should generate a React artifact with
        demand predictions, reorder recommendations, and dead stock list
        when presented with velocity data.
        """
        response = self._send_and_get_response(
            "Inventory Forecaster",
            "Here is my last 30 days of inventory velocity: "
            "Blue Dream 1/8th sold 150 units (avg 5/day), "
            "Sour Diesel 1g Cart sold 90 units (avg 3/day), "
            "Stale Gummies 10mg sold 2 units in 30 days. "
            "Current stock: Blue Dream 20, Sour Diesel 45, Stale Gummies 200. "
            "Generate an Inventory Forecast Report artifact with demand predictions, "
            "reorder recommendations, and dead stock identification."
        )

        # Verify the agent produced an artifact (button or inline)
        assert self.chat_page.has_artifact_button(), \
            "Inventory Forecaster did not generate a React artifact."

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.s32
    @autologger.automation_logger("Test")
    def test_inventory_forecast_contains_key_sections(self):
        """
        P0: Inventory Forecast Report — Content Validation
        The artifact response must reference demand forecast, reorder, and dead stock.
        """
        response = self._send_and_get_response(
            "Inventory Forecaster",
            "Analyze inventory velocity for 3 SKUs: "
            "SKU-A 200 units/month, SKU-B 50 units/month, SKU-C 0 units in 30 days. "
            "Provide a full forecast report."
        )

        response_lower = response.lower()
        assert "reorder" in response_lower or "replenish" in response_lower, \
            "Inventory Forecaster did not mention reorder recommendations."
        assert "dead stock" in response_lower or "slow-moving" in response_lower or "stale" in response_lower, \
            "Inventory Forecaster did not identify dead/slow stock."

    # =========================================================================
    # P0: Vault Door Login Page
    # =========================================================================

    @pytest.mark.sovai_cannabis
    @pytest.mark.s32
    @pytest.mark.ui
    @autologger.automation_logger("Test")
    def test_vault_door_login_branding(self):
        """
        P0: Vault Door Login Page
        The login page must display the SovAI sovereignty-first branding:
        - SovAI brand identity visible (logo or heading)
        - 'Data Vault' or 'Sovereign' language present
        - No visible LibreChat branding leak
        """
        self.browser.navigate_to(f"{self.base_url}/login")
        time.sleep(2)

        page_source = self.browser.driver.page_source.lower()

        # Vault Door branding must be present
        assert "vault" in page_source or "sovereign" in page_source, \
            "Vault Door: sovereignty branding not found on login page."

        # SovAI identity must be present
        assert "sovai" in page_source, \
            "Vault Door: SovAI brand identity not found on login page."

    @pytest.mark.sovai_cannabis
    @pytest.mark.s32
    @pytest.mark.ui
    @autologger.automation_logger("Test")
    def test_vault_door_no_librechat_leak(self):
        """
        P0: Vault Door Login — No Branding Leak
        The login page must NOT show visible 'LibreChat' text in the UI.
        """
        self.browser.navigate_to(f"{self.base_url}/login")
        time.sleep(2)

        # Check visible text elements only (not hidden metadata)
        visible_text = self.browser.execute_script(
            "return document.body.innerText.toLowerCase();"
        )

        assert "librechat" not in visible_text, \
            "Vault Door: LibreChat branding is leaking through on the login page."

    # =========================================================================
    # P0: Upload-First Workflow
    # =========================================================================

    @pytest.mark.sovai_cannabis
    @pytest.mark.s32
    @pytest.mark.ui
    @autologger.automation_logger("Test")
    def test_upload_first_drop_zone_visible(self):
        """
        P0: Upload-First Workflow
        The chat interface should have a prominent file upload zone
        that is visually prioritized over the text input.
        """
        self._ensure_authenticated_and_ready()

        page_source = self.browser.driver.page_source.lower()

        # Look for upload-first UI elements
        assert (
            "upload-first" in page_source
            or "drop files" in page_source
            or "drop-zone" in page_source
            or "upload your data" in page_source
        ), "Upload-First: No prominent upload zone found in chat interface."

    @pytest.mark.sovai_cannabis
    @pytest.mark.s32
    @pytest.mark.ui
    @autologger.automation_logger("Test")
    def test_upload_first_csv_detection(self):
        """
        P0: Upload-First Workflow — CSV Detection
        When a file input is present, it should accept CSV files
        and have smart format detection messaging.
        """
        self._ensure_authenticated_and_ready()

        page_source = self.browser.driver.page_source.lower()

        # Look for CSV-specific upload guidance
        assert (
            ".csv" in page_source
            or "csv" in page_source
            or "dutchie" in page_source
            or "flowhub" in page_source
            or "spreadsheet" in page_source
        ), "Upload-First: No CSV/POS format detection guidance found."
