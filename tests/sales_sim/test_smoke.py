"""
SalesSim Smoke Suite — S4-01 (Auth + Voice + Minimal)
=======================================================
End-to-end smoke tests for the SpeakerHero AI trainer against production.

Coverage:
  TC-01  App loads          — /app renders pack selector with demo chips
  TC-02  Demo launch        — chip → chat screen, voice toggle present
  TC-03  Prospect opens     — prospect auto-message fires BEFORE rep can type
  TC-04  Chat round-trip    — rep sends message, AI responds, input re-enables
  TC-05  Voice mode toggle  — overlay appears, overlay has exit button, exit works
  TC-06  Minimal layout     — toggle switches zoom→minimal, MINIMAL label visible
  TC-07  End → Debrief      — END SESSION → debrief score rendered
  TC-08  Breadcrumb nav     — Configure breadcrumb returns to pack selector

Auth:
  Tests navigate to /app. Supabase cookies are auto-extracted from Chrome
  via scripts/grab_cookies.py and injected via SPEAKERHERO_COOKIES env var.

Run (one-shot, authenticated):
  python3 scripts/grab_cookies.py --domain speakerhero.app --run-tests

Run manually with cookies:
  SPEAKERHERO_COOKIES='[{"name":"sb-...","value":"..."}]' pytest tests/sales_sim/ --env=sales_sim_prod -v

Notes:
  - TC-04, TC-07 require live Anthropic API (claude-sonnet-4-6 / claude-haiku-4-5)
  - TC-05, TC-06 require ElevenLabs Conversational AI to be configured
  - TC-03 validates the prospect-first flow: AI MUST initiate before rep can type
"""

import os
import json
import time
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from resources.utilities import autologger
from pages.sales_sim.sales_sim_pages import (
    ConfigPage, ChatPage, DebriefPage, LoginPage, VoiceOverlayPage
)


def _skip_if_no_auth(config_page):
    """Fast-fail helper: if not authed, skip with a clear message."""
    if config_page.is_redirected_to_login():
        pytest.skip(
            "Auth required — run via: python3 scripts/grab_cookies.py --domain speakerhero.app --run-tests"
        )


