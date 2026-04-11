"""
ProductTasks - Task module for Digitm GTM product operations.

Handles creating products, viewing details, and triggering pipelines.
Phase A: Single user, no auth required.
"""

from interfaces.browser_interface import BrowserInterface
from pages.digitm_gtm.product_detail_page import ProductDetailPage
from resources.utilities import autologger
from selenium.webdriver.common.by import By


class ProductTasks:

    def __init__(self, browser: BrowserInterface):
        self.browser = browser
        self.product_detail = ProductDetailPage(browser)

    @autologger.automation_logger("Task")
    def create_product(self, base_url: str, name: str, description: str, audience: str) -> None:
        """Navigate to new product form, fill it, and submit."""
        self.browser.navigate_to(base_url + "/products/new")
        self.browser.wait_for_element_visible(By.CSS_SELECTOR, "form", timeout=15)

        self.browser.type(By.CSS_SELECTOR, "input[placeholder*='Awesome']", name)
        self.browser.type(By.CSS_SELECTOR, "textarea", description)

        # Audience field — third input
        inputs = self.browser.find_elements(By.CSS_SELECTOR, "input[type='text']")
        if len(inputs) >= 2:
            inputs[1].clear()
            inputs[1].send_keys(audience)

        self.browser.click(By.XPATH, "//button[contains(., 'Create Product')]")

    @autologger.automation_logger("Task")
    def trigger_pipeline(self) -> None:
        """Click the Run Pipeline button on a product detail page."""
        self.product_detail.click_run_pipeline()
