"""
ProductDetailPage - Page Object Model

Page Object for a specific product's detail page (/products/[id]).
Handles pipeline runs, run pipeline button, and product info.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class ProductDetailPage:

    def __init__(self, browser: BrowserInterface):
        self.browser = browser

    # ==================== LOCATORS ====================

    PRODUCT_NAME = (By.CSS_SELECTOR, "h1")
    RUN_PIPELINE_BUTTON = (By.XPATH, "//button[contains(., 'Dry Run')]")
    DELETE_BUTTON = (By.XPATH, "//button[contains(@class, 'destructive') or .//svg]")
    PIPELINE_RUNS_HEADING = (By.XPATH, "//h2[contains(., 'Pipeline Runs')]")
    NO_RUNS_MESSAGE = (By.XPATH, "//*[contains(., 'No pipeline runs yet')]")
    RUN_CARD = (By.CSS_SELECTOR, "a[href*='/pipeline/']")

    # ==================== NAVIGATION ====================

    def wait_for_page_loaded(self, timeout: int = 15) -> "ProductDetailPage":
        self.browser.wait_for_element_visible(*self.PRODUCT_NAME, timeout=timeout)
        return self

    # ==================== ATOMIC METHODS ====================

    def click_run_pipeline(self) -> "ProductDetailPage":
        self.browser.click(*self.RUN_PIPELINE_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_product_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.PRODUCT_NAME)

    def is_run_pipeline_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.RUN_PIPELINE_BUTTON)

    def has_no_runs(self) -> bool:
        return self.browser.is_element_displayed(*self.NO_RUNS_MESSAGE, timeout=3)

    def has_pipeline_runs(self) -> bool:
        return self.browser.is_element_displayed(*self.RUN_CARD, timeout=3)

    def is_on_product_page(self) -> bool:
        return "/products/" in self.browser.get_current_url()
