"""
TeamManagementTasks - Task module

Orchestrates page objects for BoothCall team invitation and roster workflows.
Handles email invites, manual adds, and roster operations.
"""

from interfaces.browser_interface import BrowserInterface
from pages.boothcall.event_dashboard_page import EventDashboardPage
from pages.boothcall.team_management_page import TeamManagementPage
from resources.utilities import autologger


class TeamManagementTasks:
    """
    Task module for BoothCall Team Management workflow.

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
        self.team_page = TeamManagementPage(browser)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def navigate_to_team_tab(self) -> None:
        """
        Click the Team tab from the event detail page.
        """
        self.event_dashboard.click_team_tab()
        self.team_page.wait_for_team_page()

    @autologger.automation_logger("Task")
    def open_invite_dialog(self) -> None:
        """
        Click Invite Staff and wait for the invite dialog.
        """
        (self.team_page
            .click_invite_staff()
            .wait_for_invite_dialog())

    @autologger.automation_logger("Task")
    def manual_add_member(self, email: str, name: str = "") -> None:
        """
        Switch to Manual Add tab and add a member to the roster.

        Args:
            email: Member email address
            name: Member display name (optional)
        """
        self.team_page.click_manual_tab()

        self.team_page.enter_manual_email(email)

        if name:
            self.team_page.enter_manual_name(name)

        self.team_page.click_add_to_roster()

    @autologger.automation_logger("Task")
    def send_email_invite(self, email: str, name: str = "") -> None:
        """
        Send an email invitation to a team member.

        Args:
            email: Member email address
            name: Member display name (optional)
        """
        self.team_page.click_email_tab()

        self.team_page.enter_invite_email(email)

        if name:
            self.team_page.enter_invite_name(name)

        self.team_page.click_send_invitation()

    @autologger.automation_logger("Task")
    def generate_invite_link(self) -> None:
        """
        Switch to Link tab and generate a shareable invite link.
        """
        self.team_page.click_link_tab()
        self.team_page.click_copy_invite_link()
