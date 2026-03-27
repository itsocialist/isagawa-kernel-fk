"""
HostRole - CIQ Jeopardy multi-step host workflows.

Roles coordinate Tasks into complete business workflows.
Roles contain NO assertions (assertions live in Tests only).
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tasks.ciq_jeopardy.host_tasks import HostTasks
from pages.ciq_jeopardy.host_setup_page import HostSetupPage
from pages.ciq_jeopardy.game_board_page import GameBoardPage
from resources.utilities import autologger


class HostRole:
    """
    Business-level workflows for the Jeopardy host persona.

    Workflows:
        setup_and_start_game       - Full flow: nav → pick pack → start → enter waiting room
        open_question_and_return   - Select a question cell and immediately return to board
        reveal_and_judge_correct   - Reveal answer then judge it correct
        reveal_and_judge_incorrect - Reveal answer then judge it incorrect
        access_controls_mid_game   - Verify host can open controls after game has started
    """

    def __init__(self, browser, pack_name: str = "Music and Microchips"):
        self.browser = browser
        self.pack_name = pack_name
        self.tasks = HostTasks(browser)
        self.setup_page = HostSetupPage(browser)
        self.board_page = GameBoardPage(browser)
        self.room_code = None

    @autologger.automation_logger("Role")
    def setup_and_start_game(self):
        """
        Navigate to host setup, select a pack, start game.
        Stores the room code for cross-role use.
        """
        self.tasks.start_host_flow()
        self.tasks.select_question_pack(self.pack_name)
        self.tasks.start_game()
        # Room code is shown in waiting room
        try:
            self.room_code = self.setup_page.get_room_code()
        except Exception:
            self.room_code = None

    @autologger.automation_logger("Role")
    def open_question_and_return(self):
        """Click first board cell, then immediately return to board."""
        self.tasks.open_question()
        self.tasks.return_to_board()

    @autologger.automation_logger("Role")
    def reveal_and_judge_correct(self):
        """Reveal the answer on an open question and mark it correct."""
        self.tasks.reveal_answer()
        self.tasks.judge_correct()

    @autologger.automation_logger("Role")
    def reveal_and_judge_incorrect(self):
        """Reveal the answer on an open question and mark it incorrect."""
        self.tasks.reveal_answer()
        self.tasks.judge_incorrect()

    @autologger.automation_logger("Role")
    def access_controls_mid_game(self):
        """Click the Controls button while a game is in progress."""
        self.tasks.open_host_controls()
