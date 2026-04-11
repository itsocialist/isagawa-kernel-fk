"""
DashboardPage - Page Object Model

Page Object for the Digitm GTM dashboard (/dashboard).
Handles product list, pending gates, and navigation sidebar.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class DashboardPage:

    def __init__(self, browser: BrowserInterface):
        self.browser = browser

    # ==================== LOCATORS ====================

    HEADING = (By.XPATH, "//h1[contains(., 'Dashboard')]")
    SIDEBAR_BRAND = (By.XPATH, "//aside//a[contains(., 'Digitm GTM')]")
    NAV_DASHBOARD = (By.XPATH, "//aside//a[contains(., 'Dashboard')]")
    NAV_PRODUCTS = (By.XPATH, "//aside//a[contains(., 'Products')]")
    NAV_CALENDAR = (By.XPATH, "//aside//a[contains(., 'Calendar')]")
    NAV_ANALYTICS = (By.XPATH, "//aside//a[contains(., 'Analytics')]")
    NAV_SETTINGS = (By.XPATH, "//aside//a[contains(., 'Settings')]")
    NEW_PRODUCT_BUTTON = (By.XPATH, "//a[contains(., 'New Product')]")
    GATE_ALERT = (By.XPATH, "//div[contains(., 'pending review')]")
    EMPTY_STATE = (By.XPATH, "//h3[contains(., 'No products yet')]")
    PRODUCT_CARD = (By.CSS_SELECTOR, "a[href^='/products/']")

    # ==================== NAVIGATION ====================

    def navigate(self, url: str) -> "DashboardPage":
        self.browser.navigate_to(url + "/dashboard")
        return self

    def wait_for_page_loaded(self, timeout: int = 15) -> "DashboardPage":
        self.browser.wait_for_element_visible(*self.HEADING, timeout=timeout)
        return self

    # ==================== ATOMIC METHODS ====================

    def click_new_product(self) -> "DashboardPage":
        self.browser.click(*self.NEW_PRODUCT_BUTTON)
        return self

    def click_nav_products(self) -> "DashboardPage":
        self.browser.click(*self.NAV_PRODUCTS)
        return self

    def click_nav_settings(self) -> "DashboardPage":
        self.browser.click(*self.NAV_SETTINGS)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_dashboard_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.HEADING)

    def is_sidebar_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.SIDEBAR_BRAND)

    def has_pending_gates(self) -> bool:
        return self.browser.is_element_displayed(*self.GATE_ALERT, timeout=3)

    def is_empty_state(self) -> bool:
        return self.browser.is_element_displayed(*self.EMPTY_STATE, timeout=3)

    def has_products(self) -> bool:
        return self.browser.is_element_displayed(*self.PRODUCT_CARD, timeout=3)

    def is_on_dashboard(self) -> bool:
        return "/dashboard" in self.browser.get_current_url()
