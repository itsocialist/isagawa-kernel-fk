"""
Sprint 10 — Email Capture & Waitlist Functional Tests
======================================================
End-to-end functional tests validating Sprint 10 waitlist flows.

Coverage:
  TC-W-01 Landing Page Waitlist — User can enter email and join waitlist from marketing page
  TC-W-02 Debrief Page Save Progress — Anonymous user can save session progress

Auth:
  These tests are explicitly for unauthenticated flows.
  We DO NOT inject cookies for these tests.
"""

import time
import pytest
from resources.utilities import autologger
from pages.sales_sim.sales_sim_pages import LandingPage, DebriefPage

class TestWaitlistFlows:
    """
    Validates anonymous email capture capabilities added in S10-GTM-04.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser      = browser
        self.config       = config
        self.base_url     = config["url"]
        self.landing_page = LandingPage(browser)
        self.debrief_page = DebriefPage(browser)

        # Ensure we are fully anonymous
        browser.navigate_to(self.base_url)
        browser.driver.delete_all_cookies()
        # Clear session storage so we start fresh
        browser.driver.execute_script("window.sessionStorage.clear();")

    def _mock_waitlist_api(self):
        """Mock the /api/waitlist endpoint so we don't spam real emails or hit 500s."""
        self.browser.driver.execute_script("""
            if (!window.originalFetch) {
                window.originalFetch = window.fetch;
                window.fetch = async function(url, options) {
                    if (typeof url === 'string' && url.includes('/api/waitlist')) {
                        // Simulate network delay
                        await new Promise(r => setTimeout(r, 500));
                        return new Response(JSON.stringify({success: true}), {
                            status: 200,
                            headers: {'Content-Type': 'application/json'}
                        });
                    }
                    return window.originalFetch(url, options);
                };
            }
        """)

    @autologger.automation_logger("Test")
    def test_w_01_landing_page_waitlist(self):
        """
        Verify the WaitlistForm on the landing page functions.

        Arrange: Navigate to /
        Act: Enter email, click Join Waitlist
        Assert: Success message is shown
        """
        self.landing_page.navigate(self.base_url)
        self.landing_page.wait_for_load(timeout=15)
        self._mock_waitlist_api()

        test_email = f"auto-test-{int(time.time())}@example.com"
        self.landing_page.fill_waitlist_email(test_email)
        self.landing_page.submit_waitlist()

        assert self.landing_page.is_success_message_visible(timeout=10), \
            "Waitlist success message should appear after submission"

    @autologger.automation_logger("Test")
    def test_w_02_debrief_page_anonymous_waitlist(self):
        """
        Verify the anonymous 'Save your progress' form on the debrief page.

        Arrange: Inject mock session data into sessionStorage, navigate to /labs/debrief
        Act: Enter email, click Save Progress
        Assert: Progress saved success message is shown
        """
        # Navigate to base URL first to establish domain for sessionStorage
        self.browser.navigate_to(self.base_url)

        # Inject fake session data so the debrief page renders normally
        mock_session = {
            "scores": {"composure": 80, "anchor": 70},
            "sessionDurationMs": 120000,
            "turnCount": 5
        }
        self.browser.driver.execute_script(
            "window.sessionStorage.setItem('labs_session', arguments[0]);",
            __import__('json').dumps(mock_session)
        )

        self.debrief_page.navigate(self.base_url)
        
        # Debrief structure should load
        self.debrief_page.wait_for_load(timeout=15)
        self._mock_waitlist_api()

        # Waitlist input should be present for anonymous users
        assert self.browser.driver.find_elements(*self.debrief_page.WAITLIST_EMAIL_INPUT), \
            "Save Progress email input should be visible for anonymous users"

        test_email = f"anon-test-{int(time.time())}@example.com"
        self.debrief_page.fill_waitlist_email(test_email)
        self.debrief_page.submit_waitlist()

        assert self.debrief_page.is_success_message_visible(timeout=10), \
            "Save Progress success message should appear after submission"
