"""
LandingPage - Page Object Model

Page Object for the Digitm GTM landing page (/).
Handles hero section, feature grid, and sign-in CTA.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class LandingPage:

    def __init__(self, browser: BrowserInterface):
        self.browser = browser

    # ==================== LOCATORS ====================

    HERO_HEADING = (By.XPATH, "//h1[contains(., 'One product spec')]")
    HERO_SUBTEXT = (By.XPATH, "//p[contains(., 'Digitm GTM runs your go-to-market')]")
    GET_STARTED_BUTTON = (By.XPATH, "//a[contains(., 'Launch Your First Product')]")
    DASHBOARD_BUTTON = (By.XPATH, "//a[contains(., 'Dashboard')]")
    FEATURE_PIPELINE = (By.XPATH, "//h3[contains(., '7-Stage Pipeline')]")
    FEATURE_AI = (By.XPATH, "//h3[contains(., 'AI-Powered')]")
    FEATURE_FEEDBACK = (By.XPATH, "//h3[contains(., 'Weekly Feedback')]")
    FEATURE_HITL = (By.XPATH, "//h3[contains(., 'Human-in-the-Loop')]")
    FOOTER = (By.XPATH, "//footer[contains(., 'Edge Bird Systems')]")
    BRAND_NAME = (By.XPATH, "//span[contains(., 'Digitm GTM')]")

    # ==================== NAVIGATION ====================

    def navigate(self, url: str) -> "LandingPage":
        self.browser.navigate_to(url)
        return self

    def wait_for_page_loaded(self, timeout: int = 15) -> "LandingPage":
        self.browser.wait_for_element_visible(*self.HERO_HEADING, timeout=timeout)
        return self

    # ==================== ATOMIC METHODS ====================

    def click_get_started(self) -> "LandingPage":
        self.browser.click(*self.GET_STARTED_BUTTON)
        return self

    def click_dashboard(self) -> "LandingPage":
        self.browser.click(*self.DASHBOARD_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_hero_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.HERO_HEADING)

    def is_hero_subtext_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.HERO_SUBTEXT)

    def is_brand_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.BRAND_NAME)

    def is_get_started_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.GET_STARTED_BUTTON)

    def are_features_displayed(self) -> bool:
        return (
            self.browser.is_element_displayed(*self.FEATURE_PIPELINE) and
            self.browser.is_element_displayed(*self.FEATURE_AI) and
            self.browser.is_element_displayed(*self.FEATURE_FEEDBACK) and
            self.browser.is_element_displayed(*self.FEATURE_HITL)
        )

    def is_footer_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.FOOTER)

    def is_on_landing_page(self) -> bool:
        url = self.browser.get_current_url()
        return url.endswith("/") or url.endswith(":3000")
