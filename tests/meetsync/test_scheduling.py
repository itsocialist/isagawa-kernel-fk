"""
TestMeetSyncScheduling - Browser tests for MeetSync scheduling features.

Covers:
  - Time Coordinator grid loads and displays zones
  - Clock format toggle (24h/12h)
  - NLP zone extraction
  - Composer page loads (/meetings/new)
  - Schedule page loads (/schedule)
  - Compose button enables only when prompt is entered
  - AI composition flow (thinking state → result or auth banner)

Uses AAA pattern. No auth required — all tested features are public.
"""

import sys
from pathlib import Path
import pytest

# Ensure framework is on the path
PROJECT_ROOT = Path(__file__).parent.parent.parent
FRAMEWORK_PATH = str(PROJECT_ROOT / "framework")
if FRAMEWORK_PATH not in sys.path:
    sys.path.insert(0, FRAMEWORK_PATH)

from resources.utilities import autologger
from roles.meetsync.anonymous_user import AnonymousUser
from pages.meetsync.time_coordinator_page import TimeCoordinatorPage
from pages.meetsync.composer_page import ComposerPage


class TestTimeCoordinator:
    """Tests for the Global Time Coordinator grid at /meetings."""

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.base_url = config["url"]
        self.user = AnonymousUser(browser, self.base_url)
        self.coordinator_page = TimeCoordinatorPage(browser)
        self.composer_page = ComposerPage(browser)

    @pytest.mark.meetsync
    @pytest.mark.time_coordinator
    @autologger.automation_logger("Test")
    def test_coordinator_grid_loads(self):
        """
        Grid loads and is visible at /meetings.

        Arrange: base URL
        Act: navigate to /meetings
        Assert: page heading and grid table are visible
        """
        # Act
        self.user.view_time_coordinator()

        # Assert
        assert self.coordinator_page.is_page_loaded(), \
            "Global Time Coordinator heading should be visible"
        assert self.coordinator_page.is_grid_visible(), \
            "Time grid table should be rendered"

    @pytest.mark.meetsync
    @pytest.mark.time_coordinator
    @autologger.automation_logger("Test")
    def test_default_timezones_displayed(self):
        """
        Default zones (Los Angeles, New York, London, Tokyo) appear in grid headers.

        Arrange: navigate to coordinator
        Act: read timezone header labels
        Assert: at least 2 expected zones appear
        """
        # Act
        self.user.view_time_coordinator()
        labels = self.coordinator_page.get_visible_timezone_labels()

        # Assert
        expected = ["Los Angeles", "New York", "London", "Tokyo"]
        matched = [e for e in expected if any(e in lbl for lbl in labels)]
        assert len(matched) >= 2, \
            f"Expected at least 2 default zones in headers. Got: {labels}"

    @pytest.mark.meetsync
    @pytest.mark.time_coordinator
    @autologger.automation_logger("Test")
    def test_clock_format_toggles_to_12h(self):
        """
        Clicking 12h button switches cell times to AM/PM format.

        Arrange: load coordinator
        Act: click 12h format button
        Assert: AM/PM text appears in grid cells
        """
        # Arrange
        self.user.view_time_coordinator()

        # Act
        self.coordinator_page.click_format_12h()

        # Assert
        assert self.coordinator_page.is_12h_format_active(), \
            "Grid cells should show AM/PM after switching to 12h format"

    @pytest.mark.meetsync
    @pytest.mark.time_coordinator
    @autologger.automation_logger("Test")
    def test_clock_format_toggles_back_to_24h(self):
        """
        Clicking 24h after 12h restores 24-hour format.

        Arrange: load coordinator, switch to 12h
        Act: click 24h
        Assert: 24h format active
        """
        # Arrange
        self.user.view_time_coordinator()
        self.coordinator_page.click_format_12h()

        # Act
        self.coordinator_page.click_format_24h()

        # Assert
        assert self.coordinator_page.is_24h_format_active(), \
            "Grid cells should show HH:MM after switching back to 24h"

    @pytest.mark.meetsync
    @pytest.mark.time_coordinator
    @autologger.automation_logger("Test")
    def test_new_meeting_link_navigates_to_composer(self):
        """
        + New Meeting button navigates to /meetings/new.

        Arrange: load coordinator
        Act: click + New Meeting
        Assert: composer textarea is visible
        """
        # Arrange
        self.user.view_time_coordinator()

        # Act
        self.coordinator_page.click_new_meeting()
        self.composer_page.wait_for_composer(timeout=15)

        # Assert
        assert self.composer_page.is_composer_visible(), \
            "Composer textarea should be visible after navigating to /meetings/new"


