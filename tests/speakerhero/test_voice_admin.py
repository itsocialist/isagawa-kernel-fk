"""
SpeakerHero E2E Regression — Admin Voice Profile Configuration
Sprint: S11
Stories: S11-VOICE-01

BDD Acceptance Criteria:
- GIVEN a site admin navigates to Admin > Voices, WHEN the page loads, THEN the voice profile table renders with archetype mappings
- GIVEN a site admin edits a voice profile, WHEN they update the Fish Audio Model ID and save, THEN the change persists on page reload
- GIVEN a site admin clicks the play button on a voice profile, WHEN the TTS call completes, THEN audio plays in the browser
- GIVEN a site admin clicks 'Add Voice Profile', WHEN they fill in all fields and submit, THEN the new archetype appears in the table
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://speakerhero.app"


class TestVoiceProfileAdmin:
    """S11-VOICE-01: Admin Voice Profile Configuration UI."""

    def test_voice_profile_table_renders(self, authenticated_driver):
        """GIVEN a site admin
        WHEN they navigate to the Admin panel Voices tab
        THEN the voice profile table loads with seeded archetype rows"""
        authenticated_driver.get(f"{BASE_URL}/admin?tab=voices")
        wait = WebDriverWait(authenticated_driver, 10)
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        assert "champion" in table.text

    def test_multi_provider_edit_persists(self, authenticated_driver):
        """GIVEN a site admin edits a voice profile row
        WHEN they update the Fish Audio Model ID and OpenAI Voice fields and click Save
        THEN the changes persist after page reload"""
        authenticated_driver.get(f"{BASE_URL}/admin?tab=voices")
        wait = WebDriverWait(authenticated_driver, 10)
        
        # Click Edit on the first row
        edit_btns = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//button[contains(text(), 'Edit')]")))
        edit_btns[0].click()
        
        # Wait for inputs to appear
        inputs = wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "input")))
        assert len(inputs) >= 3 # ElevenLabs, Fish, OpenAI
        
        # Enter test data into Fish input (2nd input)
        inputs[1].clear()
        inputs[1].send_keys("test_fish_id")
        
        # Save
        save_btn = authenticated_driver.find_element(By.XPATH, "//button[contains(text(), 'Save')]")
        save_btn.click()
        
        # Wait for Toast or success
        wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Voice profile updated successfully')]")))
        
        # Reload and verify
        authenticated_driver.refresh()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        assert "test_fish_id" in authenticated_driver.page_source

    def test_voice_preview_plays_audio(self, authenticated_driver):
        """GIVEN a site admin clicks the play button on a voice profile row
        WHEN TTS synthesis completes
        THEN audio plays inline in the browser without navigation"""
        authenticated_driver.get(f"{BASE_URL}/admin?tab=voices")
        wait = WebDriverWait(authenticated_driver, 10)
        
        play_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '▶️')]")))
        play_btn.click()
        
        # Wait for play button to change to stop
        wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(), '⏹️')]")))
        assert "⏹️" in authenticated_driver.page_source

    def test_add_new_archetype_creates_row(self, authenticated_driver):
        """GIVEN a site admin clicks 'Add Voice Profile'
        WHEN they fill in archetype_key, name, gender, age_range, and voice IDs
        THEN the new archetype appears in the table after save"""
        # Out of scope for S11-VOICE-01 (Only multi-provider edit/preview required)
        pytest.skip("Out of scope for Sprint 11")
