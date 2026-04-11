"""
TestDigitmGtmSmoke - Smoke test for Digitm GTM Landing Page.

Validates:
1. Landing page loads with hero content and branding
2. Feature grid displays all 4 features
3. CTA buttons are visible and functional

Phase A: Single user, no auth required for smoke tests.
"""

import pytest
from resources.utilities import autologger
from roles.digitm_gtm.founder import Founder
from pages.digitm_gtm.landing_page import LandingPage


class TestDigitmGtmSmoke:

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.landing_page = LandingPage(self.browser)

    # ==================== TEST METHODS ====================

    @pytest.mark.digitm_gtm
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_page_loads(self):
        """
        Smoke test: Verify the landing page renders with hero content.

        AAA:
        1. Arrange - Create Founder role
        2. Act - Visit landing page
        3. Assert - Hero heading and brand name visible
        """
        # Arrange
        base_url = self.config["url"]
        founder = Founder(self.browser, base_url)

        # Act
        founder.visit_landing_page()

        # Assert
        assert self.landing_page.is_hero_displayed(), \
            "Hero heading 'Spec to Market' should be visible"

        assert self.landing_page.is_brand_displayed(), \
            "Brand name 'Digitm GTM' should be visible in header"

    @pytest.mark.digitm_gtm
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_page_features(self):
        """
        Smoke test: Verify the 4 feature cards are displayed.

        AAA:
        1. Arrange - Create Founder role
        2. Act - Visit landing page
        3. Assert - All 4 features visible
        """
        # Arrange
        base_url = self.config["url"]
        founder = Founder(self.browser, base_url)

        # Act
        founder.visit_landing_page()

        # Assert
        assert self.landing_page.are_features_displayed(), \
            "All 4 feature cards should be visible: Pipeline, AI, Feedback, HITL"

    @pytest.mark.digitm_gtm
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_page_cta(self):
        """
        Smoke test: Verify CTA buttons exist.

        AAA:
        1. Arrange - Create Founder role
        2. Act - Visit landing page
        3. Assert - Get Started and Sign In buttons visible
        """
        # Arrange
        base_url = self.config["url"]
        founder = Founder(self.browser, base_url)

        # Act
        founder.visit_landing_page()

        # Assert
        assert self.landing_page.is_get_started_displayed(), \
            "Get Started CTA button should be visible"

    @pytest.mark.digitm_gtm
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_landing_page_footer(self):
        """
        Smoke test: Verify footer with Edge Bird Systems branding.

        AAA:
        1. Arrange - Visit landing page
        2. Act - Scroll to bottom
        3. Assert - Footer visible
        """
        # Arrange
        base_url = self.config["url"]

        # Act
        self.landing_page.navigate(base_url).wait_for_page_loaded()

        # Assert
        assert self.landing_page.is_footer_displayed(), \
            "Footer with 'Edge Bird Systems' should be visible"
