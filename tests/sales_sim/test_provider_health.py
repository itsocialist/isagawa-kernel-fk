"""
S7-OPS-01 — Provider Health Monitor E2E Tests
==============================================
Tests the /api/admin/system/health endpoint and admin UI health badges.

Coverage:
  TC-S7-OPS-01  Health endpoint returns status for each configured provider
  TC-S7-OPS-02  Admin System tab renders health badge per provider
  TC-S7-OPS-03  Anthropic 'credit balance too low' caught and surfaced

Run:
  python3 scripts/grab_cookies.py --domain speakerhero.app --run-tests -- tests/sales_sim/test_provider_health.py

Auth:
  Requires site-admin-level Supabase cookies (ORG_ADMIN_EMAILS user).
"""

import os
import json
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from resources.utilities import autologger


class TestProviderHealth:
    """
    S7-OPS-01: Provider Health Monitor

    Validates:
    - /api/admin/system/health returns structured health status per provider
    - Admin System tab renders health badges with HEALTHY/DEGRADED/DOWN
    - Credit exhaustion errors are caught and surfaced (not swallowed as generic 500)
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser + config. Inject auth cookies."""
        self.browser  = browser
        self.config   = config
        self.base_url = config["url"]

        # Navigate to root to establish domain before injecting cookies
        browser.navigate_to(self.base_url)
        browser.driver.delete_all_cookies()

        raw_cookies = os.environ.get("SPEAKERHERO_COOKIES", "")
        if raw_cookies:
            try:
                is_https = self.base_url.startswith("https://")
                for cookie in json.loads(raw_cookies):
                    browser.driver.add_cookie({
                        "name":     cookie["name"],
                        "value":    cookie["value"],
                        "path":     cookie.get("path", "/"),
                        "secure":   is_https,
                        "httpOnly": cookie.get("httpOnly", False),
                    })
            except (json.JSONDecodeError, KeyError) as e:
                pytest.skip(f"SPEAKERHERO_COOKIES malformed — {e}")

            browser.navigate_to(self.base_url)

    def _skip_if_no_auth(self):
        """Fast-fail if not authenticated."""
        if "/auth/login" in self.browser.driver.current_url:
            pytest.skip("Auth required — run via grab_cookies.py")

    # ── TC-S7-OPS-01: Health endpoint returns structured status ───────────

    @autologger.automation_logger("Test")
    def test_ops_01_health_endpoint_returns_provider_status(self):
        """
        AC(1): /api/admin/system/health returns status for each configured provider.

        Arrange: Authenticated as site admin
        Act:     GET /api/admin/system/health
        Assert:  - Response is 200
                 - JSON contains 'llm' key with provider statuses
                 - Each provider has a 'status' field (HEALTHY|DEGRADED|DOWN)
                 - Each provider has 'latencyMs' (number) and 'error' (string|null)
        """
        self.browser.navigate_to(self.base_url + "/home")
        self._skip_if_no_auth()

        # Hit the health endpoint via JS fetch (reuses browser's auth cookies)
        result = self.browser.driver.execute_script("""
            const res = await fetch('/api/admin/system/health');
            return { status: res.status, body: await res.json() };
        """)

        assert result["status"] == 200, \
            f"Expected 200 from /api/admin/system/health, got {result['status']}"

        body = result["body"]

        # LLM providers
        assert "llm" in body, "Response must contain 'llm' key"
        llm = body["llm"]
        assert isinstance(llm, dict), "'llm' must be a dict of provider statuses"

        for provider_name, provider_status in llm.items():
            assert "status" in provider_status, \
                f"LLM provider '{provider_name}' missing 'status' field"
            assert provider_status["status"] in ("HEALTHY", "DEGRADED", "DOWN"), \
                f"LLM provider '{provider_name}' has invalid status: {provider_status['status']}"
            assert "latencyMs" in provider_status, \
                f"LLM provider '{provider_name}' missing 'latencyMs' field"
            # 'error' can be null or a string
            assert "error" in provider_status, \
                f"LLM provider '{provider_name}' missing 'error' field"

    # ── TC-S7-OPS-02: Admin System tab renders health badges ─────────────

    @autologger.automation_logger("Test")
    def test_ops_02_admin_system_tab_shows_health_badges(self):
        """
        AC(2): Admin System tab renders health badge per provider.

        Arrange: Navigate to /admin, click System tab
        Act:     Wait for health badges to load
        Assert:  - At least one element with data-testid='provider-health-badge' exists
                 - Badge text is one of HEALTHY, DEGRADED, DOWN
        """
        self.browser.navigate_to(self.base_url + "/admin")
        self._skip_if_no_auth()

        # Click System tab
        try:
            system_tab = WebDriverWait(self.browser.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'system') or contains(text(),'SYSTEM')]"))
            )
            system_tab.click()
        except Exception:
            pytest.skip("System tab not visible — user may not be site admin")

        # Wait for health badges to finish loading. The same data-testid is used
        # for the transient "CHECKING…" loading state, so waiting on the testid
        # alone returns too early — wait until at least one badge has resolved
        # to a terminal status (HEALTHY / DEGRADED / DOWN).
        valid_statuses = {"HEALTHY", "DEGRADED", "DOWN"}

        def badges_resolved(d):
            badges = d.find_elements(By.CSS_SELECTOR, "[data-testid='provider-health-badge']")
            if not badges:
                return False
            # Every visible badge must be out of the CHECKING… state
            if not all(b.text.strip().upper() in valid_statuses for b in badges):
                return False
            return badges

        badges = WebDriverWait(self.browser.driver, 20).until(badges_resolved)

        assert len(badges) >= 1, \
            "Expected at least 1 provider health badge on System tab"

        for badge in badges:
            text = badge.text.strip().upper()
            assert text in valid_statuses, \
                f"Health badge has invalid text: '{badge.text}'. Expected one of {valid_statuses}"

    # ── TC-S7-OPS-03: Credit exhaustion is surfaced, not swallowed ───────

    @autologger.automation_logger("Test")
    def test_ops_03_credit_exhaustion_surfaced(self):
        """
        AC(3): Anthropic 'credit balance too low' is caught and surfaced.

        This test verifies the health endpoint correctly identifies
        and reports credit-related errors rather than returning a generic 500.

        Arrange: Authenticated as site admin
        Act:     GET /api/admin/system/health
        Assert:  - If Anthropic is DOWN, the 'error' field contains 'credit'
                   or another specific diagnostic (not a generic traceback)
                 - If Anthropic is HEALTHY, the error field is null
        """
        self.browser.navigate_to(self.base_url + "/home")
        self._skip_if_no_auth()

        result = self.browser.driver.execute_script("""
            const res = await fetch('/api/admin/system/health');
            return { status: res.status, body: await res.json() };
        """)

        if result["status"] != 200:
            pytest.skip("Health endpoint not available")

        body = result["body"]
        anthropic = body.get("llm", {}).get("anthropic")

        if not anthropic:
            pytest.skip("Anthropic not configured — cannot test credit exhaustion")

        if anthropic["status"] == "DOWN":
            # Error should be descriptive, not a raw stack trace
            error_msg = anthropic.get("error", "")
            assert error_msg, \
                "Anthropic is DOWN but no error message — credit exhaustion is being swallowed"
            # Should mention credits, billing, or balance — not a raw exception class
            assert "Error:" not in error_msg or "credit" in error_msg.lower() or "balance" in error_msg.lower(), \
                f"Error message should be user-friendly, got: '{error_msg}'"
        elif anthropic["status"] == "HEALTHY":
            assert anthropic.get("error") is None, \
                f"Anthropic is HEALTHY but has a non-null error: {anthropic.get('error')}"
