"""
GameBoardPage - CIQ Jeopardy in-game board and question display.

Locator notes: no IDs on elements. Uses CSS classes and text-based XPath.
"""

from selenium.webdriver.common.by import By
from resources.utilities import autologger


class GameBoardPage:
    """
    Page Object for the in-game board view and question overlay.
    """

    # Header / Controls
    GAME_HEADER    = (By.CSS_SELECTOR, ".game-header, [class*='game-header'], header")
    CONTROLS_BTN   = (By.XPATH, "//button[contains(text(),'Control')]")

    # Board
    BOARD_CELL     = (By.CSS_SELECTOR, ".board-cell:not(.revealed), [class*='cell']:not([class*='revealed'])")

    # Question overlay
    QUESTION_DISPLAY = (By.CSS_SELECTOR, ".question-display, [class*='question-display']")
    QUESTION_TEXT    = (By.CSS_SELECTOR, ".question-text, [class*='clue'], [class*='question-text']")

    # Judge controls
    REVEAL_BTN    = (By.XPATH, "//button[contains(text(),'Reveal')]")
    CORRECT_BTN   = (By.XPATH, "//button[contains(text(),'Correct') or contains(text(),'✓')]")
    INCORRECT_BTN = (By.XPATH, "//button[contains(text(),'Wrong') or contains(text(),'✗') or contains(text(),'Incorrect')]")
    RETURN_BTN    = (By.XPATH, "//button[contains(text(),'Back') or contains(text(),'Return') or contains(text(),'Board')]")

    # Buzz / Timer
    BUZZ_INDICATOR = (By.CSS_SELECTOR, "[class*='buzz'], [class*='buzzed']")
    TIMER_BAR      = (By.CSS_SELECTOR, "[class*='timer'], [class*='countdown'], [style*='width']")

    # Answer
    ANSWER_TEXT    = (By.CSS_SELECTOR, "[class*='answer'], .answer-text")

    # No-buzz banner
    NO_BUZZ_BANNER = (By.XPATH, "//*[contains(text(),'No buzz') or contains(text(),'no buzz') or contains(text(),'nobody buzzed')]")

    def __init__(self, browser):
        self.browser = browser

    # ── Actions ───────────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def click_controls_button(self):
        """Click the persistent Controls button."""
        self.browser.click(*self.CONTROLS_BTN)

    @autologger.automation_logger("Page")
    def click_first_available_cell(self):
        """Click the first unrevealed question cell."""
        self.browser.click(*self.BOARD_CELL)

    @autologger.automation_logger("Page")
    def click_reveal(self):
        self.browser.click(*self.REVEAL_BTN)

    @autologger.automation_logger("Page")
    def click_correct(self):
        self.browser.click(*self.CORRECT_BTN)

    @autologger.automation_logger("Page")
    def click_incorrect(self):
        self.browser.click(*self.INCORRECT_BTN)

    @autologger.automation_logger("Page")
    def click_return_to_board(self):
        self.browser.click(*self.RETURN_BTN)

    # ── State checks ─────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def is_game_board_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.GAME_HEADER)

    @autologger.automation_logger("Page")
    def is_question_display_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.QUESTION_DISPLAY)

    @autologger.automation_logger("Page")
    def is_controls_button_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.CONTROLS_BTN)

    @autologger.automation_logger("Page")
    def is_buzz_indicator_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.BUZZ_INDICATOR)

    @autologger.automation_logger("Page")
    def is_answer_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.ANSWER_TEXT)

    @autologger.automation_logger("Page")
    def is_no_buzz_banner_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.NO_BUZZ_BANNER)

    @autologger.automation_logger("Page")
    def is_daily_double_ui_present(self) -> bool:
        """Return True if any Daily Double UI is visible in page source."""
        source = self.browser.get_page_source()
        return "daily-double" in source.lower() or "DAILY DOUBLE" in source
