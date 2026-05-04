"""
SalesSim Page Objects
=====================
Page Object Model for the SpeakerHero trainer application.

Covers:
- LoginPage      : /auth/login — Supabase magic-link + Google OAuth
- ConfigPage     : /app — Pack selector / quick-start screen (appState == 'select')
- ChatPage       : /app — Simulation chat screen (appState == 'chat')
- DebriefPage    : /app — Post-session debrief screen (appState == 'debrief')

Auth: Tests use pre-injected Supabase session cookies (see conftest.py).
      LoginPage is provided for interactive/manual auth flows.

All waits use the BrowserInterface explicit_wait from config.
All element IDs are the stable `id` attributes set in the components.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    """
    Login screen — /auth/login
    Uses Supabase magic link or Google OAuth.
    """

    EMAIL_INPUT   = (By.ID, "auth-email")
    MAGIC_LINK_BTN = (By.XPATH, "//button[contains(text(),'Send Magic Link')]")
    GOOGLE_BTN    = (By.XPATH, "//button[contains(text(),'Continue with Google')]")
    BRAND_LABEL   = (By.XPATH, "//*[contains(text(),'SPEAKERHERO')]")
    SIGN_IN_H1    = (By.XPATH, "//h1[contains(text(),'Sign in')]")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def navigate(self, base_url):
        self.browser.navigate_to(f"{base_url}/auth/login")

    def wait_for_load(self, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.EMAIL_INPUT)
        )

    def is_on_login_page(self):
        try:
            return self.driver.find_element(*self.EMAIL_INPUT).is_displayed()
        except Exception:
            return False

    def enter_email(self, email):
        el = self.driver.find_element(*self.EMAIL_INPUT)
        el.clear()
        el.send_keys(email)

    def click_magic_link(self):
        self.driver.find_element(*self.MAGIC_LINK_BTN).click()


class LandingPage:
    """
    Marketing / Landing page — /
    Contains the Waitlist Email Capture form.
    """

    WAITLIST_EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    WAITLIST_SUBMIT_BTN  = (By.XPATH, "//button[contains(text(),'Join Waitlist')]")
    WAITLIST_SUCCESS_MSG = (By.XPATH, "//*[contains(text(),\"You're on the list\")]")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def navigate(self, base_url):
        self.browser.navigate_to(base_url)

    def wait_for_load(self, timeout=15):
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.WAITLIST_EMAIL_INPUT)
        )

    def fill_waitlist_email(self, email):
        el = self.driver.find_element(*self.WAITLIST_EMAIL_INPUT)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
        el.clear()
        el.send_keys(email)

    def submit_waitlist(self):
        el = self.driver.find_element(*self.WAITLIST_SUBMIT_BTN)
        self.driver.execute_script("arguments[0].click();", el)

    def is_success_message_visible(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.WAITLIST_SUCCESS_MSG)
            )
            return True
        except Exception:
            return False


class ConfigPage:
    """
    Home / Quick-Start screen.
    URL: /home  (returning users) — shows last session + QUICK STARTS sidebar

    Auth required — unauthenticated users are redirected to /auth/login.
    """

    # Stable selectors — match id attributes in app/home/page.tsx
    QUICK_START_CHIP = (By.CSS_SELECTOR, "[id^='quick-start-']")   # /home dashboard chips
    APP_SELECT_CHIP  = (By.CSS_SELECTOR, "[id^='demo-']")           # /app select-state chips (after breadcrumb)
    NAV_WORDMARK     = (By.ID, "nav-wordmark")
    NEW_SESSION_BTN  = (By.ID, "nav-configure")                    # "New Session" in nav
    CONFIGURE_BTN    = (By.ID, "btn-configure-custom")             # "CONFIGURE CUSTOM SESSION"

    # Known quick-start IDs (for targeted launches from /home)
    CHIP_COLD_DISCOVERY   = (By.ID, "quick-start-cold-discovery")
    CHIP_EXECUTIVE_PITCH  = (By.ID, "quick-start-executive-pitch")
    CHIP_OBJECTION        = (By.ID, "quick-start-objection-gauntlet")
    CHIP_CLOUD11          = (By.ID, "quick-start-cloud-11-ecosystem-demo")

    # Practice Again / New Scenario buttons (returning user dashboard)
    PRACTICE_AGAIN_BTN    = (By.ID, "btn-practice-again")
    NEW_SCENARIO_BTN      = (By.ID, "btn-new-scenario")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def navigate(self, base_url):
        """Navigate to /home (the authenticated dashboard entry point)."""
        self.browser.navigate_to(f"{base_url}/home")

    def wait_for_load(self, timeout=20):
        """Wait until the nav wordmark is visible (confirms /home rendered)."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.NAV_WORDMARK)
        )

    def is_redirected_to_login(self):
        """Returns True if the page redirected to /auth/login."""
        try:
            return (
                "/auth/login" in self.driver.current_url or
                self.driver.find_element(By.ID, "auth-email").is_displayed()
            )
        except Exception:
            return "/auth/login" in self.driver.current_url

    def get_demo_chips(self):
        """Return all QUICK START chip buttons."""
        return self.driver.find_elements(*self.QUICK_START_CHIP)

    def click_demo_chip(self, index=0):
        """Click the nth QUICK START chip (launches a preset simulation)."""
        chips = self.get_demo_chips()
        assert chips, "No QUICK START chips found on /home"
        chips[index].click()

    def click_named_quick_start(self, chip_id: str):
        """
        Click a Quick Start card by its full element ID (e.g. 'quick-start-cold-discovery').
        Scrolls into view before clicking to handle off-screen chips.
        """
        el = self.driver.find_element(By.ID, chip_id)
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
        self.driver.execute_script("arguments[0].click();", el)

    def inject_pending_config(self, config: dict):
        """
        Write a SimulationConfig to localStorage as 'speakerhero_pending_config'.
        Simulates what the home-page Quick Start cards do before navigating to /app.
        The /app page reads this on mount and skips the wizard, going straight to chat.
        """
        import json
        self.driver.execute_script(
            "window.localStorage.setItem('speakerhero_pending_config', arguments[0]);",
            json.dumps(config)
        )

    def inject_last_config(self, config: dict):
        """
        Write a SimulationConfig to localStorage as 'speakerhero_last_config'.
        Simulates the config stored after a successful session (used by 'Practice Again').
        """
        import json
        self.driver.execute_script(
            "window.localStorage.setItem('speakerhero_last_config', arguments[0]);",
            json.dumps(config)
        )


