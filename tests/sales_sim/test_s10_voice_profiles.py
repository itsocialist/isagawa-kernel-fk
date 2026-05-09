"""
S10-VOICE-01 — Voice Profile Mapping BDD Tests
==============================================
Tests the Admin UI for natively mapping Voice IDs to stakeholder archetypes.
"""

import os
import json
import pytest
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from resources.utilities import autologger

class TestVoiceProfilesBDD:
    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        """Standard auth injection setup."""
        self.browser  = browser
        self.config   = config
        self.base_url = config["url"]

        browser.navigate_to(self.base_url)
        browser.driver.delete_all_cookies()

        raw_cookies = os.environ.get("SPEAKERHERO_COOKIES", "")
        if not raw_cookies:
            cache_path = os.path.expanduser("~/.speakerhero_cookies.json")
            if os.path.exists(cache_path):
                try:
                    cache_data = json.loads(open(cache_path).read())
                    raw_cookies = json.dumps(cache_data.get("cookies", []))
                except Exception:
                    pass

        if raw_cookies:
            try:
                is_https = self.base_url.startswith("https://")
                from urllib.parse import urlparse
                host = urlparse(self.base_url).hostname  # e.g. speakerhero.app
                for cookie in json.loads(raw_cookies):
                    browser.driver.add_cookie({
                        "name":     cookie["name"],
                        "value":    cookie["value"],
                        "domain":   host,
                        "path":     cookie.get("path", "/"),
                        "secure":   is_https,
                        "httpOnly": cookie.get("httpOnly", False),
                    })
            except (json.JSONDecodeError, KeyError) as e:
                pytest.skip(f"SPEAKERHERO_COOKIES malformed — {e}")

            # Reload to let Supabase client pick up the injected cookies
            browser.navigate_to(self.base_url)
            time.sleep(3)  # allow React/Supabase auth to hydrate


    def _skip_if_no_auth(self):
        if "/auth/login" in self.browser.driver.current_url:
            pytest.skip("Auth required — run via grab_cookies.py")

    @autologger.automation_logger("Test")
    def test_given_site_admin_when_navigating_to_voices_tab_then_can_update_voice_mapping(self):
        """
        Scenario: Site Admin updates a Voice ID mapping natively in the UI
        
        Given the user is authenticated as a Site Admin
        When the user navigates to the Admin Panel and selects the 'Voices' tab
        Then the user should see a list of stakeholder archetypes
        And when the user updates the ElevenLabs Voice ID for 'Economic Buyer'
        Then the system should save the new mapping successfully
        """
        # Given the user is authenticated as a Site Admin
        self._skip_if_no_auth()
        
        # When the user navigates to the Admin Panel and selects the 'Voices' tab
        self.browser.navigate_to(self.base_url + "/admin?tab=voices")
        
        # Wait for the Voices tab content to load (allow time for React/Supabase auth hydration)
        try:
            WebDriverWait(self.browser.driver, 15).until(
                EC.text_to_be_present_in_element((By.TAG_NAME, "h2"), "Voice Profile Mapping")
            )
        except Exception as e:
            current_url = self.browser.driver.current_url
            body_text = self.browser.driver.find_element(By.TAG_NAME, "body").text[:300]
            pytest.fail(
                f"Voices tab did not render 'Voice Profile Mapping' heading.\n"
                f"URL: {current_url}\nPage: {body_text}"
            )


        # Then the user should see a list of stakeholder archetypes
        rows = self.browser.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
        assert len(rows) > 0, "No voice profile rows found in the table."

        # And when the user updates the ElevenLabs Voice ID for 'Economic Buyer'
        economic_buyer_row = None
        for row in rows:
            if "Economic Buyer" in row.text:
                economic_buyer_row = row
                break
        
        assert economic_buyer_row is not None, "Could not find 'Economic Buyer' in the voices table."

        # Find the edit button and click it
        edit_btn = economic_buyer_row.find_element(By.XPATH, ".//button[contains(text(), 'Edit')]")
        edit_btn.click()

        # Wait for the modal/input to appear
        input_field = WebDriverWait(self.browser.driver, 5).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='elevenlabsVoiceId']"))
        )
        
        # Modify the ID (append a suffix for testing)
        input_field.clear()
        input_field.send_keys("test_voice_id_123")

        # Save the changes
        save_btn = self.browser.driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()

        # Then the system should save the new mapping successfully
        # Note: Production currently does not mount ToastContainer in this component,
        # so we wait for the table to refresh and display the new Voice ID instead.
        updated_text = WebDriverWait(self.browser.driver, 10).until(
            EC.text_to_be_present_in_element(
                (By.XPATH, f"//tr[contains(., 'Economic Buyer')]//span"),
                "test_voice_id_123"
            )
        )
        assert updated_text is True, "The updated Voice ID did not appear in the table after saving."