class TestComposer:
    """Tests for the Meeting Composer at /meetings/new and /schedule."""

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.base_url = config["url"]
        self.user = AnonymousUser(browser, self.base_url)
        self.composer_page = ComposerPage(browser)

    @pytest.mark.meetsync
    @pytest.mark.composer
    @autologger.automation_logger("Test")
    def test_composer_page_loads(self):
        """
        /meetings/new loads the composer textarea.

        Arrange: base URL
        Act: navigate to /meetings/new
        Assert: textarea visible
        """
        # Act
        self.composer_page.navigate_new(self.base_url).wait_for_composer()

        # Assert
        assert self.composer_page.is_composer_visible(), \
            "Composer textarea should be visible at /meetings/new"

    @pytest.mark.meetsync
    @pytest.mark.composer
    @autologger.automation_logger("Test")
    def test_schedule_page_loads_composer(self):
        """
        /schedule now renders the MeetingComposer (not the old scaffold).

        Arrange: base URL
        Act: navigate to /schedule
        Assert: composer textarea visible (not the old 'Step 1' scaffold)
        """
        # Act
        self.composer_page.navigate_schedule(self.base_url).wait_for_composer()

        # Assert
        assert self.composer_page.is_composer_visible(), \
            "Composer textarea should be visible at /schedule — old scaffold should be gone"

    @pytest.mark.meetsync
    @pytest.mark.composer
    @autologger.automation_logger("Test")
    def test_compose_button_disabled_when_prompt_empty(self):
        """
        Compose button is disabled until text is entered.

        Arrange: navigate to /meetings/new
        Act: read button state before typing
        Assert: button is disabled
        """
        # Arrange
        self.composer_page.navigate_new(self.base_url).wait_for_composer()

        # Assert
        assert self.composer_page.is_compose_button_disabled(), \
            "Compose button should be disabled when textarea is empty"

    @pytest.mark.meetsync
    @pytest.mark.composer
    @autologger.automation_logger("Test")
    def test_compose_button_enables_when_prompt_entered(self):
        """
        Compose button enables after typing a prompt.

        Arrange: navigate to /meetings/new
        Act: type a prompt
        Assert: button is enabled
        """
        # Arrange
        self.composer_page.navigate_new(self.base_url).wait_for_composer()

        # Act
        self.composer_page.enter_prompt("30 min for London and Tokyo")

        # Assert
        assert self.composer_page.is_compose_button_enabled(), \
            "Compose button should be enabled after entering a prompt"

    @pytest.mark.meetsync
    @pytest.mark.composer
    @pytest.mark.ai_integration
    @autologger.automation_logger("Test")
    def test_compose_enters_thinking_state_on_submit(self):
        """
        Clicking Compose immediately transitions button to 'Composing…' state.

        Arrange: navigate to /meetings/new, enter prompt
        Act: click Compose
        Assert: button text changes to 'Composing…' (thinking state)
        """
        # Arrange
        self.composer_page.navigate_new(self.base_url).wait_for_composer()
        self.composer_page.enter_prompt("30 min for London and Tokyo next Tuesday")

        # Act
        self.composer_page.click_compose()

        # Assert — button should briefly show Composing… before AI responds
        assert self.composer_page.is_thinking_state_active(), \
            "Compose button should show 'Composing…' while AI is processing"

    @pytest.mark.meetsync
    @pytest.mark.composer
    @pytest.mark.ai_integration
    @autologger.automation_logger("Test")
    def test_compose_returns_result_or_surfaces_error(self):
        """
        After AI processing completes, either a proposal or a clear error is shown.
        No silent failures — the 'Could not compose' catch must surface something.

        Arrange: navigate to composer, enter prompt
        Act: submit, wait for AI response (up to 60s)
        Assert: proposal card OR error message is visible (never silent blank)
        """
        # Arrange
        self.composer_page.navigate_new(self.base_url).wait_for_composer()
        self.composer_page.enter_prompt("30 minute meeting for London and Tokyo")

        # Act
        self.composer_page.click_compose()
        self.composer_page.wait_for_error_or_auth_banner(timeout=60)

        # Assert
        proposal_shown = self.composer_page.is_proposal_visible()
        error_shown = self.composer_page.is_error_displayed()
        auth_shown = self.composer_page.is_auth_banner_displayed()

        assert proposal_shown or error_shown or auth_shown, \
            "After AI processing, either a proposal, error message, or auth banner must be visible — silent blank is a failure"

        if error_shown:
            error_text = self.composer_page.get_error_text()
            assert error_text, "Error message should have descriptive text, not be empty"
            # Fail the test with the actual error so we can see what broke
            pytest.fail(f"AI scheduling returned error: '{error_text}'")
