"""
SpeakerHero E2E Regression — Labs Consumer Scenarios
Sprint: S11
Stories: S11-B2C-01

BDD Acceptance Criteria:
- GIVEN an anonymous user visits /labs, WHEN they select "Negotiate a Car Purchase", THEN the simulation starts with Mike Santos persona
- GIVEN a user is in a car negotiation session, WHEN the dealer uses anchoring/time pressure tactics, THEN the simulation stays in character
- GIVEN a user completes a car negotiation session, WHEN they reach debrief, THEN scoring uses the car-buying rubric (preparation, anchoring, composure, walk_away_power, deal_quality)
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://speakerhero.app"


class TestLabsCarNegotiation:
    """S11-B2C-01: Negotiate a Car Purchase — consumer Labs scenario."""

    def test_car_negotiation_card_visible_in_labs(self, driver):
        """GIVEN an anonymous user
        WHEN they navigate to /labs
        THEN they see a 'Negotiate a Car Purchase' scenario card"""
        driver.get(f"{BASE_URL}/labs")
        wait = WebDriverWait(driver, 10)
        card = wait.until(EC.presence_of_element_located((By.ID, "labs-scenario-car-negotiation")))
        assert "Negotiate a Car Purchase" in card.text

    def test_car_negotiation_starts_simulation(self, driver):
        """GIVEN an anonymous user selects the car negotiation card
        WHEN they click to start
        THEN the simulation begins with Mike Santos persona context"""
        driver.get(f"{BASE_URL}/labs")
        wait = WebDriverWait(driver, 10)
        card = wait.until(EC.element_to_be_clickable((By.ID, "labs-scenario-car-negotiation")))
        card.click()
        
        # Verify we navigated to play page and loaded Mike Santos
        header = wait.until(EC.presence_of_element_located((By.TAG_NAME, "header")))
        assert "Mike Santos" in header.text
        assert "Test Drive" in header.text

    def test_car_negotiation_debrief_uses_correct_rubric(self, driver):
        """GIVEN a user completes a car negotiation session
        WHEN they reach the debrief screen
        THEN scoring dimensions include preparation, anchoring, composure, walk_away_power, deal_quality"""
        # Inject mock session data into sessionStorage
        driver.get(f"{BASE_URL}/labs")
        driver.execute_script("""
            sessionStorage.setItem('labs_scenario_key', 'cn-scenario-test-drive');
            sessionStorage.setItem('labs_session', JSON.stringify({
                scores: {
                    preparation: 85,
                    anchoring: 70,
                    composure: 90,
                    walk_away_power: 80,
                    deal_quality: 75
                },
                turnCount: 5
            }));
        """)
        driver.get(f"{BASE_URL}/labs/debrief")
        wait = WebDriverWait(driver, 10)
        
        body_text = wait.until(EC.presence_of_element_located((By.TAG_NAME, "main"))).text
        assert "Preparation" in body_text
        assert "Walk-Away Power" in body_text
        assert "Deal Quality" in body_text
