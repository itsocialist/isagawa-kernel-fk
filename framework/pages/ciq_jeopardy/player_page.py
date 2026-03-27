"""
PlayerPage - CIQ Jeopardy player join flow (/join).

Locator notes: no IDs — using CSS classes and text XPath.
Player join flow: enter name → enter room code → join → buzz-in.
"""

from selenium.webdriver.common.by import By
from resources.utilities import autologger


class PlayerPage:
    """
    Page Object for the player join screen (/join).

    Flow:
        1. navigate()        → /join
        2. enter_name()      → type display name
        3. enter_room_code() → type 4-char room code
        4. click_join()      → submit join form
        5. is_in_game()      → confirm joined (buzz button visible)
        6. click_buzz()      → buzz in on a question
    """

    # Join form
    NAME_INPUT      = (By.CSS_SELECTOR, "input[placeholder*='name'], input[placeholder*='Name'], input[type='text']")
    ROOM_CODE_INPUT = (By.CSS_SELECTOR, "input[placeholder*='code'], input[placeholder*='Code'], input[maxlength='4']")
    JOIN_BTN        = (By.XPATH, "//button[contains(text(),'Join')]")

    # In-game player view
    BUZZ_BTN        = (By.XPATH, "//button[contains(text(),'Buzz') or contains(text(),'BUZZ')]")
    WAITING_MSG     = (By.XPATH, "//*[contains(text(),'Waiting') or contains(text(),'waiting')]")
    PLAYER_SCORE    = (By.CSS_SELECTOR, "[class*='score'], [class*='player-score']")
    GAME_TITLE      = (By.CSS_SELECTOR, "h1, h2")

    # Join page heading
    JOIN_HEADING    = (By.XPATH, "//h1[contains(text(),'Join') or contains(text(),'Player')]")

    def __init__(self, browser):
        self.browser = browser

    # ── Navigation ────────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def navigate(self):
        """Navigate to the player join page."""
        self.browser.navigate_to(self.browser.config["url"] + "/join")

    # ── Actions ───────────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def enter_name(self, name: str):
        """Type the player display name."""
        self.browser.type_text(*self.NAME_INPUT, text=name)

    @autologger.automation_logger("Page")
    def enter_room_code(self, code: str):
        """Type the 4-char room code."""
        self.browser.type_text(*self.ROOM_CODE_INPUT, text=code.upper())

    @autologger.automation_logger("Page")
    def click_join(self):
        """Click the Join button."""
        self.browser.click(*self.JOIN_BTN)

    @autologger.automation_logger("Page")
    def click_buzz(self):
        """Click the Buzz button to buzz in on a question."""
        self.browser.click(*self.BUZZ_BTN)

    # ── State checks ─────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def is_join_page_loaded(self) -> bool:
        """Return True when the join form is on screen."""
        return self.browser.is_element_displayed(*self.JOIN_BTN)

    @autologger.automation_logger("Page")
    def is_in_game(self) -> bool:
        """Return True when the player is in-game (buzz button available or waiting msg)."""
        return (self.browser.is_element_displayed(*self.BUZZ_BTN) or
                self.browser.is_element_displayed(*self.WAITING_MSG))

    @autologger.automation_logger("Page")
    def is_buzz_button_visible(self) -> bool:
        """Return True when the Buzz button is interactable."""
        return self.browser.is_element_displayed(*self.BUZZ_BTN)

    @autologger.automation_logger("Page")
    def get_player_score(self) -> str:
        """Return the player's current displayed score text."""
        try:
            return self.browser.get_text(*self.PLAYER_SCORE).strip()
        except Exception:
            return "0"
