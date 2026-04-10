"""
ShiftManagementTasks - Task module

Orchestrates page objects for BoothCall shift CRUD workflows.
Handles shift creation, edit, and delete as domain operations.
"""

from interfaces.browser_interface import BrowserInterface
from pages.boothcall.event_dashboard_page import EventDashboardPage
from pages.boothcall.shift_management_page import ShiftManagementPage
from resources.utilities import autologger


class ShiftManagementTasks:
    """
    Task module for BoothCall Shift Management workflow.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    """

    def __init__(self, browser: BrowserInterface):
        """
        Compose Page Objects — NO decorator on constructor.

        Args:
            browser: BrowserInterface instance
        """
        self.browser = browser
        self.event_dashboard = EventDashboardPage(browser)
        self.shift_page = ShiftManagementPage(browser)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def navigate_to_shifts_tab(self) -> None:
        """
        Click the Shifts tab from the event detail page.
        """
        self.event_dashboard.click_shifts_tab()
        self.shift_page.wait_for_add_shift_button()

    @autologger.automation_logger("Task")
    def open_add_shift_dialog(self) -> None:
        """
        Click Add Shift button and wait for the dialog to appear.
        """
        (self.shift_page
            .click_add_shift()
            .wait_for_dialog_visible())

    @autologger.automation_logger("Task")
    def fill_shift_form_and_submit(self, role: str = "Demo Lead", start_time: str = "09:00", end_time: str = "17:00") -> None:
        """
        Fill out the Add Shift form and submit it.

        Args:
            role: Role preset name (e.g. "Demo Lead", "Greeter")
            start_time: Start time in HH:mm format
            end_time: End time in HH:mm format
        """
        # Select role
        self.shift_page.click_role_selector()

        if role == "Demo Lead":
            self.shift_page.select_role_demo_lead()
        elif role == "Greeter":
            self.shift_page.select_role_greeter()

        # Select start date (pick first available day)
        (self.shift_page
            .click_start_date_picker()
            .select_first_available_day())

        # Set start time
        self.shift_page.set_start_time(start_time)

        # Select end date (pick first available day again — same day)
        (self.shift_page
            .click_end_date_picker()
            .select_first_available_day())

        # Set end time
        self.shift_page.set_end_time(end_time)

        # Submit
        self.shift_page.click_submit()

    @autologger.automation_logger("Task")
    def delete_first_shift(self) -> None:
        """
        Click delete on the first shift card and confirm deletion.
        """
        (self.shift_page
            .click_delete_on_first_shift()
            .confirm_delete())
