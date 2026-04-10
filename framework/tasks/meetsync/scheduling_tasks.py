"""
SchedulingTasks - Task module

Orchestrates MeetSync page objects to accomplish scheduling workflows.
Covers time coordinator interaction and meeting composition.
"""

from interfaces.browser_interface import BrowserInterface
from pages.meetsync.time_coordinator_page import TimeCoordinatorPage
from pages.meetsync.composer_page import ComposerPage
from resources.utilities import autologger


class SchedulingTasks:
    """
    Task module for MeetSync scheduling workflows.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.coordinator_page = TimeCoordinatorPage(browser)
        self.composer_page = ComposerPage(browser)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def load_time_coordinator(self, base_url: str) -> None:
        """Navigate to /meetings and wait for the grid to be visible."""
        (self.coordinator_page
            .navigate(base_url)
            .wait_for_page_load()
            .wait_for_grid())

    @autologger.automation_logger("Task")
    def extract_timezones_via_nlp(self, base_url: str, prompt: str) -> None:
        """Navigate to coordinator, enter an NLP prompt, and submit it."""
        (self.coordinator_page
            .navigate(base_url)
            .wait_for_page_load()
            .wait_for_grid()
            .enter_nlp_prompt(prompt)
            .click_extract())

    @autologger.automation_logger("Task")
    def toggle_clock_format_to_12h(self, base_url: str) -> None:
        """Navigate to coordinator and switch to 12h clock format."""
        (self.coordinator_page
            .navigate(base_url)
            .wait_for_page_load()
            .wait_for_grid()
            .click_format_12h())

    @autologger.automation_logger("Task")
    def open_composer_and_type_prompt(self, base_url: str, prompt: str) -> None:
        """Navigate to /meetings/new and enter a scheduling prompt."""
        (self.composer_page
            .navigate_new(base_url)
            .wait_for_composer()
            .enter_prompt(prompt))

    @autologger.automation_logger("Task")
    def submit_meeting_composition(self, base_url: str, prompt: str) -> None:
        """Navigate to /meetings/new, enter a prompt, and click Compose."""
        (self.composer_page
            .navigate_new(base_url)
            .wait_for_composer()
            .enter_prompt(prompt)
            .click_compose())

    @autologger.automation_logger("Task")
    def open_schedule_and_type_prompt(self, base_url: str, prompt: str) -> None:
        """Navigate to /schedule and enter a scheduling prompt."""
        (self.composer_page
            .navigate_schedule(base_url)
            .wait_for_composer()
            .enter_prompt(prompt))

    @autologger.automation_logger("Task")
    def submit_via_schedule_page(self, base_url: str, prompt: str) -> None:
        """Navigate to /schedule, enter a prompt, and click Compose."""
        (self.composer_page
            .navigate_schedule(base_url)
            .wait_for_composer()
            .enter_prompt(prompt)
            .click_compose())