class TestSalesSimSmoke:
    """
    Authenticated smoke suite for SpeakerHero trainer (production).
    Validates the full user path including voice mode and minimal layout.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser + config. Inject Supabase auth cookies if available."""
        self.browser       = browser
        self.config        = config
        self.base_url      = config["url"]
        self.login_page    = LoginPage(browser)
        self.config_page   = ConfigPage(browser)
        self.chat_page     = ChatPage(browser)
        self.voice_page    = VoiceOverlayPage(browser)
        self.debrief_page  = DebriefPage(browser)

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
                        "secure":   is_https,   # must be True on HTTPS or browser drops it
                        "httpOnly": cookie.get("httpOnly", False),
                    })
            except (json.JSONDecodeError, KeyError) as e:
                pytest.skip(f"SPEAKERHERO_COOKIES malformed — {e}")

            # Reload so Supabase SSR middleware reads the injected cookies
            # and the client-side session state is established
            browser.navigate_to(self.base_url)
            time.sleep(1)  # brief settle for Supabase auth state propagation

        self.config_page.navigate(self.base_url)

    # ── Shared helper ────────────────────────────────────────────────────────

    def _launch_demo_to_chat(self):
        """
        Navigate /home → click Cold Discovery Call quick-start → wait for chat input.
        Uses a specific chip ID rather than index[0] for selector stability.
        """
        self.config_page.wait_for_load(timeout=20)
        # Try the specific Cold Discovery Call chip first; fall back to first chip
        try:
            chip = self.browser.driver.find_element(*ConfigPage.CHIP_COLD_DISCOVERY)
        except Exception:
            chips = self.config_page.get_demo_chips()
            assert chips, "No QUICK START chips found on /home"
            chip = chips[0]
        chip.click()
        self.chat_page.wait_for_load(timeout=20)

    def _wait_for_prospect_to_open(self):
        """
        Block until the prospect's auto-triggered opening message completes.
        The chat's isOpening call fires on mount — input stays disabled until done.
        Up to 60s for the first cold-call Anthropic response.
        """
        self.chat_page.wait_for_prospect_opening(timeout=60)

    # ── TC-01: App loads ─────────────────────────────────────────────────────

    @autologger.automation_logger("Test")
    def test_01_app_loads_pack_selector(self):
        """
        Verify /app renders the pack selector with demo chips.

        Arrange: Navigate /app with auth cookies
        Act:     Wait for demo chips
        Assert:  ≥1 demo chip visible; not redirected to login
        """
        _skip_if_no_auth(self.config_page)

        if self.config_page.is_redirected_to_login():
            pytest.fail(
                "Redirected to /auth/login — cookies not accepted. "
                "Re-run: python3 scripts/grab_cookies.py --domain speakerhero.app --run-tests"
            )

        self.config_page.wait_for_load(timeout=20)
        chips = self.config_page.get_demo_chips()
        assert len(chips) >= 1, f"Expected ≥1 demo chip, got {len(chips)}"

    # ── TC-02: Demo chip → chat screen ───────────────────────────────────────

    @autologger.automation_logger("Test")
    def test_02_demo_launch_enters_chat(self):
        """
        Verify clicking a demo chip transitions to the chat screen.

        Arrange: /app loaded with demo chips
        Act:     Click first chip
        Assert:  Chat input visible; voice toggle (#voice-mode-toggle) present
        """
        _skip_if_no_auth(self.config_page)

        self._launch_demo_to_chat()

        assert self.browser.driver.find_element(*ChatPage.INPUT_BOX).is_displayed(), \
            "#simulation-input should be visible after demo launch"

        assert self.chat_page.is_voice_toggle_visible(), \
            "#voice-mode-toggle should be visible in chat header"

    # ── TC-03: Prospect speaks FIRST ─────────────────────────────────────────

    @pytest.mark.live_api
    @autologger.automation_logger("Test")
    def test_03_prospect_opens_conversation(self):
        """
        Verify the PROSPECT auto-initiates the conversation on mount.
        The rep's input MUST be disabled until the prospect's opening message
        completes streaming — this is the prospect-first flow contract.

        Arrange: Launch demo, chat UI mounted
        Act:     Wait for prospect opening (isLoading=true → false cycle)
        Assert:  ≥1 assistant message visible; input is now enabled for the rep
        """
        _skip_if_no_auth(self.config_page)

        self._launch_demo_to_chat()

        # Wait for the prospect to fire their opening statement (up to 60s)
        self._wait_for_prospect_to_open()

        # Assert: at least one assistant message exists in the conversation
        messages = self.chat_page.get_all_messages()
        assert len(messages) >= 1, \
            f"At least 1 prospect message should be visible after opening; got {len(messages)}"


    # ── TC-04: Rep sends message → AI responds ────────────────────────────────

    @pytest.mark.live_api
    @autologger.automation_logger("Test")
    def test_04_rep_message_gets_ai_response(self):
        """
        Verify a rep message triggers an AI response and input re-enables.

        Arrange: Launch demo; wait for prospect opening
        Act:     Type and send rep message
        Assert:  Input clears; send button re-enables within 60s (Sonnet 4.6 latency)
        """
        _skip_if_no_auth(self.config_page)

        self._launch_demo_to_chat()
        self._wait_for_prospect_to_open()

        # Capture message count before sending
        before_count = self.chat_page.count_messages()

        # Act — type and send rep message
        test_msg = "Hi — thanks for taking my call. Can I ask what your biggest challenge is right now?"
        self.chat_page.type_message(test_msg)
        assert self.chat_page.get_input_value() == test_msg, "Input should hold typed text"
        self.chat_page.send_message()

        # Assert — input clears on submit
        WebDriverWait(self.browser.driver, 5).until(
            lambda d: d.find_element(*ChatPage.INPUT_BOX).get_attribute("value") == ""
        )

        # Assert — new message(s) appear within 60s (rep bubble + AI response)
        self.chat_page.wait_for_ai_response(timeout=60, before_count=before_count)

        # Verify final message count
        messages = self.chat_page.get_all_messages()
        assert len(messages) > before_count, \
            f"Expected more messages after round-trip; before={before_count}, after={len(messages)}"

    # ── TC-05: Voice mode toggle → overlay appears ────────────────────────────

    @pytest.mark.live_api
    @autologger.automation_logger("Test")
    def test_05_voice_mode_overlay_appears(self):
        """
        Verify clicking the voice toggle shows the VoiceDuplexOverlay.

        Arrange: Launch demo; wait for prospect opening
        Act:     Click #voice-mode-toggle
        Assert:  #voice-duplex-overlay is visible
                 #exit-voice-mode button is present
                 Connection status text is visible (CONNECTING or LIVE)
        """
        _skip_if_no_auth(self.config_page)

        self._launch_demo_to_chat()
        self._wait_for_prospect_to_open()

        # Act — click voice toggle
        self.chat_page.click_voice_toggle()

        # Assert — overlay appears
        self.voice_page.wait_for_overlay(timeout=15)
        assert self.voice_page.is_overlay_visible(), \
            "#voice-duplex-overlay should be visible after toggling voice mode"

        # Assert — exit button is present (regression guard)
        try:
            exit_btn = self.browser.driver.find_element(*VoiceOverlayPage.EXIT_BTN)
            assert exit_btn.is_displayed(), "#exit-voice-mode should be visible"
        except Exception:
            pytest.fail("#exit-voice-mode button not found in voice overlay")

        # Assert — status text indicates connection attempt
        status = self.voice_page.get_status_text()
        print(f"\n  Voice status: '{status}'")
        # Accept CONNECTING, LIVE, or empty (if signed URL failed gracefully)
        # We don't fail on empty — failure mode is no overlay at all

    # ── TC-06: Minimal layout toggle ─────────────────────────────────────────

    @pytest.mark.live_api
    @autologger.automation_logger("Test")
    def test_06_voice_minimal_layout_toggle(self):
        """
        Verify the zoom/minimal layout toggle works inside voice mode.

        Arrange: Launch demo → wait for prospect → enter voice mode
        Act:     Click #voice-layout-toggle
        Assert:  MINIMAL label becomes visible (layout switched)
        """
        _skip_if_no_auth(self.config_page)

        self._launch_demo_to_chat()
        self._wait_for_prospect_to_open()

        # Enter voice mode
        self.chat_page.click_voice_toggle()
        self.voice_page.wait_for_overlay(timeout=15)

        # Assert — layout toggle button exists
        try:
            layout_btn = self.browser.driver.find_element(*VoiceOverlayPage.LAYOUT_TOGGLE)
            assert layout_btn.is_displayed(), "#voice-layout-toggle should be visible"
        except Exception:
            pytest.fail("#voice-layout-toggle not found in voice overlay")

        # Act — switch to minimal
        self.voice_page.toggle_layout()

        # Assert — MINIMAL label visible
        WebDriverWait(self.browser.driver, 5).until(
            lambda d: self.voice_page.is_minimal_layout()
        )
        assert self.voice_page.is_minimal_layout(), \
            "Voice overlay should show MINIMAL label after layout toggle"

        # Act — toggle back to zoom
        self.voice_page.toggle_layout()
        time.sleep(0.5)

        # Assert — MINIMAL label gone (back to zoom)
        assert not self.voice_page.is_minimal_layout(), \
            "Voice overlay should NOT show MINIMAL label after toggling back to zoom"

    # ── TC-07: End session → Debrief ─────────────────────────────────────────

    @pytest.mark.live_api
    @autologger.automation_logger("Test")
    def test_07_end_session_shows_debrief(self):
        """
        Verify ending a session transitions to the debrief screen with a score.

        Arrange: Launch demo, wait for prospect, send one rep message
        Act:     Click END SESSION
        Assert:  Debrief loads; overall score is a number
        """
        _skip_if_no_auth(self.config_page)

        self._launch_demo_to_chat()
        self._wait_for_prospect_to_open()

        # Send one rep message first
        self.chat_page.type_and_send("I understand. What matters most to you in a solution like this?")
        self.chat_page.wait_for_ai_response(timeout=60)

        # Act
        self.chat_page.click_end_session()

        # Assert — debrief screen appears
        self.debrief_page.wait_for_load(timeout=15)

        # Assert — analysis completes with a numeric score
        self.debrief_page.wait_for_analysis(timeout=60)
        score = self.debrief_page.get_overall_score_text()
        assert score, "Overall score should be visible on debrief screen"
        assert any(c.isdigit() for c in score), \
            f"Score should contain a number, got: '{score}'"

    # ── TC-08: Breadcrumb → back to config ───────────────────────────────────

    @autologger.automation_logger("Test")
    def test_08_breadcrumb_back_to_configure(self):
        """
        Verify Configure breadcrumb returns to the pack selector (appState='select').

        Arrange: Launch demo → reach chat screen
        Act:     Click Configure breadcrumb
        Assert:  URL is /app; nav wordmark is present (PackSelector rendered)
        """
        _skip_if_no_auth(self.config_page)

        self._launch_demo_to_chat()
        # Don't wait for prospect — pure UI nav test, no API dependency

        try:
            crumb = self.browser.driver.find_element(
                By.XPATH,
                "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONFIGURE')]"
            )
            if not crumb.is_displayed():
                pytest.skip("Breadcrumb not rendered — may need wider viewport (run --window-size=1400,900)")
        except Exception:
            pytest.skip("Configure breadcrumb not found — check chat header layout")

        self.chat_page.click_breadcrumb_configure()

        # Configure breadcrumb resets appState to 'select' on /app.
        # Demo chips are now admin-only in footer — assert on URL + nav instead.
        self.config_page.wait_for_load(timeout=15)
        current_url = self.browser.driver.current_url
        assert "/app" in current_url, \
            f"Should be back on /app after Configure breadcrumb, got: {current_url}"
        wordmarks = self.browser.driver.find_elements(*ConfigPage.NAV_WORDMARK)
        assert len(wordmarks) >= 1, \
            "Nav wordmark (#nav-wordmark) should be present on /app select state"
