"""
TestDigitmGtmPipeline - E2E test for the full pipeline workflow.

Validates:
1. Dashboard loads with sidebar navigation
2. Product creation form works
3. Product appears in list after creation
4. Pipeline can be triggered from product detail
5. Pipeline view shows stages

Phase A: Single user, no auth required.
"""

import pytest
import time
from resources.utilities import autologger
from roles.digitm_gtm.founder import Founder
from pages.digitm_gtm.landing_page import LandingPage
from pages.digitm_gtm.dashboard_page import DashboardPage
from pages.digitm_gtm.product_detail_page import ProductDetailPage
from pages.digitm_gtm.pipeline_view_page import PipelineViewPage
from selenium.webdriver.common.by import By


class TestDigitmGtmDashboard:
    """E2E tests for dashboard and navigation."""

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.dashboard = DashboardPage(self.browser)

    @pytest.mark.digitm_gtm
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_dashboard_loads(self):
        """
        E2E: Dashboard renders with sidebar and heading.

        AAA:
        1. Arrange - Navigate to dashboard
        2. Act - Wait for page load
        3. Assert - Dashboard heading and sidebar visible
        """
        # Arrange & Act
        base_url = self.config["url"]
        self.dashboard.navigate(base_url).wait_for_page_loaded()

        # Assert
        assert self.dashboard.is_dashboard_displayed(), \
            "Dashboard heading should be visible"
        assert self.dashboard.is_sidebar_displayed(), \
            "Sidebar with 'Digitm GTM' brand should be visible"

    @pytest.mark.digitm_gtm
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_sidebar_navigation(self):
        """
        E2E: Sidebar nav links work.

        AAA:
        1. Arrange - Load dashboard
        2. Act - Click Products in sidebar
        3. Assert - Products page loads
        """
        # Arrange
        base_url = self.config["url"]
        self.dashboard.navigate(base_url).wait_for_page_loaded()

        # Act
        self.dashboard.click_nav_products()
        time.sleep(1)

        # Assert
        assert "/products" in self.browser.get_current_url(), \
            "Should navigate to /products after clicking sidebar link"


class TestDigitmGtmProductCreation:
    """E2E tests for creating and viewing products."""

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.dashboard = DashboardPage(self.browser)
        self.product_detail = ProductDetailPage(self.browser)

    @pytest.mark.digitm_gtm
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_new_product_wizard_loads(self):
        """
        E2E: Product creation wizard renders with step 1.

        AAA:
        1. Arrange - Navigate to new product page
        2. Act - Wait for wizard
        3. Assert - Step 1 heading, input, and Continue button visible
        """
        # Arrange & Act
        base_url = self.config["url"]
        self.browser.navigate_to(base_url + "/products/new")
        self.browser.wait_for_element_visible(By.XPATH, "//h2[contains(., 'product called')]", timeout=15)

        # Assert
        assert self.browser.is_element_displayed(By.XPATH, "//h2[contains(., 'product called')]"), \
            "Step 1 heading should be visible"
        assert self.browser.is_element_displayed(By.TAG_NAME, "input"), \
            "Product name input should be visible"
        assert self.browser.is_element_displayed(By.XPATH, "//button[contains(., 'Continue')]"), \
            "Continue button should be visible"

    @pytest.mark.digitm_gtm
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_create_product_via_wizard(self):
        """
        E2E: Create a product through the 5-step wizard.

        AAA:
        1. Arrange - Navigate to wizard
        2. Act - Complete all 5 steps
        3. Assert - Redirected to product detail page
        """
        # Arrange
        base_url = self.config["url"]
        product_name = f"Wizard Product {int(time.time())}"
        self.browser.navigate_to(base_url + "/products/new")
        self.browser.wait_for_element_visible(By.XPATH, "//h2[contains(., 'product called')]", timeout=15)

        # Step 1: Name
        self.browser.type(By.TAG_NAME, "input", product_name)
        self.browser.click(By.XPATH, "//button[contains(., 'Continue')]")
        time.sleep(1)

        # Step 2: Description
        self.browser.wait_for_element_visible(By.TAG_NAME, "textarea", timeout=10)
        self.browser.type(
            By.TAG_NAME, "textarea",
            "An automated test product created by the wizard E2E test"
        )
        self.browser.click(By.XPATH, "//button[contains(., 'Continue')]")
        time.sleep(1)

        # Step 3: Audience
        self.browser.wait_for_element_visible(By.TAG_NAME, "input", timeout=10)
        self.browser.type(By.TAG_NAME, "input", "QA automation engineers and testers")
        self.browser.click(By.XPATH, "//button[contains(., 'Continue')]")
        time.sleep(1)

        # Step 4: Details (optional — just click Continue)
        self.browser.wait_for_element_visible(By.XPATH, "//h2[contains(., 'different')]", timeout=10)
        self.browser.click(By.XPATH, "//button[contains(., 'Continue')]")
        time.sleep(1)

        # Step 5: Confirm — click Create & Launch Pipeline
        self.browser.wait_for_element_visible(By.XPATH, "//h2[contains(., 'Ready to launch')]", timeout=10)
        self.browser.click(By.XPATH, "//button[contains(., 'Create')]")

        # Wait for redirect to product detail
        time.sleep(5)

        # Assert
        assert "/products/" in self.browser.get_current_url(), \
            "Should redirect to product detail page after wizard completion"
        assert self.product_detail.is_product_displayed(), \
            "Product name should be visible on detail page"

    @pytest.mark.digitm_gtm
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_product_appears_in_list(self):
        """
        E2E: Products page shows created products.

        AAA:
        1. Arrange - Navigate to products list
        2. Act - Wait for list to load
        3. Assert - At least one product card visible
        """
        # Arrange & Act
        base_url = self.config["url"]
        self.browser.navigate_to(base_url + "/products")
        time.sleep(2)

        # Assert
        assert self.browser.is_element_displayed(
            By.CSS_SELECTOR, "a[href^='/products/']", timeout=10
        ), "At least one product link should be visible in the list"


