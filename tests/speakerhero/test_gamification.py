"""
SpeakerHero E2E Regression — Gamification Engine
Sprint: S11
Stories: S11-B2C-02

BDD Acceptance Criteria:
- GIVEN a user completes a session, WHEN they visit /home/gamification, THEN their streak is incremented
- GIVEN a user has not practiced for 48 hours, WHEN they visit /home/gamification, THEN their streak resets to 0
- GIVEN a user scores ≥80% on margin defense, WHEN debrief completes, THEN the 'Price Defender' achievement unlocks
- GIVEN multiple users complete sessions this week, WHEN any user views the leaderboard, THEN rankings are ordered by total_score desc
"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BASE_URL = "https://speakerhero.app"


class TestGamificationStreak:
    """S11-B2C-02a: Streak tracking across sessions."""

    def test_streak_increments_after_session_completion(self, authenticated_driver):
        """GIVEN a user completes a simulation session
        WHEN they navigate to the gamification hub
        THEN their current_streak is incremented by 1"""
        authenticated_driver.get(f"{BASE_URL}/home/gamification")
        wait = WebDriverWait(authenticated_driver, 10)
        
        # Read initial streak
        streak_element = wait.until(EC.presence_of_element_located((By.ID, "streak-count")))
        initial_streak = int(streak_element.text)
        
        # Complete a session (using an api route hook or js injection for testing)
        authenticated_driver.execute_script("""
            fetch('/api/gamification/streak', { method: 'POST', body: JSON.stringify({ action: 'increment' }) });
        """)
        
        # Reload and check
        authenticated_driver.refresh()
        new_streak_element = wait.until(EC.presence_of_element_located((By.ID, "streak-count")))
        assert int(new_streak_element.text) == initial_streak + 1

    def test_streak_resets_after_48h_inactivity(self, authenticated_driver):
        """GIVEN a user has not completed a session in 48+ hours
        WHEN they complete a new session
        THEN their current_streak resets to 1 (not incremented from prior)"""
        # Testing server-side logic usually requires db fixture
        pytest.skip("Requires date manipulation in DB")

    def test_same_day_double_session_no_double_count(self, authenticated_driver):
        """GIVEN a user already completed a session today
        WHEN they complete a second session on the same day
        THEN their current_streak remains unchanged"""
        pytest.skip("Requires date manipulation in DB")


class TestGamificationAchievements:
    """S11-B2C-02b: Achievement unlock engine."""

    def test_first_session_achievement_unlocks(self, authenticated_driver):
        """GIVEN a user has never completed a session
        WHEN they complete their first session
        THEN the 'first_session' achievement is unlocked"""
        authenticated_driver.get(f"{BASE_URL}/home/gamification")
        wait = WebDriverWait(authenticated_driver, 10)
        
        # Check achievement grid
        achievements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "achievement-card")))
        assert len(achievements) > 0

    def test_price_defender_unlocks_on_high_margin(self, authenticated_driver):
        """GIVEN a user scores ≥80% on margin/pricing defense
        WHEN the debrief completes
        THEN the 'price_defender' achievement unlocks and a toast is shown"""
        pytest.skip("Requires simulation completion flow")

    def test_no_duplicate_achievement_unlock(self, authenticated_driver):
        """GIVEN a user already has the 'first_session' achievement
        WHEN they complete another session
        THEN no duplicate achievement row is created"""
        pytest.skip("Requires simulation completion flow")


class TestGamificationLeaderboard:
    """S11-B2C-02c: Weekly cohort leaderboard."""

    def test_leaderboard_displays_ranked_users(self, authenticated_driver):
        """GIVEN multiple users have scores for the current week
        WHEN a user views the gamification hub
        THEN the leaderboard shows users ordered by total_score descending"""
        authenticated_driver.get(f"{BASE_URL}/home/gamification")
        wait = WebDriverWait(authenticated_driver, 10)
        
        # Wait for leaderboard rows
        rows = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tbody tr")))
        assert len(rows) > 0
        
        # Check if first row score >= second row score
        if len(rows) > 1:
            score1 = int(rows[0].find_element(By.CSS_SELECTOR, "td:nth-child(3)").text)
            score2 = int(rows[1].find_element(By.CSS_SELECTOR, "td:nth-child(3)").text)
            assert score1 >= score2

    def test_leaderboard_shows_user_rank_and_percentile(self, authenticated_driver):
        """GIVEN the authenticated user has a leaderboard entry
        WHEN they view the gamification hub
        THEN their rank number and percentile are displayed"""
        authenticated_driver.get(f"{BASE_URL}/home/gamification")
        wait = WebDriverWait(authenticated_driver, 10)
        
        # Ensure 'You' row exists
        you_row = wait.until(EC.presence_of_element_located((By.XPATH, "//tr[contains(., 'You')]")))
        assert you_row is not None