class PackSelectorPage:
    """
    Pack Selector wizard — /app when appState == 'select'

    Models the 4-step configuration wizard:
      Step 1 (context): Product + ICP selection
      Step 2 (role):    Training Pack
      Step 3 (subject): Subject (stakeholder archetype)
      Step 4 (scenario): Scenario

    Selectors match id attributes in PackSelector.tsx.
    """

    # Step navigation pills / buttons
    STEP_CONTEXT  = (By.CSS_SELECTOR, "[data-step='context'], button[id*='step-context']")
    STEP_ROLE     = (By.CSS_SELECTOR, "[data-step='role'], button[id*='step-role']")
    STEP_SUBJECT  = (By.CSS_SELECTOR, "[data-step='subject'], button[id*='step-subject']")
    STEP_SCENARIO = (By.CSS_SELECTOR, "[data-step='scenario'], button[id*='step-scenario']")

    # Step header text — used as a reliable "which step am I on?" indicator
    STEP_HEADER   = (By.CSS_SELECTOR, ".pack-selector-step-header, h2.step-title, [class*='step-header']")

    # The "Complete All Steps to Start" / "Start Training" button
    START_BTN     = (By.XPATH, "//button[contains(text(),'Start') or contains(text(),'Complete All Steps')]")

    # Generic card selectors for selectable items (products, ICPs, training packs, etc.)
    SELECTABLE_CARD = (By.CSS_SELECTOR, "[data-selectable='true'], .pack-card, [class*='selectable']")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def navigate(self, base_url):
        """Navigate directly to the wizard at /app."""
        self.browser.navigate_to(f"{base_url}/app")

    def wait_for_wizard(self, timeout=20):
        """Wait until the Start button is present — wizard is mounted."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.START_BTN)
        )

    def get_start_button(self):
        """Return the Start/Complete-All-Steps button element."""
        return self.driver.find_element(*self.START_BTN)

    def is_start_enabled(self):
        """
        Return True if the Start Training button is fully enabled.
        Handles both the disabled attribute and aria-disabled patterns.
        """
        try:
            btn = self.get_start_button()
            disabled_attr = btn.get_attribute("disabled")
            aria_disabled  = btn.get_attribute("aria-disabled")
            # A button is enabled when neither attribute signals disabled
            return (
                disabled_attr is None and
                aria_disabled not in ("true", "1")
            )
        except Exception:
            return False

    def wait_for_start_enabled(self, timeout=15):
        """Wait until the Start button becomes enabled (all steps satisfied)."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: self.is_start_enabled()
        )

    def wait_for_start_disabled(self, timeout=10):
        """Assert the button stays disabled (used in regression guards)."""
        WebDriverWait(self.driver, timeout).until(
            lambda d: not self.is_start_enabled()
        )

    def click_start(self):
        """Click the Start Training button (assumes it is enabled)."""
        btn = self.get_start_button()
        self.driver.execute_script("arguments[0].click();", btn)

    def is_on_wizard(self):
        """Return True if the pack-selector wizard is rendered on /app."""
        try:
            return self.get_start_button().is_displayed()
        except Exception:
            return False

    def is_on_chat(self):
        """Return True if the page has transitioned to the chat view (simulation input visible)."""
        try:
            return self.driver.find_element(By.ID, "simulation-input").is_displayed()
        except Exception:
            return False


