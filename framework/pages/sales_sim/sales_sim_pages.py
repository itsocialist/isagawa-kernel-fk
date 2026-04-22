"""
SalesSim Page Objects
=====================
Page Object Model for the SalesSim trainer application.

Covers:
- ConfigPage     : Pack selector / quick-start screen
- ChatPage       : Simulation chat screen
- DebriefPage    : Post-session debrief screen

All waits use the BrowserInterface explicit_wait from config.
All element IDs are the stable `id` attributes set in the components.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ConfigPage:
    """
    Pack Selector / Quick-Start screen.
    URL: http://localhost:4500  (appState == 'select')
    """

    # Stable selectors — maps to id/class attributes set in PackSelector.tsx
    DEMO_CHIP             = (By.CSS_SELECTOR, "[id^='demo-']")
    STEP_PROGRESS         = (By.CSS_SELECTOR, ".flex button.flex-1")
    PRODUCT_CARD          = (By.CSS_SELECTOR, "button.w-full.p-4.text-left")
    PACK_LIBRARY_BTN      = (By.CSS_SELECTOR, "button.btn-secondary")
    START_BTN             = (By.CSS_SELECTOR, "button.btn-primary")
    LABEL_ACCENT          = (By.CSS_SELECTOR, ".label-accent")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def wait_for_load(self, timeout=15):
        """Wait until the Quick Start heading is visible."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(),'Quick Start')]"))
        )

    def get_demo_chips(self):
        """Return all Quick Demo chip buttons."""
        return self.driver.find_elements(*self.DEMO_CHIP)

    def click_demo_chip(self, index=0):
        """Click the nth quick-demo chip (launches a preset simulation)."""
        chips = self.get_demo_chips()
        assert chips, "No demo chips found on config page"
        chips[index].click()

    def get_step_labels(self):
        """Return text of the 3 step-progress buttons."""
        btns = self.driver.find_elements(*self.STEP_PROGRESS)
        return [b.text.strip() for b in btns if b.text.strip()]

    def select_first_product(self):
        """Click the first product card in the current step."""
        cards = self.driver.find_elements(*self.PRODUCT_CARD)
        assert cards, "No product cards found"
        cards[0].click()

    def is_start_button_enabled(self):
        btn = self.driver.find_element(*self.START_BTN)
        return btn.is_enabled() and "disabled" not in btn.get_attribute("class")

    def click_start(self):
        self.driver.find_element(*self.START_BTN).click()


class ChatPage:
    """
    Simulation Chat screen.
    URL: http://localhost:4500  (appState == 'chat')
    """

    INPUT_BOX        = (By.ID, "simulation-input")
    SEND_BTN         = (By.ID, "send-btn")
    VOICE_TOGGLE     = (By.ID, "voice-mode-toggle")
    END_BTN          = (By.XPATH, "//button[contains(text(),'END')]")
    CHAT_MESSAGES    = (By.CSS_SELECTOR, ".sim-message-bubble, [class*='message-bubble']")
    BREADCRUMB       = (By.CSS_SELECTOR, "button[style*='accent-primary']")
    TYPING_INDICATOR = (By.CSS_SELECTOR, "[class*='typing'], .typing-indicator")
    CONTEXT_BAR      = (By.CSS_SELECTOR, ".context-bar")
    CONNECTING_MSG   = (By.XPATH, "//*[contains(text(),'joining the call')]")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def wait_for_load(self, timeout=20):
        """Wait until the chat input box is visible."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.INPUT_BOX)
        )

    def wait_for_first_message(self, timeout=30):
        """Wait for at least one assistant message to appear (AI cold-open)."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(
                (By.XPATH, "//*[contains(@class,'sim-message') or contains(text(),'joining') or contains(@class,'chat')]")
            )
        )

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

    def is_send_disabled(self):
        btn = self.driver.find_element(*self.SEND_BTN)
        return not btn.is_enabled() or btn.get_attribute("disabled") == "true"

    def is_context_bar_visible(self):
        try:
            return self.driver.find_element(*self.CONTEXT_BAR).is_displayed()
        except Exception:
            return False

    def is_voice_toggle_visible(self):
        try:
            return self.driver.find_element(*self.VOICE_TOGGLE).is_displayed()
        except Exception:
            return False

    def click_end_session(self):
        self.driver.find_element(*self.END_BTN).click()

    def click_breadcrumb_configure(self):
        """Click the Configure breadcrumb to go back to pack selection."""
        crumbs = self.driver.find_elements(
            By.XPATH, "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONFIGURE')]"
        )
        for c in crumbs:
            if c.is_displayed():
                # Scroll into view + JS click to avoid element click intercept from overlay bar
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", c)
                self.driver.execute_script("arguments[0].click();", c)
                return
        raise AssertionError("Configure breadcrumb not found or not visible")


class DebriefPage:
    """
    Debrief screen — post-session scoring + analysis.
    URL: http://localhost:4500  (appState == 'debrief')
    """

    RETRY_BTN          = (By.XPATH, "//button[contains(text(),'Retry Scenario')]")
    NEW_SCENARIO_BTN   = (By.XPATH, "//button[contains(text(),'New Scenario')]")
    COPY_REPORT_BTN    = (By.XPATH, "//button[contains(text(),'Copy Report') or contains(text(),'Copied')]")
    OVERALL_SCORE      = (By.CSS_SELECTOR, ".score-display")
    SCORE_BARS         = (By.CSS_SELECTOR, ".sim-card .h-1\\.5")
    SECTION_STRENGTHS  = (By.XPATH, "//*[contains(text(),'Strengths') or contains(text(),'STRENGTHS')]")
    SECTION_GAPS       = (By.XPATH, "//*[contains(text(),'CRITICAL GAPS')]")
    BREADCRUMB         = (By.XPATH, "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONFIGURE')]")
    SKELETON           = (By.CSS_SELECTOR, "[style*='skeleton-shimmer'], [style*='background-position']")
    ANALYZING_BADGE    = (By.XPATH, "//*[contains(text(),'Analyzing Session')]")

    def __init__(self, browser):
        self.browser = browser
        self.driver  = browser.driver

    def wait_for_analysis(self, timeout=60):
        """Wait until the debrief score is rendered (analysis complete)."""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.OVERALL_SCORE)
        )

    def wait_for_load(self, timeout=15):
        """Wait until the debrief screen structure is visible (may still be loading)."""
        WebDriverWait(self.driver, timeout).until(
            EC.any_of(
                EC.presence_of_element_located(self.ANALYZING_BADGE),
                EC.presence_of_element_located(self.OVERALL_SCORE),
                EC.presence_of_element_located(self.RETRY_BTN),
            )
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
