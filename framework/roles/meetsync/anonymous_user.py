"""
AnonymousUser - Role module

Represents an unauthenticated visitor to MeetSync.
Can access the Time Coordinator and Composer without signing in.
"""

from interfaces.browser_interface import BrowserInterface
from resources.utilities import autologger
from tasks.meetsync.scheduling_tasks import SchedulingTasks
from pages.meetsync.time_coordinator_page import TimeCoordinatorPage
from pages.meetsync.composer_page import ComposerPage  # noqa: F401 (re-exported for test access)


class AnonymousUser:
    """
    AnonymousUser role - public scheduling workflows (no login required).

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, browser: BrowserInterface, base_url: str):
        self.browser = browser
        self.base_url = base_url
        self.scheduling_tasks = SchedulingTasks(browser)
        self.coordinator_page = TimeCoordinatorPage(browser)
        self.composer_page = ComposerPage(browser)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def view_time_coordinator(self) -> None:
        """Load the global time coordinator grid and verify it is ready."""
        self.scheduling_tasks.load_time_coordinator(self.base_url)

    @autologger.automation_logger("Role")
    def extract_timezones_from_prompt(self, prompt: str) -> None:
        """Use the NLP bar on the coordinator to extract timezones from a prompt."""
        self.scheduling_tasks.extract_timezones_via_nlp(self.base_url, prompt)

    @autologger.automation_logger("Role")
    def toggle_to_12h_format(self) -> None:
        """Open coordinator and switch to 12-hour clock format."""
        self.scheduling_tasks.toggle_clock_format_to_12h(self.base_url)

    @autologger.automation_logger("Role")
    def compose_meeting_from_new_page(self, prompt: str) -> None:
        """Open /meetings/new, type a prompt, and submit for AI composition."""
        self.scheduling_tasks.submit_meeting_composition(self.base_url, prompt)

    @autologger.automation_logger("Role")
    def compose_meeting_from_schedule_page(self, prompt: str) -> None:
        """Open /schedule, type a prompt, and submit for AI composition."""
        self.scheduling_tasks.submit_via_schedule_page(self.base_url, prompt)
