"""
TeamManagementPage - Page Object Model

Page Object for the BoothCall Team page (/events/[id]/team).
Handles invite dialog (email, link, manual), roster listing, and member actions.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class TeamManagementPage:
    """
    Page Object for BoothCall Team Management.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, browser: BrowserInterface):
        """Compose BrowserInterface — NO inheritance."""
        self.browser = browser

    # ==================== LOCATORS (Class Constants) ====================

    # Page header
    TEAM_HEADING = (By.XPATH, "//h2[contains(., 'Team Roster')]")
    INVITE_STAFF_BUTTON = (By.CSS_SELECTOR, "#invite-staff-btn")

    # Invite dialog
    DIALOG_TITLE = (By.XPATH, "//h2[text()='Add Team Members']")

    # Tab triggers inside dialog
    EMAIL_TAB = (By.XPATH, "//button[@role='tab'][contains(., 'Email Invite')]")
    LINK_TAB = (By.XPATH, "//button[@role='tab'][contains(., 'Invite Link')]")
    MANUAL_TAB = (By.XPATH, "//button[@role='tab'][contains(., 'Manual Add')]")

    # Email invite tab
    INVITE_EMAIL_INPUT = (By.CSS_SELECTOR, "#invite-email")
    INVITE_NAME_INPUT = (By.CSS_SELECTOR, "#invite-name")
    SEND_INVITATION_BUTTON = (By.XPATH, "//button[contains(., 'Send Invitation')]")

    # Link invite tab
    COPY_LINK_BUTTON = (By.XPATH, "//button[contains(., 'Copy Invite Link')]")

    # Manual add tab
    MANUAL_EMAIL_INPUT = (By.CSS_SELECTOR, "#manual-email")
    MANUAL_NAME_INPUT = (By.CSS_SELECTOR, "#manual-name")
    ADD_TO_ROSTER_BUTTON = (By.XPATH, "//button[contains(., 'Add to Roster')]")

    # Roster list
    MEMBER_ROW = (By.CSS_SELECTOR, "[class*='flex items-center gap-4 px-5']")
    PENDING_BADGE = (By.XPATH, "//span[contains(., 'Pending')]")
    ACCEPTED_BADGE = (By.XPATH, "//span[contains(., 'Accepted')]")
    REVOKE_BUTTON = (By.XPATH, "//button[contains(., 'Revoke')]")

    # Empty state
    EMPTY_STATE = (By.XPATH, "//p[contains(., 'No team members yet')]")

    # Toast notifications
    SUCCESS_TOAST = (By.XPATH, "//li[contains(@class, 'toast')]")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def wait_for_team_page(self, timeout: int = 15) -> "TeamManagementPage":
        """Wait for Team Roster heading to be visible."""
        self.browser.wait_for_element_visible(*self.TEAM_HEADING, timeout=timeout)
        return self

    def click_invite_staff(self) -> "TeamManagementPage":
        """Click the Invite Staff button."""
        self.browser.click(*self.INVITE_STAFF_BUTTON)
        return self

    def wait_for_invite_dialog(self, timeout: int = 10) -> "TeamManagementPage":
        """Wait for the invite dialog to appear."""
        self.browser.wait_for_element_visible(*self.DIALOG_TITLE, timeout=timeout)
        return self

    # --- Email invite ---
    def click_email_tab(self) -> "TeamManagementPage":
        """Click the Email Invite tab."""
        self.browser.click(*self.EMAIL_TAB)
        return self

    def enter_invite_email(self, email: str) -> "TeamManagementPage":
        """Enter email in the invite email field."""
        self.browser.type(*self.INVITE_EMAIL_INPUT, email)
        return self

    def enter_invite_name(self, name: str) -> "TeamManagementPage":
        """Enter name in the invite name field."""
        self.browser.type(*self.INVITE_NAME_INPUT, name)
        return self

    def click_send_invitation(self) -> "TeamManagementPage":
        """Click the Send Invitation button."""
        self.browser.click(*self.SEND_INVITATION_BUTTON)
        return self

    # --- Link invite ---
    def click_link_tab(self) -> "TeamManagementPage":
        """Click the Invite Link tab."""
        self.browser.click(*self.LINK_TAB)
        return self

    def click_copy_invite_link(self) -> "TeamManagementPage":
        """Click the Copy Invite Link button."""
        self.browser.click(*self.COPY_LINK_BUTTON)
        return self

    # --- Manual add ---
    def click_manual_tab(self) -> "TeamManagementPage":
        """Click the Manual Add tab."""
        self.browser.click(*self.MANUAL_TAB)
        return self

    def enter_manual_email(self, email: str) -> "TeamManagementPage":
        """Enter email in the manual add field."""
        self.browser.type(*self.MANUAL_EMAIL_INPUT, email)
        return self

    def enter_manual_name(self, name: str) -> "TeamManagementPage":
        """Enter name in the manual add name field."""
        self.browser.type(*self.MANUAL_NAME_INPUT, name)
        return self

    def click_add_to_roster(self) -> "TeamManagementPage":
        """Click the Add to Roster button."""
        self.browser.click(*self.ADD_TO_ROSTER_BUTTON)
        return self

    # --- Roster actions ---
    def click_revoke_on_first_pending(self) -> "TeamManagementPage":
        """Click Revoke on the first pending member."""
        self.browser.click(*self.REVOKE_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_team_page_displayed(self) -> bool:
        """Check if the Team Roster heading is visible."""
        return self.browser.is_element_displayed(*self.TEAM_HEADING)

    def is_invite_dialog_displayed(self) -> bool:
        """Check if the invite dialog is visible."""
        return self.browser.is_element_displayed(*self.DIALOG_TITLE)

    def is_empty_state_displayed(self) -> bool:
        """Check if the empty state message is visible."""
        return self.browser.is_element_displayed(*self.EMPTY_STATE)

    def get_member_count(self) -> int:
        """Count the number of roster member rows."""
        rows = self.browser.find_elements(*self.MEMBER_ROW, timeout=5)
        return len(rows)

    def is_member_displayed(self, email_or_name: str) -> bool:
        """Check if a member with the given email or name is visible."""
        locator = (By.XPATH, f"//*[contains(text(), '{email_or_name}')]")
        return self.browser.is_element_displayed(*locator)

    def is_accepted_badge_displayed(self) -> bool:
        """Check if any Accepted badge is visible in the roster."""
        return self.browser.is_element_displayed(*self.ACCEPTED_BADGE)

    def is_pending_badge_displayed(self) -> bool:
        """Check if any Pending badge is visible in the roster."""
        return self.browser.is_element_displayed(*self.PENDING_BADGE)

    def is_success_toast_displayed(self) -> bool:
        """Check if a success toast notification is visible."""
        return self.browser.is_element_displayed(*self.SUCCESS_TOAST, timeout=10)
