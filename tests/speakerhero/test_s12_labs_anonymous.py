"""
S12-FLOW-01: Labs Anonymous Simulation Flow
============================================
BDD acceptance criteria for anonymous Labs sessions (Hard Conversations).

Validates the P0 fix: Labs simulations MUST work WITHOUT authentication.
The source='labs' flag in SimulationChat bypasses requireUser() in /api/simulate.

These tests run WITHOUT auth cookies — deliberately testing the anonymous path.
Any 401 or silent failure is a regression of the fix in commit 15d349d.

Run:
    pytest tests/speakerhero/test_s12_labs_anonymous.py --env=sales_sim_prod -v
"""

import time
import json
import pytest
import urllib.request
import urllib.error
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.sales_sim.sales_sim_pages import LabsPage, LabsPlayPage


@pytest.mark.labs
@pytest.mark.anonymous
class TestLabsLandingPage:
    """Labs landing page loads and displays scenarios without auth."""

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser + config. NO auth cookies — tests anonymous access."""
        self.browser  = browser
        self.config   = config
        self.base_url = config["url"]
        self.labs     = LabsPage(browser)

        # Clear any leftover cookies to ensure truly anonymous
        browser.navigate_to(self.base_url)
        browser.driver.delete_all_cookies()

    def test_labs_page_loads_without_auth(self):
        """
        GIVEN an anonymous user (no Supabase session cookies)
        WHEN they navigate to /labs
        THEN the Hard Conversations landing page loads with scenario cards
        """
        self.labs.navigate(self.base_url)
        assert self.labs.is_loaded(), \
            "Labs landing page should load without authentication"

    def test_labs_displays_at_least_four_scenarios(self):
        """
        GIVEN the /labs page is loaded
        WHEN checking the scenario cards
        THEN at least 4 scenarios are visible (Raise, Car, Burnout, Decline)
        """
        self.labs.navigate(self.base_url)
        self.labs.wait_for_load()
        count = self.labs.get_scenario_count()
        assert count >= 4, \
            f"Expected at least 4 scenario cards, found {count}"

    def test_labs_hero_heading_present(self):
        """
        GIVEN the /labs page is loaded
        WHEN checking the hero section
        THEN a heading is visible with Hard Conversations branding
        """
        self.labs.navigate(self.base_url)
        self.labs.wait_for_load()
        heading = self.browser.driver.find_element(*self.labs.HERO_HEADING)
        assert heading.is_displayed(), "Hero heading should be visible"
        assert len(heading.text) > 10, "Hero heading should have meaningful content"


@pytest.mark.labs
@pytest.mark.anonymous
@pytest.mark.slow
class TestLabsRaiseSimulation:
    """
    S12-FLOW-01 AC: GIVEN /labs, WHEN I click 'Ask for a Raise',
    THEN the Labs simulation starts and the prospect delivers an opening message.

    This is the critical regression test for the P0 auth bypass fix.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser + config. NO auth cookies — anonymous access."""
        self.browser   = browser
        self.config    = config
        self.base_url  = config["url"]
        self.labs      = LabsPage(browser)
        self.play      = LabsPlayPage(browser)

        # Clear any leftover cookies to ensure truly anonymous
        browser.navigate_to(self.base_url)
        browser.driver.delete_all_cookies()

    def test_raise_scenario_navigates_to_play(self):
        """
        GIVEN the /labs page
        WHEN I click 'Ask for a Raise'
        THEN the browser navigates to /labs/play with scenario=raise-standard
        """
        self.labs.navigate(self.base_url)
        self.labs.wait_for_load()
        self.labs.click_raise_scenario()

        WebDriverWait(self.browser.driver, 15).until(
            EC.url_contains("/labs/play")
        )
        assert "scenario=raise" in self.browser.driver.current_url, \
            "URL should contain the raise scenario parameter"

    def test_raise_simulation_shows_connecting_state(self):
        """
        GIVEN I've navigated to /labs/play for the raise scenario
        WHEN the page loads
        THEN the 'CONNECTING...' state is shown initially
        AND the chat input is present
        """
        self.browser.navigate_to(f"{self.base_url}/labs/play?scenario=raise-standard")
        self.play.wait_for_load(timeout=30)

        # Input should be present even while connecting
        assert self.browser.driver.find_element(*self.play.SIM_INPUT).is_displayed(), \
            "Chat input should be visible on play page"

    def test_raise_ai_opening_message_arrives(self):
        """
        GIVEN a Labs 'Ask for a Raise' simulation started anonymously
        WHEN waiting up to 90 seconds
        THEN the AI prospect (Jordan Reyes) delivers an opening message
        AND the 'CONNECTING...' text is no longer visible

        CRITICAL: This was the P0 bug — requireUser() blocked anonymous
        /api/simulate calls. Fix: source='labs' bypasses auth.
        """
        # Navigate directly — avoids session-scoped browser state drift
        self.browser.navigate_to(f"{self.base_url}/labs/play?scenario=raise-standard")
        self.play.wait_for_load(timeout=30)

        # Wait for the AI to deliver its opening message
        opened = self.play.wait_for_opening_message(timeout=90)
        assert opened, \
            "AI prospect should deliver opening message within 90s (P0 auth bypass regression)"

        # CONNECTING label should have disappeared
        assert not self.play.is_connecting(), \
            "CONNECTING state should clear after opening message arrives"

        # Verify it's a real message (not empty)
        msg = self.play.get_last_assistant_message()
        assert len(msg) > 10, \
            f"Opening message should be substantive, got: '{msg[:50]}...'"

    def test_raise_chat_round_trip(self):
        """
        GIVEN the AI prospect has delivered an opening message (anonymously)
        WHEN the user sends a message
        THEN the AI responds with a new message
        AND the input re-enables for the next turn

        Validates the full anonymous chat loop, not just the opening.
        """
        # Navigate directly to avoid state contamination
        self.browser.navigate_to(f"{self.base_url}/labs/play?scenario=raise-standard")
        self.play.wait_for_load(timeout=30)

        # Wait for opening
        opened = self.play.wait_for_opening_message(timeout=90)
        if not opened:
            pytest.skip("Opening message did not arrive — cannot test round-trip")

        initial_count = self.play.get_message_count()

        # Send a user message
        self.play.send_message("I wanted to talk about my compensation.")

        # Wait for AI response
        responded = self.play.wait_for_response(initial_count, timeout=60)
        assert responded, \
            "AI should respond to user message in anonymous Labs session"

        # Input should re-enable
        time.sleep(1)  # Brief settle
        assert self.play.is_input_enabled(), \
            "Chat input should re-enable after AI response"


@pytest.mark.labs
@pytest.mark.anonymous
@pytest.mark.slow
class TestLabsCarNegotiationSimulation:
    """
    S12-FLOW-01 AC: GIVEN /labs, WHEN I click 'Negotiate a Car Purchase',
    THEN the Labs simulation starts and reaches a state where the user can respond.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser + config. NO auth cookies — anonymous access."""
        self.browser   = browser
        self.config    = config
        self.base_url  = config["url"]
        self.labs      = LabsPage(browser)
        self.play      = LabsPlayPage(browser)

        # Clear any leftover cookies to ensure truly anonymous
        browser.navigate_to(self.base_url)
        browser.driver.delete_all_cookies()

    def test_car_scenario_navigates_to_play(self):
        """
        GIVEN the /labs page
        WHEN I click 'Negotiate a Car Purchase'
        THEN the browser navigates to /labs/play with the car scenario param
        """
        self.labs.navigate(self.base_url)
        self.labs.wait_for_load()
        self.labs.click_car_scenario()

        WebDriverWait(self.browser.driver, 15).until(
            EC.url_contains("/labs/play")
        )
        assert "scenario=cn-scenario" in self.browser.driver.current_url, \
            "URL should contain the car negotiation scenario parameter"

    def test_car_ai_opening_message_arrives(self):
        """
        GIVEN a Labs 'Negotiate a Car Purchase' simulation started anonymously
        WHEN waiting up to 90 seconds
        THEN the Car Dealership Sales Manager delivers an opening message
        AND the CONNECTING state clears
        """
        self.browser.navigate_to(f"{self.base_url}/labs/play?scenario=cn-scenario-test-drive")
        self.play.wait_for_load(timeout=30)

        opened = self.play.wait_for_opening_message(timeout=90)
        assert opened, \
            "Car scenario AI should deliver opening message within 90s"

        msg = self.play.get_last_assistant_message()
        assert len(msg) > 10, \
            f"Opening message should be substantive, got: '{msg[:50]}...'"


@pytest.mark.labs
@pytest.mark.anonymous
class TestLabsNoAuthRegression:
    """
    Regression guard: Labs must NEVER require authentication.
    These tests explicitly verify no auth-related errors appear.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Wire browser + config. NO auth cookies — anonymous access."""
        self.browser   = browser
        self.config    = config
        self.base_url  = config["url"]

        # Clear any leftover cookies to ensure truly anonymous
        browser.navigate_to(self.base_url)
        browser.driver.delete_all_cookies()

    def test_no_auth_redirect_on_labs(self):
        """
        GIVEN no auth cookies are set
        WHEN navigating to /labs
        THEN the browser does NOT redirect to /auth/login
        """
        self.browser.navigate_to(f"{self.base_url}/labs")
        time.sleep(3)  # Allow any redirect to complete
        assert "/auth/" not in self.browser.driver.current_url, \
            "Labs page should NOT redirect to login"

    def test_no_auth_redirect_on_labs_play(self):
        """
        GIVEN no auth cookies are set
        WHEN navigating directly to /labs/play?scenario=raise-standard
        THEN the browser does NOT redirect to /auth/login
        AND the page stays on /labs/play
        """
        self.browser.navigate_to(f"{self.base_url}/labs/play?scenario=raise-standard")
        time.sleep(5)  # Allow Next.js Suspense hydration to complete
        assert "/auth/" not in self.browser.driver.current_url, \
            "Labs play page should NOT redirect to login"
        assert "/labs/play" in self.browser.driver.current_url, \
            "Browser should remain on /labs/play"

    def test_labs_play_renders_simulation_ui(self):
        """
        GIVEN /labs/play loaded without auth
        WHEN the Suspense boundary hydrates
        THEN the simulation chat input renders
        """
        self.browser.navigate_to(f"{self.base_url}/labs/play?scenario=raise-standard")
        # Next.js Suspense + client hydration can take 10-15s in headless Chrome
        for _ in range(30):  # Poll for 15 seconds
            time.sleep(0.5)
            has_input = self.browser.driver.execute_script(
                "return !!document.querySelector('#simulation-input, [placeholder*=\"Reply\"], input[type=\"text\"]')"
            )
            if has_input:
                break
        assert has_input, "Simulation chat input should render without auth"

    def test_no_error_toast_on_anonymous_opening(self):
        """
        GIVEN an anonymous Labs session starts
        WHEN the opening message request fires
        THEN no error toast appears (e.g., 'Could not connect to the simulation')

        This catches the specific failure mode where requireUser() throws a 401
        and SimulationChat shows a toast error instead of the opening message.
        """
        self.browser.navigate_to(f"{self.base_url}/labs/play?scenario=raise-standard")
        time.sleep(5)  # Allow opening request to fire and potentially fail

        # Check for error toast elements
        error_toasts = self.browser.driver.find_elements(
            By.XPATH, "//*[contains(text(),'Could not connect')]"
        )
        assert len(error_toasts) == 0, \
            "No 'Could not connect' error toast should appear for anonymous Labs sessions"

    def test_api_returns_non_401_for_labs_source(self):
        """
        GIVEN no auth cookies or session
        WHEN POSTing to /api/simulate with source='labs'
        THEN the API does NOT return 401 (it may return 500 for LLM errors, but never 401)

        This is the most important regression test for the P0 fix.
        It verifies the auth bypass at the API level, independent of the UI.
        """
        url = f"{self.base_url}/api/simulate"
        payload = json.dumps({
            "messages": [{"role": "user", "content": "Hello"}],
            "sessionId": "selenium-auth-test",
            "config": {
                "selectedProfile": {
                    "name": "Test", "title": "Test", "company": "Test",
                    "industry": "Test", "backstory": "Test",
                    "personalityTraits": ["assertive"],
                    "physicalDescription": "Test"
                },
                "subject": {"config": {"condition": "manager", "conditionLevel": "your-manager", "name": "Test"}},
                "scenario": {"config": {"name": "test", "context": "test"}},
                "training": {"config": {"targetRole": "IC"}},
                "distance": 5, "temperature": 5
            },
            "isOpening": False,
            "source": "labs"
        }).encode('utf-8')

        req = urllib.request.Request(
            url, data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        try:
            resp = urllib.request.urlopen(req)
            status = resp.getcode()
        except urllib.error.HTTPError as e:
            status = e.code

        assert status != 401, \
            f"API should not return 401 for source='labs' — got {status}"

    def test_api_returns_401_for_app_source_without_auth(self):
        """
        GIVEN no auth cookies or session
        WHEN POSTing to /api/simulate with source='app'
        THEN the API returns 401 (authenticated path should enforce auth)

        Counter-test: verifies that auth is still enforced for regular app users.
        """
        url = f"{self.base_url}/api/simulate"
        payload = json.dumps({
            "messages": [{"role": "user", "content": "Hello"}],
            "sessionId": "selenium-auth-test-app",
            "config": {
                "selectedProfile": {
                    "name": "Test", "title": "Test", "company": "Test",
                    "industry": "Test", "backstory": "Test",
                    "personalityTraits": ["assertive"],
                    "physicalDescription": "Test"
                },
                "subject": {"config": {"condition": "manager", "conditionLevel": "your-manager", "name": "Test"}},
                "scenario": {"config": {"name": "test", "context": "test"}},
                "training": {"config": {"targetRole": "IC"}},
                "distance": 5, "temperature": 5
            },
            "isOpening": False,
            "source": "app"
        }).encode('utf-8')

        req = urllib.request.Request(
            url, data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        try:
            resp = urllib.request.urlopen(req)
            status = resp.getcode()
        except urllib.error.HTTPError as e:
            status = e.code

        assert status == 401, \
            f"API should return 401 for source='app' without auth — got {status}"
