"""
ShiftManagementPage - Page Object Model

Page Object for the BoothCall Add Shift dialog and Shifts management panel.
Handles shift creation, editing, and deletion UI interactions.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class ShiftManagementPage:
    """
    Page Object for BoothCall Shift Management.

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

    # Add Shift Dialog
    ADD_SHIFT_BUTTON = (By.CSS_SELECTOR, "#add-shift-btn")
    DIALOG_TITLE = (By.XPATH, "//h2[text()='Add Shift']")
    ROLE_SELECT_TRIGGER = (By.CSS_SELECTOR, "[role='combobox']")
    ROLE_OPTION_DEMO_LEAD = (By.XPATH, "//div[@role='option'][contains(., 'Demo Lead')]")
    ROLE_OPTION_GREETER = (By.XPATH, "//div[@role='option'][contains(., 'Greeter')]")
    ROLE_OPTION_SCANNER = (By.XPATH, "//div[@role='option'][contains(., 'Scanner')]")

    # DateTimePicker — Start time
    START_DATE_BUTTON = (By.XPATH, "(//button[@type='button'][contains(@class, 'flex-1')])[1]")
    START_TIME_INPUT = (By.XPATH, "(//input[@type='time'])[1]")

    # DateTimePicker — End time
    END_DATE_BUTTON = (By.XPATH, "(//button[@type='button'][contains(@class, 'flex-1')])[2]")
    END_TIME_INPUT = (By.XPATH, "(//input[@type='time'])[2]")

    # Calendar popover
    CALENDAR_DAY_TODAY = (By.CSS_SELECTOR, "[aria-selected='true'], .rdp-day_today")
    CALENDAR_NEXT_DAY = (By.XPATH, "//button[@name='day' and not(@disabled)]")

    # Staff inputs
    MIN_STAFF_INPUT = (By.XPATH, "//input[@type='number'][1]")
    MAX_STAFF_INPUT = (By.XPATH, "//input[@type='number'][2]")

    # Submit
    SUBMIT_BUTTON = (By.XPATH, "//button[@type='submit']")

    # Shift list items (Shifts management panel)
    SHIFT_CARD = (By.CSS_SELECTOR, "[class*='rounded-2xl'][class*='group']")
    SHIFT_LABEL = (By.CSS_SELECTOR, "h3")
    EDIT_BUTTON = (By.XPATH, "//button[contains(., 'Edit')]")
    DELETE_BUTTON = (By.XPATH, "//button[contains(., 'Delete')]")

    # Delete confirmation dialog
    DELETE_CONFIRM_BUTTON = (By.XPATH, "//button[contains(., 'Delete Shift')]")
    DELETE_CANCEL_BUTTON = (By.XPATH, "//button[contains(., 'Cancel')]")

    # Toast notifications
    SUCCESS_TOAST = (By.XPATH, "//li[contains(@class, 'toast')]//div[contains(., 'added') or contains(., 'updated') or contains(., 'deleted')]")

    # Coverage schedule subheading
    COVERAGE_SUBTITLE = (By.XPATH, "//*[contains(text(), 'shift')]")

    # ==================== NAVIGATION ====================

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def wait_for_add_shift_button(self, timeout: int = 15) -> "ShiftManagementPage":
        """Wait for the Add Shift button to be visible."""
        self.browser.wait_for_element_visible(*self.ADD_SHIFT_BUTTON, timeout=timeout)
        return self

    def click_add_shift(self) -> "ShiftManagementPage":
        """Click the Add Shift button to open the dialog."""
        self.browser.click(*self.ADD_SHIFT_BUTTON)
        return self

    def wait_for_dialog_visible(self, timeout: int = 10) -> "ShiftManagementPage":
        """Wait for the Add Shift dialog to be visible."""
        self.browser.wait_for_element_visible(*self.DIALOG_TITLE, timeout=timeout)
        return self

    def click_role_selector(self) -> "ShiftManagementPage":
        """Click the role dropdown trigger."""
        self.browser.click(*self.ROLE_SELECT_TRIGGER)
        return self

    def select_role_demo_lead(self) -> "ShiftManagementPage":
        """Select Demo Lead from the role dropdown."""
        self.browser.click(*self.ROLE_OPTION_DEMO_LEAD)
        return self

    def select_role_greeter(self) -> "ShiftManagementPage":
        """Select Greeter from the role dropdown."""
        self.browser.click(*self.ROLE_OPTION_GREETER)
        return self

    def click_start_date_picker(self) -> "ShiftManagementPage":
        """Open the start date calendar popover."""
        self.browser.click(*self.START_DATE_BUTTON)
        return self

    def select_first_available_day(self) -> "ShiftManagementPage":
        """Select the first available (non-disabled) calendar day."""
        self.browser.click(*self.CALENDAR_NEXT_DAY)
        return self

    def set_start_time(self, time_value: str) -> "ShiftManagementPage":
        """Set the start time value (HH:mm format)."""
        self.browser.type(*self.START_TIME_INPUT, time_value)
        return self

    def click_end_date_picker(self) -> "ShiftManagementPage":
        """Open the end date calendar popover."""
        self.browser.click(*self.END_DATE_BUTTON)
        return self

    def set_end_time(self, time_value: str) -> "ShiftManagementPage":
        """Set the end time value (HH:mm format)."""
        self.browser.type(*self.END_TIME_INPUT, time_value)
        return self

    def set_min_staff(self, count: str) -> "ShiftManagementPage":
        """Set the minimum staff count."""
        self.browser.type(*self.MIN_STAFF_INPUT, count)
        return self

    def set_max_staff(self, count: str) -> "ShiftManagementPage":
        """Set the maximum staff count."""
        self.browser.type(*self.MAX_STAFF_INPUT, count)
        return self

    def click_submit(self) -> "ShiftManagementPage":
        """Click the submit button to save the shift."""
        self.browser.click(*self.SUBMIT_BUTTON)
        return self

    def click_edit_on_first_shift(self) -> "ShiftManagementPage":
        """Click the Edit button on the first shift card."""
        self.browser.click(*self.EDIT_BUTTON)
        return self

    def click_delete_on_first_shift(self) -> "ShiftManagementPage":
        """Click the Delete button on the first shift card."""
        self.browser.click(*self.DELETE_BUTTON)
        return self

    def confirm_delete(self) -> "ShiftManagementPage":
        """Click the Delete Shift confirmation button."""
        self.browser.click(*self.DELETE_CONFIRM_BUTTON)
        return self

    def cancel_delete(self) -> "ShiftManagementPage":
        """Click Cancel on the delete confirmation dialog."""
        self.browser.click(*self.DELETE_CANCEL_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_add_shift_button_displayed(self) -> bool:
        """Check if the Add Shift button is visible."""
        return self.browser.is_element_displayed(*self.ADD_SHIFT_BUTTON)

    def is_dialog_displayed(self) -> bool:
        """Check if the Add Shift dialog is currently visible."""
        return self.browser.is_element_displayed(*self.DIALOG_TITLE)

    def is_success_toast_displayed(self) -> bool:
        """Check if a success toast notification is visible."""
        return self.browser.is_element_displayed(*self.SUCCESS_TOAST, timeout=10)

    def get_shift_card_count(self) -> int:
        """Count the number of shift cards present."""
        cards = self.browser.find_elements(*self.SHIFT_CARD, timeout=5)
        return len(cards)

    def is_shift_displayed(self, label: str) -> bool:
        """Check if a shift with the given label is visible in the list."""
        locator = (By.XPATH, f"//h3[contains(text(), '{label}')]")
        return self.browser.is_element_displayed(*locator)