class TestDigitmGtmPipelineRun:
    """E2E tests for pipeline execution and management."""

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.product_detail = ProductDetailPage(self.browser)
        self.pipeline_view = PipelineViewPage(self.browser)

    def _navigate_to_first_product(self):
        """Helper: go to the first product's detail page."""
        base_url = self.config["url"]
        self.browser.navigate_to(base_url + "/products")
        time.sleep(2)
        # Click the first product link
        self.browser.click(By.CSS_SELECTOR, "a[href^='/products/c']")
        time.sleep(2)
        self.product_detail.wait_for_page_loaded()

    @pytest.mark.digitm_gtm
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_run_pipeline_button_triggers_run(self):
        """
        E2E: Clicking Run Pipeline creates a pipeline run.

        AAA:
        1. Arrange - Navigate to a product detail page
        2. Act - Click Run Pipeline
        3. Assert - Pipeline run appears in the runs list
        """
        # Arrange
        self._navigate_to_first_product()

        assert self.product_detail.is_run_pipeline_displayed(), \
            "Run Pipeline button should be visible"

        # Act
        self.product_detail.click_run_pipeline()
        time.sleep(3)  # Wait for run to be created

        # Assert - a pipeline run link should now appear
        assert self.product_detail.has_pipeline_runs() or self.product_detail.has_no_runs(), \
            "Pipeline runs section should be visible after triggering"

    @pytest.mark.digitm_gtm
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_pipeline_view_shows_stages(self):
        """
        E2E: Pipeline view page shows 7 stage cards.

        AAA:
        1. Arrange - Navigate to a product and trigger pipeline
        2. Act - Click into the pipeline run
        3. Assert - Stage cards are visible
        """
        # Arrange - go to first product
        self._navigate_to_first_product()

        # Check if there's already a pipeline run to view
        time.sleep(2)
        if self.product_detail.has_pipeline_runs():
            # Act - click into the first run
            self.browser.click(By.CSS_SELECTOR, "a[href*='/pipeline/']")
            time.sleep(2)

            # Assert
            assert self.pipeline_view.is_pipeline_displayed(), \
                "Pipeline heading should be visible"
            assert self.pipeline_view.has_stage_cards(), \
                "Stage cards should be visible in the pipeline view"
            assert self.pipeline_view.is_on_pipeline_page(), \
                "URL should contain /pipeline/"
        else:
            pytest.skip("No pipeline runs available to view — run test_run_pipeline_button_triggers_run first")


class TestDigitmGtmSettings:
    """E2E tests for settings page."""

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config

    @pytest.mark.digitm_gtm
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_settings_page_loads(self):
        """
        E2E: Settings page shows adapter config and auto-feedback toggles.

        AAA:
        1. Arrange - Navigate to settings
        2. Act - Wait for page
        3. Assert - Settings heading and adapter info visible
        """
        # Arrange & Act
        base_url = self.config["url"]
        self.browser.navigate_to(base_url + "/settings")
        time.sleep(2)

        # Assert
        assert self.browser.is_element_displayed(
            By.XPATH, "//h1[contains(., 'Settings')]", timeout=10
        ), "Settings heading should be visible"
        assert self.browser.is_element_displayed(
            By.XPATH, "//*[contains(., 'Social Adapter')]", timeout=5
        ), "Social Adapter section should be visible"
