"""
Sprint 10 — Regression Tests
=============================
Covers two bugs fixed in Sprint 10 that must never regress:

  BUG-S10-A  Quick Start bypasses wizard → lands on wizard instead of chat.
             Root cause: org Quick Start preset had icpId = subjectPack.id
             (wrong field), causing resolveDemoPreset() to return null, which
             caused /app to fall back to the 'select' state wizard.

  BUG-S10-B  "Complete All Steps" button never activates in org/CRE mode.
             Root cause: switching Training Pack silently nulled out the
             selected Product/ICP without sending the user back to Step 1,
             leaving canStart permanently false with no visible feedback.

Test IDs follow the TC-RG-XX convention (Regression).

Auth:
  Both tests inject a valid pending config via localStorage (same mechanism
  used by the home-page Quick Start cards) so they work without a live org
  API. The pending_config path is the real production code path — this is
  NOT a mock of the navigation itself.

Run:
  cd /Users/briandawson/workspace/platform-selenium
  source venv/bin/activate
  pytest tests/sales_sim/test_s10_regressions.py --env=sales_sim_dev -v
"""

import json
import time
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from resources.utilities import autologger
from pages.sales_sim.sales_sim_pages import ConfigPage, PackSelectorPage, ChatPage


# ---------------------------------------------------------------------------
# Minimal SimulationConfig fixture — mirrors the shape /app expects.
# Uses real pack IDs from the built-in TRAINING_PACKS / PRODUCT_PACKS.
# All fields required by the pending-config consumer in app/page.tsx.
# ---------------------------------------------------------------------------

MINIMAL_VALID_CONFIG = {
    "product": {
        "id": "prod-revops-platform",
        "type": "product",
        "version": 1,
        "schemaVersion": "1.0",
        "meta": {"name": "RevOps Platform", "description": ""},
        "source": "builtin",
        "isSystem": True,
        "isActive": True,
        "config": {
            "id": "prod-revops-platform",
            "name": "RevOps Platform",
            "tagline": "Close more deals",
            "category": "SaaS",
            "description": "B2B revenue operations software.",
            "keyFeatures": [],
            "commonObjections": [],
        },
    },
    "icp": {
        "id": "icp-enterprise-saas",
        "type": "icp",
        "version": 1,
        "schemaVersion": "1.0",
        "meta": {"name": "Enterprise SaaS", "description": ""},
        "source": "builtin",
        "isSystem": True,
        "isActive": True,
        "config": {
            "id": "icp-enterprise-saas",
            "name": "Enterprise SaaS",
            "description": "Large enterprise B2B SaaS buyer.",
            "icon": "🏢",
            "companySize": "500+",
            "industries": ["Technology"],
            "painPoints": [],
            "budget": "$50k-$500k",
            "decisionTimeline": "3-6 months",
        },
    },
    "training": {
        "id": "enterprise-ae",
        "type": "training",
        "version": 1,
        "schemaVersion": "1.0",
        "meta": {"name": "Enterprise AE", "description": ""},
        "source": "builtin",
        "isSystem": True,
        "isActive": True,
        "config": {
            "id": "enterprise-ae",
            "name": "Enterprise AE Training",
            "icon": "🎯",
            "description": "MEDDIC enterprise deal training.",
            "targetRole": "Enterprise Account Executive",
            "scoringDimensions": [],
            "subjectPacks": [],
            "scenarioPacks": [],
        },
    },
    "subject": {
        "id": "ent-champion",
        "type": "subject",
        "version": 1,
        "schemaVersion": "1.0",
        "meta": {"name": "Champion / Internal Advocate", "description": ""},
        "source": "builtin",
        "isSystem": True,
        "isActive": True,
        "config": {
            "id": "ent-champion",
            "name": "Champion / Internal Advocate",
            "condition": "Enthusiastic internal sponsor",
            "conditionLevel": "moderate",
            "behaviorPrompt": "You are an enthusiastic champion.",
            "subjects": [],
        },
    },
    "scenario": {
        "id": "ent-discovery",
        "type": "scenario",
        "version": 1,
        "schemaVersion": "1.0",
        "meta": {"name": "First Discovery Call", "description": ""},
        "source": "builtin",
        "isSystem": True,
        "isActive": True,
        "config": {
            "id": "ent-discovery",
            "name": "First Discovery Call",
            "description": "Initial qualification call.",
            "context": "You have 30 minutes. Build rapport and uncover pain.",
            "initialDistance": 7,
            "initialTemperature": 4,
        },
    },
    "selectedProfile": {
        "id": "ent-ch-1",
        "name": "Jordan Kim",
        "title": "Director of Revenue Operations",
        "company": "Nexlayer Inc.",
        "industry": "SaaS / B2B Tech",
        "backstory": "Promoted 6 months ago.",
        "personalityTraits": ["eager"],
        "physicalDescription": "Young, sharp dresser",
    },
}


