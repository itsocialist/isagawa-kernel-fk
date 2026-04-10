"""
EventOrganizer - Role module

Represents an event organizer persona who navigates the BoothCall platform,
views events, and manages shifts. Orchestrates complete business workflows
using Task modules.
"""

from interfaces.browser_interface import BrowserInterface
from resources.utilities import autologger
from tasks.boothcall.navigation_tasks import NavigationTasks
from tasks.boothcall.shift_management_tasks import ShiftManagementTasks


class EventOrganizer:
    """
    EventOrganizer role - orchestrates event management workflows.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, browser_interface: BrowserInterface, base_url: str):
        """
        Initialize and compose Task modules.

        Args:
            browser_interface: BrowserInterface instance
            base_url: Base URL for BoothCall application
        """
        self.browser = browser_interface
        self.base_url = base_url
        self.navigation_tasks = NavigationTasks(browser_interface)
        self.shift_management_tasks = ShiftManagementTasks(browser_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def visit_landing_and_navigate_to_login(self) -> None:
        """
        Complete workflow: Visit landing page, then navigate to the login page.

        Orchestrates MULTIPLE task operations:
        1. Open the landing page
        2. Click Sign In to navigate to the login page
        """
        self.navigation_tasks.open_landing_page(self.base_url)
        self.navigation_tasks.navigate_to_login_from_landing()

    @autologger.automation_logger("Role")
    def visit_landing_page(self) -> None:
        """
        Simple workflow: Visit the BoothCall landing page and verify load.
        """
        self.navigation_tasks.open_landing_page(self.base_url)

    @autologger.automation_logger("Role")
    def create_shift_on_event(self, role: str = "Demo Lead", start_time: str = "09:00", end_time: str = "17:00") -> None:
        """
        Complete workflow: Navigate to Shifts tab, open dialog, create a shift.

        Orchestrates MULTIPLE task operations:
        1. Navigate to Shifts tab
        2. Open Add Shift dialog
        3. Fill and submit shift form

        Args:
            role: Shift role preset name
            start_time: Start time in HH:mm format
            end_time: End time in HH:mm format
        """
        self.shift_management_tasks.navigate_to_shifts_tab()
        self.shift_management_tasks.open_add_shift_dialog()
        self.shift_management_tasks.fill_shift_form_and_submit(role, start_time, end_time)

    @autologger.automation_logger("Role")
    def create_shift_on_event_continue(self, role: str = "Demo Lead", start_time: str = "09:00", end_time: str = "17:00") -> None:
        """
        Continue workflow (already on event page): Open dialog and create a shift.
        Skips tab navigation — assumes already on Shifts tab.

        Args:
            role: Shift role preset name
            start_time: Start time in HH:mm format
            end_time: End time in HH:mm format
        """
        self.shift_management_tasks.open_add_shift_dialog()
        self.shift_management_tasks.fill_shift_form_and_submit(role, start_time, end_time)

    @autologger.automation_logger("Role")
    def delete_first_shift_on_event(self) -> None:
        """
        Complete workflow: Navigate to Shifts tab and delete the first shift.
        """
        self.shift_management_tasks.navigate_to_shifts_tab()
        self.shift_management_tasks.delete_first_shift()
