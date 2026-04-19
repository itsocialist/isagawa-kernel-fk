"""
PipelineViewPage - Page Object Model

Page Object for the pipeline run view (/products/[id]/pipeline/[runId]).

Updated for the chevron-tab refactor (digitm-gtm commit 84b8805): only
one stage card renders at a time (the selected one), with a chevron
strip for tab-style navigation. Content-calendar gate approval now
includes a post-preview block (digitm-gtm commit 7282b18).
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class PipelineViewPage:

    def __init__(self, browser: BrowserInterface):
        self.browser = browser

    # ==================== LOCATORS ====================

    PIPELINE_HEADING = (By.XPATH, "//h1[contains(., 'Pipeline:')]")

    # The one stage card that owns the content area (chevron-tab refactor)
    SELECTED_STAGE_CARD = (By.CSS_SELECTOR, "div.glass.rounded-lg")

    # Chevron strip — uses aria-label="Pipeline stages" on the <nav>
    CHEVRON_STRIP = (By.CSS_SELECTOR, 'nav[aria-label="Pipeline stages"]')

    # Approval / gate UI — heading is now lowercase "Approval required"
    # (changed in the chevron-tab refactor)
    GATE_SECTION = (
        By.XPATH,
        "//h2[contains(translate(., 'APROVLQUIRED', 'aprovlquired'), 'approval required')]",
    )
    APPROVE_BUTTON = (By.XPATH, "//button[normalize-space(text())='Approve']")
    REJECT_BUTTON = (By.XPATH, "//button[normalize-space(text())='Reject']")
    REJECT_TEXTAREA = (By.CSS_SELECTOR, "textarea[placeholder*='needs to change']")
    REJECT_CONFIRM = (By.XPATH, "//button[contains(., 'Confirm Rejection')]")

    # Content-calendar gate preview (digitm-gtm commit 7282b18)
    PREVIEW_HEADER = (By.XPATH, "//h4[contains(., 'Preview — first')]")
    PREVIEW_CARDS = (
        By.XPATH,
        "//h4[contains(., 'Preview — first')]/../following-sibling::div[1]/div",
    )

    SSE_LOG_TOGGLE = (By.XPATH, "//summary[contains(., 'Live pipeline log')]")

    # ==================== NAVIGATION ====================

    def navigate(self, base_url: str, product_id: str, run_id: str) -> "PipelineViewPage":
        self.browser.navigate_to(f"{base_url}/products/{product_id}/pipeline/{run_id}")
        return self

    def wait_for_page_loaded(self, timeout: int = 15) -> "PipelineViewPage":
        self.browser.wait_for_element_visible(*self.PIPELINE_HEADING, timeout=timeout)
        return self

    # ==================== ATOMIC METHODS ====================

    def click_chevron(self, stage_label: str) -> "PipelineViewPage":
        """
        Click a chevron by its short label (e.g. 'Research', 'Pricing',
        'Assets', 'Content', 'Schedule', 'Listings', 'Feedback').
        Matches the aria-label prefix.
        """
        locator = (
            By.XPATH,
            f"//nav[@aria-label='Pipeline stages']//button[starts-with(@aria-label, '{stage_label} ')]",
        )
        self.browser.click(*locator)
        return self

    def click_approve(self) -> "PipelineViewPage":
        self.browser.click(*self.APPROVE_BUTTON)
        return self

    def click_reject(self) -> "PipelineViewPage":
        self.browser.click(*self.REJECT_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def is_pipeline_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.PIPELINE_HEADING)

    def has_pending_gates(self) -> bool:
        return self.browser.is_element_displayed(*self.GATE_SECTION, timeout=3)

    def is_approve_button_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.APPROVE_BUTTON, timeout=3)

    def has_selected_stage_card(self) -> bool:
        return self.browser.is_element_displayed(*self.SELECTED_STAGE_CARD, timeout=3)

    def has_chevron_strip(self) -> bool:
        return self.browser.is_element_displayed(*self.CHEVRON_STRIP, timeout=3)

    def is_on_pipeline_page(self) -> bool:
        return "/pipeline/" in self.browser.get_current_url()

    # ==================== CONTENT GATE PREVIEW METHODS ====================

    def has_preview_header(self) -> bool:
        """True when the 'Preview — first N of M' block is visible."""
        return self.browser.is_element_displayed(*self.PREVIEW_HEADER, timeout=5)

    def count_preview_cards(self) -> int:
        """Number of post-preview cards rendered in the approval panel."""
        elements = self.browser.find_elements(*self.PREVIEW_CARDS)
        return len(elements)

    def preview_contains_text(self, needle: str) -> bool:
        """True if the preview block contains the given text anywhere."""
        locator = (
            By.XPATH,
            f"//h4[contains(., 'Preview — first')]/../following-sibling::div[1]"
            f"//*[contains(., \"{needle}\")]",
        )
        return self.browser.is_element_displayed(*locator, timeout=3)

    def preview_hashtag_visible(self, tag: str) -> bool:
        """True if a `#tag` marker appears in the preview block.

        Uses `contains` rather than `text()=` because React renders the `#`
        prefix and the tag as one text node in some flows and split in others,
        which makes an exact-text match brittle.
        """
        locator = (
            By.XPATH,
            f"//h4[contains(., 'Preview — first')]/../following-sibling::div[1]"
            f"//*[contains(normalize-space(.), '#{tag}')]",
        )
        return self.browser.is_element_displayed(*locator, timeout=3)
