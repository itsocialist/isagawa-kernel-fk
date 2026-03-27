"""
PlayerRole - CIQ Jeopardy player persona.

Composes PlayerPage actions into full workflow steps.
"""

import time
from resources.utilities import autologger
from pages.ciq_jeopardy.player_page import PlayerPage


class PlayerRole:
    """
    Represents a player joining and participating in a CIQ Jeopardy game.

    Composes high-level player actions from PlayerPage interactions.
    """

    def __init__(self, browser, name: str = "TestPlayer"):
        self.browser = browser
        self.name = name
        self.player_page = PlayerPage(browser)

    @autologger.automation_logger("Role")
    def join_game(self, room_code: str, player_name: str = None) -> bool:
        """
        Full join flow: navigate → name → code → submit.

        Args:
            room_code: 4-char room code from the host waiting room
            player_name: Display name (defaults to self.name)

        Returns:
            True if successfully joined (in-game state confirmed)
        """
        name = player_name or self.name
        self.player_page.navigate()
        time.sleep(0.5)

        self.player_page.enter_name(name)
        self.player_page.enter_room_code(room_code)
        self.player_page.click_join()
        time.sleep(1.5)  # socket handshake

        return self.player_page.is_in_game()

    @autologger.automation_logger("Role")
    def buzz_in(self) -> bool:
        """
        Buzz in on the current question.

        Returns:
            True if buzz button was visible and clicked
        """
        if self.player_page.is_buzz_button_visible():
            self.player_page.click_buzz()
            return True
        return False

    @autologger.automation_logger("Role")
    def get_score(self) -> str:
        """Return the player's current score as a string."""
        return self.player_page.get_player_score()