class ChatPage:
    """
    Simulation Chat screen.
    URL: /app  (appState == 'chat')
    """

    INPUT_BOX        = (By.ID, "simulation-input")
    SEND_BTN         = (By.ID, "send-btn")
    VOICE_TOGGLE     = (By.ID, "voice-mode-toggle")
    END_BTN          = (By.XPATH, "//button[contains(text(),'END')]")
    CONNECTING_MSG   = (By.XPATH, "//*[contains(text(),'joining the call')]")

    # Assistant (prospect) messages: the outer row is justify-start, contains sim-msg-group
    # This is the authoritative selector for 'prospect has spoken'
    PROSPECT_MSG     = (By.CSS_SELECTOR, "div.flex.justify-start .sim-msg-group")

    # All message groups (both user + assistant) — used for count-based wait
    ALL_MSG_GROUPS   = (By.CSS_SELECTOR, ".sim-msg-group")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def wait_for_load(self, timeout=20):
        """Wait until the chat input box is visible (UI mounted)."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.INPUT_BOX)
        )

    def wait_for_prospect_opening(self, timeout=60):
        """
        Wait for the prospect's auto-triggered opening message to appear in the DOM.
        The send button is controlled by `disabled={isLoading || !input.trim()}`:
        — we can't rely on button state since it stays disabled with empty input.
        Instead, wait for a 'justify-start sim-msg-group' element (assistant bubble).
        """
        WebDriverWait(self.driver, timeout).until(
            lambda d: len(d.find_elements(*self.PROSPECT_MSG)) >= 1
        )

    def count_messages(self):
        """Return total number of message groups currently rendered."""
        return len(self.driver.find_elements(*self.ALL_MSG_GROUPS))

    def get_all_messages(self):
        """Return all rendered message group elements."""
        return self.driver.find_elements(*self.ALL_MSG_GROUPS)

    def type_message(self, text):
        box = self.driver.find_element(*self.INPUT_BOX)
        box.clear()
        box.send_keys(text)

    def send_message(self):
        self.driver.find_element(*self.SEND_BTN).click()

    def type_and_send(self, text):
        self.type_message(text)
        self.send_message()

    def get_input_value(self):
        return self.driver.find_element(*self.INPUT_BOX).get_attribute("value")

    def wait_for_ai_response(self, timeout=60, before_count=None):
        """
        Wait for a new message to appear after the rep sends one.
        Uses message count rather than button state, since the send button
        requires non-empty input to enable — it won't re-enable on its own.

        Args:
            before_count: message count before sending; waits for count to increase.
                          If None, waits for any message group to appear.
        """
        if before_count is not None:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(*self.ALL_MSG_GROUPS)) > before_count
            )
        else:
            # Fallback: wait for isLoading to clear by checking button with text pre-typed
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(*self.PROSPECT_MSG)) >= 2
            )

    def is_send_disabled(self):
        btn = self.driver.find_element(*self.SEND_BTN)
        return not btn.is_enabled() or btn.get_attribute("disabled") == "true"

    def is_voice_toggle_visible(self):
        try:
            return self.driver.find_element(*self.VOICE_TOGGLE).is_displayed()
        except Exception:
            return False

    def click_voice_toggle(self):
        self.driver.find_element(*self.VOICE_TOGGLE).click()

    def click_end_session(self):
        self.driver.find_element(*self.END_BTN).click()

    def click_breadcrumb_configure(self):
        """Click the Configure breadcrumb to go back to pack selection."""
        crumbs = self.driver.find_elements(
            By.XPATH, "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONFIGURE')]"
        )
        for c in crumbs:
            if c.is_displayed():
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
                self.driver.execute_script("arguments[0].click();", c)
                return
        raise AssertionError("Configure breadcrumb not found or not visible")


class VoiceOverlayPage:
    """
    Voice Duplex Overlay — shown when voice mode is active.
    Activated by clicking #voice-mode-toggle on the ChatPage.

    Selectors match VoiceDuplexOverlay.tsx id attributes.
    """

    OVERLAY          = (By.ID, "voice-duplex-overlay")
    LAYOUT_TOGGLE    = (By.ID, "voice-layout-toggle")    # zoom ↔ minimal
    EXIT_BTN         = (By.ID, "exit-voice-mode")
    EXIT_BTN_MOBILE  = (By.ID, "exit-voice-mode-mobile")

    # Button label shows where you'd GO next (not current state)
    # When in ZOOM layout  → button reads "MINIMAL" (click to go minimal)
    # When in MINIMAL layout → button reads "ZOOM"   (click to go back to zoom)
    LAYOUT_BTN_WHEN_MINIMAL = (By.XPATH, "//*[@id='voice-layout-toggle' and contains(text(),'ZOOM')]")
    LAYOUT_BTN_WHEN_ZOOM    = (By.XPATH, "//*[@id='voice-layout-toggle' and contains(text(),'MINIMAL')]")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def wait_for_overlay(self, timeout=15):
        """Wait for the voice overlay to appear."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.OVERLAY)
        )

    def is_overlay_visible(self):
        try:
            return self.driver.find_element(*self.OVERLAY).is_displayed()
        except Exception:
            return False

    def get_status_text(self):
        """Return the current connection status label."""
        try:
            return self.driver.find_element(*self.STATUS_TEXT).text.strip()
        except Exception:
            return ""

    def toggle_layout(self):
        """Click the zoom/minimal layout toggle button."""
        self.driver.find_element(*self.LAYOUT_TOGGLE).click()

    def is_minimal_layout(self):
        """
        Returns True if currently in MINIMAL view.
        When in minimal mode, the toggle button label reads 'ZOOM' (the next state).
        """
        try:
            btn = self.driver.find_element(*self.LAYOUT_TOGGLE)
            return 'ZOOM' in btn.text and 'MINIMAL' not in btn.text
        except Exception:
            return False

    def is_zoom_layout(self):
        """Returns True if currently in ZOOM view (button reads 'MINIMAL')."""
        try:
            btn = self.driver.find_element(*self.LAYOUT_TOGGLE)
            return 'MINIMAL' in btn.text
        except Exception:
            return False

    def exit_voice_mode(self):
        """Click the exit button to leave voice mode."""
        try:
            btn = self.driver.find_element(*self.EXIT_BTN)
        except Exception:
            btn = self.driver.find_element(*self.EXIT_BTN_MOBILE)
        btn.click()



