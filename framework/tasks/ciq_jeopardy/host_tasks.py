"""
HostTasks - CIQ Jeopardy host-side domain operations.

Each task performs exactly one domain operation.
Tasks coordinate across Page Objects but contain NO assertions.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pages.ciq_jeopardy.home_page import HomePage
from pages.ciq_jeopardy.host_setup_page import HostSetupPage
from pages.ciq_jeopardy.game_board_page import GameBoardPage
from resources.utilities import autologger


class HostTasks:
    """
    Domain tasks for the Jeopardy host persona.

    Tasks:
        navigate_to_home       - Load the landing page
        start_host_flow        - Navigate to /host setup
        select_question_pack   - Choose a pack from the dropdown
        start_game             - Click Start Game and enter waiting room
        advance_to_board       - (After player joins) confirm game started to board
        open_question          - Click the first available board cell
        reveal_answer          - Click Reveal Answer on question overlay
        judge_correct          - Click Correct
        judge_incorrect        - Click Wrong/Incorrect
        return_to_board        - Click Return to Board from question view
        open_host_controls     - Click the mid-game Controls button
    """

    def __init__(self, browser):
        self.browser = browser
        self.home_page = HomePage(browser)
        self.setup_page = HostSetupPage(browser)
        self.board_page = GameBoardPage(browser)

    @autologger.automation_logger("Task")
    def navigate_to_home(self):
        """Navigate to the CIQ Jeopardy home page."""
        self.home_page.navigate()

    @autologger.automation_logger("Task")
    def start_host_flow(self):
        """Navigate directly to the host setup page."""
        self.setup_page.navigate()

    @autologger.automation_logger("Task")
    def select_question_pack(self, pack_name: str):
        """Select a question pack by name from the pack dropdown."""
        self.setup_page.select_pack_by_name(pack_name)

    @autologger.automation_logger("Task")
    def start_game(self):
        """Click Start Game to enter the waiting room."""
        self.setup_page.click_start_game()

    @autologger.automation_logger("Task")
    def open_question(self):
        """Click the first available (unrevealed) board cell."""
        self.board_page.click_first_available_cell()

    @autologger.automation_logger("Task")
    def reveal_answer(self):
        """Click Reveal Answer."""
        self.board_page.click_reveal()

    @autologger.automation_logger("Task")
    def judge_correct(self):
        """Click Correct judge button."""
        self.board_page.click_correct()

    @autologger.automation_logger("Task")
    def judge_incorrect(self):
        """Click Incorrect judge button."""
        self.board_page.click_incorrect()

    @autologger.automation_logger("Task")
    def return_to_board(self):
        """Return from question view to the main board."""
        self.board_page.click_return_to_board()

    @autologger.automation_logger("Task")
    def open_host_controls(self):
        """Click the mid-game Controls button."""
        self.board_page.click_controls_button()

    @autologger.automation_logger("Task")
    def get_room_code(self) -> str:
        """Return the room code from the setup / waiting room screen."""
        return self.setup_page.get_room_code()

    @autologger.automation_logger("Task")
    def get_available_packs(self) -> list:
        """Return list of available question pack names."""
        return self.setup_page.get_available_packs()
