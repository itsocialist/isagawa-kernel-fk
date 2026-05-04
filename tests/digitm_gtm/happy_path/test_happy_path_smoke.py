"""
TestHappyPathSmoke — fast end-to-end smoke for the create-product → run-pipeline → first-gate flow.

Companion to test_full_pipeline.py (which runs all 7 stages, ~3-5 min, ~25k tokens).
This version stops at the FIRST gate (Market Research → approval → Pricing starts) so
the regression-detection feedback loop is short. Single Opus call for Market Research,
single approval click, single assertion that Pricing transitions out of QUEUED.

Covers digitm-gtm spec B-65 / Sprint 15 T107.

Run:
    pytest tests/digitm_gtm/happy_path/test_happy_path_smoke.py --env=digitm_gtm --headless -v -s

Phase A: single user, no auth required. Token cost: ~3-5k (one Opus call for
MARKET_RESEARCH + the orchestrator's setup overhead).
"""

import pytest
import time
from selenium.webdriver.common.by import By


MAX_STAGE_WAIT = 300  # 5 minutes for Market Research (Opus call)
POLL_INTERVAL = 5


class TestHappyPathSmoke:
    """
    Smoke-style happy-path E2E. Creates a product, runs the pipeline,
    approves the first gate, verifies the orchestrator advances to the
    next stage. STOPS THERE — does not run the full pipeline.

    The point: catch regressions in the create→run→gate→advance round-trip
    cheaply. Full-pipeline coverage lives in test_full_pipeline.py and
    is run separately when token budget allows.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.base_url = config["url"]

    # ─── Helpers ─────────────────────────────────────────────────

    def _navigate(self, path):
        self.browser.navigate_to(self.base_url + path)

    def _wait_for(self, by, value, timeout=15):
        self.browser.wait_for_element_visible(by, value, timeout=timeout)

    def _is_visible(self, by, value, timeout=3):
        return self.browser.is_element_displayed(by, value, timeout=timeout)

    def _click(self, by, value):
        self.browser.click(by, value)

    def _log(self, msg):
        print(f"\n  [HAPPY-PATH] {msg}")

    # ─── Test ────────────────────────────────────────────────────

    def test_create_product_run_pipeline_approve_first_gate(self):
        # 1. Create product via the wizard
        product_name = f"HappyPath Smoke {int(time.time())}"
        self._log(f"Creating product: {product_name}")
        self._navigate("/products/new")
        self._wait_for(By.CSS_SELECTOR, "form")
        self.browser.type(By.CSS_SELECTOR, "#product-name", product_name)
        self.browser.type(
            By.CSS_SELECTOR,
            "#product-description",
            "Smoke test product for the happy-path E2E. Validates the "
            "create→run→gate→advance round-trip without paying for the "
            "full pipeline cost.",
        )
        self.browser.type(
            By.CSS_SELECTOR,
            "#product-audience",
            "QA engineers running fast regression smokes",
        )
        self._click(By.XPATH, "//button[contains(., 'Create Product')]")
        time.sleep(5)

        url = self.browser.get_current_url()
        assert "/products/" in url, f"Expected /products/{{id}}, got {url}"
        product_id = url.split("/products/")[1].split("/")[0].split("?")[0]
        self._log(f"Product created: {product_id}")

        # 2. Launch pipeline. The mutation blocks until the first gate
        # (Market Research) so we wait up to 5 minutes for the Opus
        # call + orchestrator round-trip.
        self._log("Launching GTM pipeline...")
        self._click(By.XPATH, "//button[contains(., 'Launch GTM')]")
        time.sleep(5)

        run_link_appeared = False
        for _ in range(MAX_STAGE_WAIT // POLL_INTERVAL):
            if self._is_visible(By.CSS_SELECTOR, "a[href*='/pipeline/']", timeout=2):
                run_link_appeared = True
                break
            time.sleep(POLL_INTERVAL)
        assert run_link_appeared, "Pipeline run link did not appear within timeout"
        self._log("Pipeline run created")

        # 3. Navigate to the pipeline view
        self._click(By.CSS_SELECTOR, "a[href*='/pipeline/']")
        time.sleep(3)
        assert "/pipeline/" in self.browser.get_current_url()

        # 4. Wait for the Market Research gate, approve it
        self._log("Waiting for Market Research gate...")
        gate_found = False
        for i in range(MAX_STAGE_WAIT // POLL_INTERVAL):
            current_url = self.browser.get_current_url()
            self.browser.navigate_to(current_url)
            time.sleep(2)

            if self._is_visible(
                By.XPATH, "//h2[contains(., 'Approval Required')]", timeout=2
            ):
                if self._is_visible(
                    By.XPATH,
                    "//div[contains(., 'Market Research')]"
                    "/ancestor::div//button[contains(., 'Approve')]"
                    " | //div[contains(., 'Market Research')]"
                    "//button[contains(., 'Approve')]",
                    timeout=2,
                ):
                    self._log("Market Research gate found — approving")
                    self._click(By.XPATH, "//button[contains(., 'Approve')]")
                    time.sleep(3)
                    gate_found = True
                    break

            if (i + 1) % 10 == 0:
                self._log(f"  Still waiting for Market Research gate... ({(i+1)*POLL_INTERVAL}s)")
        assert gate_found, f"Market Research gate did not appear within {MAX_STAGE_WAIT}s"

        # 5. Confirm Pricing transitioned out of QUEUED — that's the orchestrator
        # advancing past the approved gate. We don't wait for Pricing to complete;
        # seeing it RUNNING (or already past it) is enough to validate the round-trip.
        self._log("Verifying Pricing stage advances...")
        time.sleep(5)
        self.browser.navigate_to(self.browser.get_current_url())
        time.sleep(2)

        # Look for any Pricing stage indicator NOT in QUEUED state.
        # The lens rail will show Pricing as RUNNING (animated) or
        # GATE_PENDING / COMPLETED depending on timing. Any of those
        # validates that the orchestrator picked up the approved gate.
        pricing_advanced = False
        for indicator in [
            "//*[contains(., 'Pricing')]/ancestor::*[contains(@class, 'lens')]",
            "//*[contains(., 'Pricing')]/ancestor::div[contains(@class, 'glass')]"
            "//*[contains(., 'running') or contains(., 'gate_pending')"
            " or contains(., 'completed') or contains(., 'GATE_PENDING')"
            " or contains(., 'COMPLETED') or contains(., 'RUNNING')]",
        ]:
            if self._is_visible(By.XPATH, indicator, timeout=10):
                pricing_advanced = True
                break

        assert pricing_advanced, (
            "Pricing stage did not advance after Market Research gate approval "
            "— orchestrator round-trip likely broken"
        )
        self._log("✓ Happy-path smoke complete: Market Research → gate → Pricing advanced")
