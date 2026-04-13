"""
PipelineViewPage - Page Object Model

Page Object for the pipeline run view (/products/[id]/pipeline/[runId]).
Handles stage track, gate review, and artifacts viewer.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class PipelineViewPage:

    def __init__(self, browser: BrowserInterface):
        self.browser = browser

    # ==================== LOCATORS ====================

    PIPELINE_HEADING = (By.XPATH, "//h1[contains(., 'Pipeline:')]")
    STAGE_CARD = (By.CSS_SELECTOR, "div.glass.rounded-lg")
    GATE_SECTION = (By.XPATH, "//h2[contains(., 'Approval Required')]")
    APPROVE_BUTTON = (By.XPATH, "//button[contains(., 'Approve')]")
    REJECT_BUTTON = (By.XPATH, "//button[contains(., 'Reject')]")
    ARTIFACTS_TOGGLE = (By.XPATH, "//summary[contains(., 'View artifacts')]")
    SSE_LOG_TOGGLE = (By.XPATH, "//summary[contains(., 'Live pipeline log')]")
    STATUS_COMPLETED = (By.XPATH, "//*[contains(., 'completed')]")
    STATUS_RUNNING = (By.XPATH, "//*[contains(@class, 'animate-spin')]")

    # ==================== NAVIGATION ====================

    def wait_for_page_loaded(self, timeout: int = 15) -> "PipelineViewPage":
        self.browser.wait_for_element_visible(*self.PIPELINE_HEADING, timeout=timeout)
        return self

    # ==================== ATOMIC METHODS ====================

    def click_approve(self) -> "PipelineViewPage":
        self.browser.click(*self.APPROVE_BUTTON)
        return self

    def click_reject(self) -> "PipelineViewPage":
        self.browser.click(*self.REJECT_BUTTON)
        return self

    def expand_artifacts(self) -> "PipelineViewPage":
        self.browser.click(*self.ARTIFACTS_TOGGLE)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_pipeline_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.PIPELINE_HEADING)

    def has_pending_gates(self) -> bool:
        return self.browser.is_element_displayed(*self.GATE_SECTION, timeout=3)

    def is_approve_button_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.APPROVE_BUTTON, timeout=3)

    def has_stage_cards(self) -> bool:
        return self.browser.is_element_displayed(*self.STAGE_CARD, timeout=3)

    def is_pipeline_running(self) -> bool:
        return self.browser.is_element_displayed(*self.STATUS_RUNNING, timeout=3)

    def is_on_pipeline_page(self) -> bool:
        return "/pipeline/" in self.browser.get_current_url()
