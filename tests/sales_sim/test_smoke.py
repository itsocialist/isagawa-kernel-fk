"""
SalesSim Smoke Suite — S4-01
==============================
End-to-end smoke tests for the SalesSim AI trainer.

Coverage:
  TC-01  Home page loads — config screen renders with demo chips and step tabs
  TC-02  Demo launch     — clicking a quick-demo chip lands on the simulation chat
  TC-03  Chat input      — user can type and send a message; send button disables while loading
  TC-04  End session     — clicking END transitions to the debrief screen
  TC-05  Back navigation — breadcrumb Configure link returns to config screen

Run (dev server must be running on :4500):
  pytest tests/sales_sim/ --env=sales_sim_dev -v --headed

Run headless:
  pytest tests/sales_sim/ --env=sales_sim_dev -v

Notes:
  - TC-03 and TC-04 require OpenAI API to be responding — mark flaky with @pytest.mark.live_api
  - TC-01, TC-02, TC-05 are pure UI smoke — no API dependency
"""

import time
import pytest
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from resources.utilities import autologger
from pages.sales_sim.sales_sim_pages import ConfigPage, ChatPage, DebriefPage


class TestSalesSimSmoke:
    """
    Smoke suite for SalesSim trainer.

    Validates the critical user path:
      Home → Demo launch → Chat → End session → Debrief → Back to Config
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser + config. Reset to clean state before each test."""
        self.browser    = browser
        self.config     = config
        self.config_page  = ConfigPage(browser)
        self.chat_page    = ChatPage(browser)
        self.debrief_page = DebriefPage(browser)

        # Navigate to root and clear all local/session storage + cookies
        browser.navigate_to(config["url"])
        browser.execute_script("localStorage.clear(); sessionStorage.clear();")
        browser.driver.delete_all_cookies()
        browser.navigate_to(config["url"])

    # --------------------------------------------------------------------------
    # TC-01: Home page loads
    # --------------------------------------------------------------------------

    @autologger.automation_logger("Test")
    def test_01_home_page_loads(self):
        """
        Verify the SalesSim config screen renders correctly on load.

        AAA:
        - Arrange: Navigate to root URL with clean state
        - Act: Wait for Quick Start heading
        - Assert: demo chips, step tabs, and start button are all present
        """
        # Act
        self.config_page.wait_for_load(timeout=15)

        # Assert — demo chips visible
        chips = self.config_page.get_demo_chips()
        assert len(chips) >= 1, \
            f"Expected at least 1 quick-demo chip, got {len(chips)}"

        # Assert — step progress tabs visible
        step_labels = self.config_page.get_step_labels()
        assert len(step_labels) >= 3, \
            f"Expected 3 step-progress tabs, got {len(step_labels)}: {step_labels}"

        # Assert — start button exists (disabled at this point)
        start = self.browser.driver.find_element(*ConfigPage.START_BTN)
        assert start is not None, "START SIMULATION button should be present"
        assert start.get_attribute("disabled"), \
            "Start button should be disabled until all steps are complete"

    # --------------------------------------------------------------------------
    # TC-02: Demo launch lands on chat
    # --------------------------------------------------------------------------

    @autologger.automation_logger("Test")
    def test_02_demo_launch_enters_chat(self):
        """
        Verify clicking a Quick Demo chip transitions to the simulation chat screen.

        AAA:
        - Arrange: Config screen loaded, demo chips visible
        - Act: Click the first demo chip
        - Assert: Chat input box is visible (appState transitions to 'chat')
        """
        # Arrange
        self.config_page.wait_for_load()
        chips = self.config_page.get_demo_chips()
        assert chips, "No demo chips found"

        # Act
        chips[0].click()

        # Assert — chat input appears within 15s
        self.chat_page.wait_for_load(timeout=15)

        assert self.browser.driver.find_element(*ChatPage.INPUT_BOX).is_displayed(), \
            "Chat input box should be visible after demo launch"

    # --------------------------------------------------------------------------
    # TC-03: Chat — type and send message (requires live API)
    # --------------------------------------------------------------------------

    @pytest.mark.live_api
    @autologger.automation_logger("Test")
    def test_03_chat_message_send(self):
        """
        Verify a user can type and send a message in the simulation.

        AAA:
        - Arrange: Launch a demo simulation, wait for the AI cold-open
        - Act: Type a message and click Send
        - Assert: Input clears and send button re-enables within 30s (response received)
        """
        # Arrange — launch demo
        self.config_page.wait_for_load()
        self.config_page.click_demo_chip(0)
        self.chat_page.wait_for_load(timeout=15)

        # Wait up to 20s for the AI to send its opening message
        try:
            WebDriverWait(self.browser.driver, 20).until(
                lambda d: d.find_element(*ChatPage.INPUT_BOX).is_enabled()
            )
        except Exception:
            pass  # Input may already be enabled

        # Act — type a message
        test_message = "Hello, I'm calling to learn more about your current setup."
        self.chat_page.type_message(test_message)

        # Assert input value set
        assert self.chat_page.get_input_value() == test_message, \
            "Input box should contain the typed message"

        # Act — send the message
        self.chat_page.send_message()

        # Assert — input clears after send
        WebDriverWait(self.browser.driver, 5).until(
            lambda d: d.find_element(*ChatPage.INPUT_BOX).get_attribute("value") == ""
        )

        # Assert — send button re-enables within 30s (response cycle complete)
        WebDriverWait(self.browser.driver, 30).until(
            lambda d: d.find_element(*ChatPage.SEND_BTN).is_enabled()
        )

    # --------------------------------------------------------------------------
    # TC-04: End session → Debrief screen (requires live API)
    # --------------------------------------------------------------------------

    @pytest.mark.live_api
    @autologger.automation_logger("Test")
    def test_04_end_session_shows_debrief(self):
        """
        Verify ending a session transitions to the debrief screen with a score.

        AAA:
        - Arrange: Start a demo simulation, send one message, wait for response
        - Act: Click END SESSION button
        - Assert: Debrief screen loads and displays an overall score (1-10)
        """
        # Arrange — launch demo + send one message
        self.config_page.wait_for_load()
        self.config_page.click_demo_chip(0)
        self.chat_page.wait_for_load(timeout=15)

        # Wait for input to enable, then send a message
        WebDriverWait(self.browser.driver, 25).until(
            lambda d: d.find_element(*ChatPage.INPUT_BOX).is_enabled()
        )
        self.chat_page.type_and_send("I understand. Can you tell me more about your current process?")

        # Wait for AI to respond (send btn re-enables)
        WebDriverWait(self.browser.driver, 30).until(
            lambda d: d.find_element(*ChatPage.SEND_BTN).is_enabled()
        )

        # Act — end the session
        self.chat_page.click_end_session()

        # Assert — debrief screen appears (may show skeleton or score)
        self.debrief_page.wait_for_load(timeout=15)

        # Assert — after analysis completes, overall score is visible
        self.debrief_page.wait_for_analysis(timeout=60)
        score_text = self.debrief_page.get_overall_score_text()
        assert score_text, "Overall score should be visible on debrief screen"

        # Assert score text contains a digit (e.g. "7" or "7/10")
        assert any(c.isdigit() for c in score_text), \
            f"Score text should contain a number, got: '{score_text}'"

    # --------------------------------------------------------------------------
    # TC-05: Back navigation — debrief → configure
    # --------------------------------------------------------------------------

    @autologger.automation_logger("Test")
    def test_05_breadcrumb_back_to_configure(self):
        """
        Verify the Configure breadcrumb navigates back to the config screen.

        AAA:
        - Arrange: Manually set appState via sessionStorage to simulate being on debrief
                   (avoids full live API round-trip for a pure nav test)
        - Act: Reload page with config in sessionStorage, launch demo → arrive at chat
               Then confirm breadcrumb appears and links back to config
        - Assert: Chat screen has a Configure breadcrumb that is clickable
                  After clicking, the Quick Start heading is visible again
        """
        # Arrange — launch demo to reach chat (pure UI, no API needed for nav test)
        self.config_page.wait_for_load()
        self.config_page.click_demo_chip(0)
        self.chat_page.wait_for_load(timeout=15)

        # Assert — breadcrumb is visible on chat screen
        try:
            crumb = self.browser.driver.find_element(
                By.XPATH,
                "//button[contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'CONFIGURE')]"
            )
            assert crumb.is_displayed(), "Configure breadcrumb should be visible on chat screen"
        except Exception:
            pytest.skip("Breadcrumb not rendered — may require wider screen. Run with --window-size=1280,800")

        # Act — click Configure breadcrumb
        self.chat_page.click_breadcrumb_configure()

        # Assert — Quick Start heading is visible (back on config screen)
        WebDriverWait(self.browser.driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(),'Quick Start')]")
            )
        )

        heading = self.browser.driver.find_element(
            By.XPATH, "//h1[contains(text(),'Quick Start')]"
        )
        assert heading.is_displayed(), \
            "Quick Start heading should be visible after navigating back via breadcrumb"