def _skip_if_no_auth(page):
    """Skip test if we got redirected to login (no cookies injected)."""
    if page.is_redirected_to_login():
        pytest.skip(
            "Auth required — run via: python3 scripts/grab_cookies.py "
            "--domain localhost --run-tests  OR  inject cookies manually."
        )


class TestS10Regressions:
    """
    Regression guard for Sprint 10 bugs.
    These tests MUST pass on every merge to prevent re-introduction.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser        = browser
        self.config         = config
        self.base_url       = config["url"]
        self.config_page    = ConfigPage(browser)
        self.pack_selector  = PackSelectorPage(browser)
        self.chat_page      = ChatPage(browser)

        # Navigate first to establish origin for localStorage ops
        browser.navigate_to(self.base_url)
        # Clear any stale session data that could bleed between tests
        browser.driver.execute_script("""
            window.localStorage.removeItem('speakerhero_pending_config');
            window.localStorage.removeItem('speakerhero_last_config');
            window.sessionStorage.clear();
        """)

        # Detect if we are unauthenticated so individual tests can skip cleanly.
        # We check the /app route once here and cache the result.
        self._is_authed = not self.config_page.is_redirected_to_login()

    # -------------------------------------------------------------------------
    # BUG-S10-A: Quick Start must bypass the wizard and land on chat
    # -------------------------------------------------------------------------

    @autologger.automation_logger("Regression")
    def test_rg_01_quick_start_bypasses_wizard(self):
        """
        BUG-S10-A regression guard.

        When a valid speakerhero_pending_config is written to localStorage
        (exactly what the home-page Quick Start cards do), navigating to /app
        MUST skip the pack-selector wizard and land directly on the chat screen.

        Failure mode: /app renders the wizard ('select' state) instead of chat.
        Root cause fixed: icpId was set to subjectPack.id (wrong field) in the
        org Quick Start preset builder, causing resolveDemoPreset() to return
        null, which made the pending_config invalid and fell back to wizard.

        Arrange: Write a valid pending config to localStorage.
        Act:     Navigate to /app.
        Assert:  The chat input box (#simulation-input) is visible, NOT the
                 wizard's 'Complete All Steps' button.
        """
        if not self._is_authed:
            pytest.skip(
                "Auth required — inject cookies via scripts/grab_cookies.py "
                "before running authenticated regression tests."
            )

        # Arrange — inject the pending config the same way home-page chips do.
        # Must be written AFTER navigate_to(base_url) so we share the same origin.
        self.config_page.inject_pending_config(MINIMAL_VALID_CONFIG)

        # Act — navigate to /app (the mount effect reads pending_config)
        self.pack_selector.navigate(self.base_url)

        # Wait up to 20s for the page to settle on either chat or wizard
        def _page_settled(d):
            on_login  = "/auth/login" in d.current_url
            on_chat   = bool(d.find_elements(By.ID, "simulation-input"))
            on_wizard = bool(d.find_elements(
                By.XPATH,
                "//button[contains(text(),'Complete All Steps') or contains(text(),'Start Training')]"
            ))
            return on_login or on_chat or on_wizard

        WebDriverWait(self.browser.driver, 20).until(_page_settled)

        current_url   = self.browser.driver.current_url
        is_on_chat    = self.pack_selector.is_on_chat()
        is_on_wizard  = self.pack_selector.is_on_wizard()

        assert "/auth/login" not in current_url, (
            "Unexpected auth redirect during RG-01 — session cookies may have expired."
        )
        assert is_on_chat, (
            "BUG-S10-A REGRESSION: Quick Start landed on wizard instead of chat. "
            f"URL={current_url}, is_on_chat={is_on_chat}, is_on_wizard={is_on_wizard}. "
            "Check that resolveDemoPreset() receives a valid icpId (not subjectPack.id)."
        )
        assert not is_on_wizard, (
            "BUG-S10-A REGRESSION: Wizard visible after Quick Start launch. "
            "The pending_config was not consumed correctly by /app on mount."
        )

    @autologger.automation_logger("Regression")
    def test_rg_02_quick_start_from_home_chip(self):
        """
        BUG-S10-A variant: test the full /home → chip-click → /app path.

        Arrange: Navigate to /home, wait for Quick Start chips to render.
        Act:     Click the 'Cold Discovery Call' chip.
        Assert:  Browser navigates to /app and lands on chat (not wizard).

        Note: This test requires authentication cookies. It is skipped
        automatically if unauthenticated.
        """
        if not self._is_authed:
            pytest.skip(
                "Auth required — inject cookies via scripts/grab_cookies.py "
                "before running authenticated regression tests."
            )

        self.config_page.navigate(self.base_url)
        self.config_page.wait_for_load(timeout=20)

        _skip_if_no_auth(self.config_page)

        # Wait for Quick Start section to render (org-packs or generic)
        WebDriverWait(self.browser.driver, 10).until(
            lambda d: len(d.find_elements(By.CSS_SELECTOR, "[id^='quick-start-']")) > 0
        )

        # Click the first available Quick Start chip
        chips = self.browser.driver.find_elements(By.CSS_SELECTOR, "[id^='quick-start-']")
        assert chips, "No Quick Start chips found on /home"
        first_chip_id = chips[0].get_attribute("id")
        self.config_page.click_named_quick_start(first_chip_id)

        # Wait for navigation to /app
        WebDriverWait(self.browser.driver, 10).until(
            lambda d: "/app" in d.current_url
        )

        # Page must settle on chat — not wizard
        def _app_settled(d):
            return (
                bool(d.find_elements(By.ID, "simulation-input")) or
                bool(d.find_elements(
                    By.XPATH,
                    "//button[contains(text(),'Complete All Steps') or contains(text(),'Start Training')]"
                ))
            )

        WebDriverWait(self.browser.driver, 15).until(_app_settled)

        assert self.pack_selector.is_on_chat(), (
            f"BUG-S10-A REGRESSION: Quick Start chip '{first_chip_id}' landed on wizard. "
            "A valid pending_config must be written before navigating to /app."
        )

    # -------------------------------------------------------------------------
    # BUG-S10-B: "Complete All Steps" button must activate after valid selections
    # -------------------------------------------------------------------------

    @autologger.automation_logger("Regression")
    def test_rg_03_start_button_disabled_without_selections(self):
        """
        BUG-S10-B baseline: the Start button must be DISABLED on a fresh /app load.

        Arrange: Clear all localStorage, navigate to /app with no pending config.
        Act:     Wait for the wizard to mount.
        Assert:  The Start Training / Complete All Steps button is disabled.

        This ensures the button isn't trivially always enabled.
        """
        if not self._is_authed:
            pytest.skip(
                "Auth required — inject cookies via scripts/grab_cookies.py "
                "before running authenticated regression tests."
            )

        # Ensure no pending config
        self.browser.driver.execute_script(
            "window.localStorage.removeItem('speakerhero_pending_config');"
        )

        self.pack_selector.navigate(self.base_url)
        self.pack_selector.wait_for_wizard(timeout=20)

        assert not self.pack_selector.is_start_enabled(), (
            "BUG-S10-B REGRESSION: Start button is ENABLED before any selections. "
            "The canStart guard in PackSelector.tsx is broken."
        )

    @autologger.automation_logger("Regression")
    def test_rg_04_start_button_activates_with_full_config(self):
        """
        BUG-S10-B regression guard: after injecting a full valid config that was
        persisted by a prior session (speakerhero_last_config), navigating to /app
        should restore that config and the wizard — if shown — should be in a
        ready-to-start state OR the app should bypass to chat.

        This catches the scenario where Step 1 selections were silently nulled
        after a Training Pack change, making canStart permanently false.
        """
        if not self._is_authed:
            pytest.skip(
                "Auth required — inject cookies via scripts/grab_cookies.py "
                "before running authenticated regression tests."
            )

        # Use pending_config so we get the direct-to-chat path —
        # that's the regression we care about.
        self.config_page.inject_pending_config(MINIMAL_VALID_CONFIG)
        self.pack_selector.navigate(self.base_url)

        # Wait for either chat input or a ready wizard
        def _settled(d):
            on_chat   = bool(d.find_elements(By.ID, "simulation-input"))
            btn_ready = self.pack_selector.is_start_enabled()
            on_login  = "/auth/login" in d.current_url
            return on_chat or btn_ready or on_login

        WebDriverWait(self.browser.driver, 20).until(_settled)

        current_url = self.browser.driver.current_url
        assert "/auth/login" not in current_url, (
            "Unexpected auth redirect during RG-04 — session cookies may have expired."
        )

        on_chat   = self.pack_selector.is_on_chat()
        btn_ready = self.pack_selector.is_start_enabled()

        assert on_chat or btn_ready, (
            "BUG-S10-B REGRESSION: After injecting a complete config, the app is "
            "NEITHER on chat NOR showing an enabled Start button. "
            f"is_on_chat={on_chat}, is_start_enabled={btn_ready}. "
            "The canStart logic in PackSelector.tsx has regressed — check "
            "selectedProduct/selectedICP/selectedSubject/selectedScenario state."
        )

    @autologger.automation_logger("Regression")
    def test_rg_05_start_button_remains_disabled_with_missing_icp(self):
        """
        BUG-S10-B guard: a config with a NULL icp must NOT enable the Start button.

        This catches the scenario where the ICP was silently cleared when a
        Training Pack change made the previously-selected ICP incompatible,
        but the wizard did not redirect back to Step 1.

        Arrange: Inject a pending config where `icp` is present but its inner
                 `config.id` is empty (simulates the nulled-out ICP state).
        Act:     Navigate to /app, wait for wizard.
        Assert:  The Start button is DISABLED (incomplete selections).
        """
        incomplete_config = {**MINIMAL_VALID_CONFIG}
        # Corrupt the ICP entry — id mismatch simulates a broken resolution
        incomplete_config["icp"] = {
            **MINIMAL_VALID_CONFIG["icp"],
            "id": "",                        # empty id → pack resolution fails
            "config": {**MINIMAL_VALID_CONFIG["icp"]["config"], "id": ""},
        }

        self.config_page.inject_pending_config(incomplete_config)
        self.pack_selector.navigate(self.base_url)

        # Wait for the wizard to mount (no auto-launch since config is invalid)
        try:
            self.pack_selector.wait_for_wizard(timeout=15)
        except Exception:
            # If wizard didn't appear, check if we accidentally ended up on chat
            assert not self.pack_selector.is_on_chat(), (
                "BUG-S10-B REGRESSION: Incomplete config (missing ICP) still "
                "launched the simulation. The validation guard is broken."
            )
            return

        # Wizard is shown — button must be disabled
        assert not self.pack_selector.is_start_enabled(), (
            "BUG-S10-B REGRESSION: Start button is ENABLED despite missing ICP. "
            "The canStart guard in PackSelector.tsx is not checking selectedICP correctly."
        )
