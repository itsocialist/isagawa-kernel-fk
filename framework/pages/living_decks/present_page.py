"""
PresentPage - Page Object Model

Page Object for the Living Decks presentation viewer (/present or /docs/presentations/*.html).
Handles scroll-snap navigation, slide detection, and fullscreen mode.
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from interfaces.browser_interface import BrowserInterface


class PresentPage:
    """
    Page Object for the presentation viewer.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    BASE_URL = "http://localhost:5550"

    # ==================== LOCATORS ====================

    SLIDES              = (By.CSS_SELECTOR, "section.slide, section[class*='slide']")
    SLIDE_CONTENT       = (By.CSS_SELECTOR, ".slide-content, [class*='slide-content']")
    PRESENTER_CONTROLS  = (By.CSS_SELECTOR, ".presenter-controls, [class*='presenter-controls'], #presenter-controls")
    NEXT_BUTTON         = (By.CSS_SELECTOR, ".next-slide, [data-action='next'], button[title*='Next']")
    PREV_BUTTON         = (By.CSS_SELECTOR, ".prev-slide, [data-action='prev'], button[title*='Prev']")
    SLIDE_COUNTER       = (By.CSS_SELECTOR, ".slide-counter, [class*='slide-counter']")
    FULLSCREEN_BUTTON   = (By.CSS_SELECTOR, ".fullscreen-btn, [data-action='fullscreen']")
    BG_CANVAS           = (By.ID, "bg-canvas")

    def __init__(self, browser: BrowserInterface):
        """Compose BrowserInterface — NO inheritance."""
        self.browser = browser

    # ==================== NAVIGATION ====================

    def navigate_to_file(self, filename: str) -> "PresentPage":
        self.browser.navigate_to(f"{self.BASE_URL}/docs/presentations/{filename}")
        return self

    def navigate_to_present(self, filename: str = "") -> "PresentPage":
        url = f"{self.BASE_URL}/present"
        if filename:
            url += f"?file={filename}"
        self.browser.navigate_to(url)
        return self

    # ==================== ACTIONS ====================

    def press_arrow_down(self) -> "PresentPage":
        self.browser.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
        return self

    def press_arrow_up(self) -> "PresentPage":
        self.browser.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_UP)
        return self

    def click_next(self) -> "PresentPage":
        self.browser.click(*self.NEXT_BUTTON)
        return self

    def click_prev(self) -> "PresentPage":
        self.browser.click(*self.PREV_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS ====================

    def count_slides(self) -> int:
        return len(self.browser.find_elements(*self.SLIDES))

    def is_bg_canvas_rendered(self) -> bool:
        return self.browser.is_element_displayed(*self.BG_CANVAS)

    def get_slide_counter_text(self) -> str:
        return self.browser.get_text(*self.SLIDE_COUNTER)

    def are_presenter_controls_visible(self) -> bool:
        return self.browser.is_element_displayed(*self.PRESENTER_CONTROLS)

    def get_first_slide_h1(self) -> str:
        slides = self.browser.find_elements(*self.SLIDES)
        try:
            return slides[0].find_element(By.TAG_NAME, "h1").text
        except Exception:
            return ""