class DebriefPage:
    """
    Debrief screen — post-session scoring + analysis.
    URL: /app  (appState == 'debrief')
    """

    RETRY_BTN          = (By.XPATH, "//button[contains(text(),'Retry Scenario')]")
    NEW_SCENARIO_BTN   = (By.XPATH, "//button[contains(text(),'New Scenario')]")
    COPY_REPORT_BTN    = (By.XPATH, "//button[contains(text(),'Copy Report') or contains(text(),'Copied')]")
    OVERALL_SCORE      = (By.CSS_SELECTOR, ".score-display")
    SECTION_STRENGTHS  = (By.XPATH, "//*[contains(text(),'Strengths') or contains(text(),'STRENGTHS')]")
    SECTION_GAPS       = (By.XPATH, "//*[contains(text(),'CRITICAL GAPS')]")
    BREADCRUMB         = (By.XPATH, "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONFIGURE')]")
    ANALYZING_BADGE    = (By.XPATH, "//*[contains(text(),'Analyzing Session')]")
    
    # Save Progress Form (Anonymous users only)
    WAITLIST_EMAIL_INPUT = (By.CSS_SELECTOR, "input[type='email']")
    WAITLIST_SUBMIT_BTN  = (By.XPATH, "//button[contains(text(),'Save Progress')]")
    WAITLIST_SUCCESS_MSG = (By.XPATH, "//*[contains(text(),'Progress saved')]")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def navigate(self, base_url):
        self.browser.navigate_to(f"{base_url}/labs/debrief")

    def wait_for_load(self, timeout=15):
        """Wait until the debrief screen structure is visible (may still be loading)."""
        WebDriverWait(self.driver, timeout).until(
            EC.any_of(
                EC.presence_of_element_located(self.ANALYZING_BADGE),
                EC.presence_of_element_located(self.OVERALL_SCORE),
                EC.presence_of_element_located(self.RETRY_BTN),
                EC.presence_of_element_located(self.WAITLIST_EMAIL_INPUT) # For Labs/Anonymous Debrief
            )
        )

    def wait_for_analysis(self, timeout=60):
        """Wait until the debrief score is rendered (analysis complete)."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.OVERALL_SCORE)
        )

    def get_overall_score_text(self):
        el = self.driver.find_element(*self.OVERALL_SCORE)
        return el.text.strip()

    def is_strengths_section_visible(self):
        try:
            return self.driver.find_element(*self.SECTION_STRENGTHS).is_displayed()
        except Exception:
            return False

    def is_gaps_section_visible(self):
        try:
            return self.driver.find_element(*self.SECTION_GAPS).is_displayed()
        except Exception:
            return False

    def click_retry(self):
        self.driver.find_element(*self.RETRY_BTN).click()

    def click_new_scenario(self):
        self.driver.find_element(*self.NEW_SCENARIO_BTN).click()

    def click_copy_report(self):
        self.driver.find_element(*self.COPY_REPORT_BTN).click()

    def click_breadcrumb_configure(self):
        el = self.driver.find_element(*self.BREADCRUMB)
        assert el.is_enabled(), "Configure breadcrumb should be clickable from debrief"
        el.click()

    # Anonymous User Waitlist flows
    def fill_waitlist_email(self, email):
        el = self.driver.find_element(*self.WAITLIST_EMAIL_INPUT)
        el.clear()
        el.send_keys(email)

    def submit_waitlist(self):
        self.driver.find_element(*self.WAITLIST_SUBMIT_BTN).click()

    def is_success_message_visible(self, timeout=10):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.WAITLIST_SUCCESS_MSG)
            )
            return True
        except Exception:
            return False
