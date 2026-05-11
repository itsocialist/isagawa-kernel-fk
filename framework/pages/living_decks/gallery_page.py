"""
GalleryPage - Page Object Model

Page Object for the Living Decks presentation gallery (/gallery).
Handles browsing, filtering, sharing, presenting, and deleting presentations.
"""

from selenium.webdriver.common.by import By
from interfaces.browser_interface import BrowserInterface


class GalleryPage:
    """
    Page Object for the gallery interface.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    BASE_URL = "http://localhost:5550"

    # ==================== LOCATORS ====================

    PRESENTATION_CARDS    = (By.CSS_SELECTOR, ".gallery-card, .presentation-card, [class*='deck-card'], [class*='gallery-item']")
    CARD_TITLE            = (By.CSS_SELECTOR, ".card-title, .deck-title, h3, h4")
    SHARE_BUTTON          = (By.CSS_SELECTOR, "[data-action='share'], .share-btn, button[title*='Share']")
    PRESENT_BUTTON        = (By.CSS_SELECTOR, "[data-action='present'], .present-btn, button[title*='Present']")
    EDIT_BUTTON           = (By.CSS_SELECTOR, "[data-action='edit'], .edit-btn, button[title*='Edit']")
    DELETE_BUTTON         = (By.CSS_SELECTOR, "[data-action='delete'], .delete-btn, button[title*='Delete']")
    SHARE_LINK_INPUT      = (By.CSS_SELECTOR, ".share-link, input[readonly][value*='localhost'], [class*='share-url']")
    FILTER_ALL            = (By.CSS_SELECTOR, "[data-filter='all'], .filter-btn.active")
    FILTER_BUTTONS        = (By.CSS_SELECTOR, ".filter-btn, [data-filter]")
    EMPTY_STATE           = (By.CSS_SELECTOR, ".empty-state, [class*='no-presentations'], [class*='empty']")
    COPY_LINK_BUTTON      = (By.CSS_SELECTOR, ".copy-link, [data-action='copy'], button[title*='Copy']")

    def __init__(self, browser: BrowserInterface):
        """Compose BrowserInterface — NO inheritance."""
        self.browser = browser

    # ==================== NAVIGATION ====================

    def navigate(self) -> "GalleryPage":
        self.browser.navigate_to(f"{self.BASE_URL}/gallery")
        return self

    # ==================== ACTIONS ====================

    def click_share_on_card(self, index: int = 0) -> "GalleryPage":
        """Click Share on the nth presentation card."""
        cards = self.browser.find_elements(*self.PRESENTATION_CARDS)
        share_btn = cards[index].find_element(*self.SHARE_BUTTON)
        share_btn.click()
        return self

    def click_edit_on_card(self, index: int = 0) -> "GalleryPage":
        cards = self.browser.find_elements(*self.PRESENTATION_CARDS)
        edit_btn = cards[index].find_element(*self.EDIT_BUTTON)
        edit_btn.click()
        return self

    def click_present_on_card(self, index: int = 0) -> "GalleryPage":
        cards = self.browser.find_elements(*self.PRESENTATION_CARDS)
        present_btn = cards[index].find_element(*self.PRESENT_BUTTON)
        present_btn.click()
        return self

    def click_delete_on_card(self, index: int = 0) -> "GalleryPage":
        cards = self.browser.find_elements(*self.PRESENTATION_CARDS)
        delete_btn = cards[index].find_element(*self.DELETE_BUTTON)
        delete_btn.click()
        return self

    def click_copy_link(self) -> "GalleryPage":
        self.browser.click(*self.COPY_LINK_BUTTON)
        return self

    def click_filter(self, filter_name: str) -> "GalleryPage":
        """Click filter button matching filter_name."""
        buttons = self.browser.find_elements(*self.FILTER_BUTTONS)
        for btn in buttons:
            if filter_name.lower() in btn.text.lower() or btn.get_attribute("data-filter") == filter_name:
                btn.click()
                break
        return self

    # ==================== STATE-CHECK METHODS ====================

    def count_presentations(self) -> int:
        return len(self.browser.find_elements(*self.PRESENTATION_CARDS))

    def is_empty(self) -> bool:
        return self.browser.is_element_displayed(*self.EMPTY_STATE)

    def get_card_title(self, index: int = 0) -> str:
        cards = self.browser.find_elements(*self.PRESENTATION_CARDS)
        return cards[index].find_element(*self.CARD_TITLE).text

    def is_share_link_displayed(self) -> bool:
        return self.browser.is_element_displayed(*self.SHARE_LINK_INPUT)

    def get_share_link_value(self) -> str:
        return self.browser.get_attribute(*self.SHARE_LINK_INPUT, attribute="value")

    def is_share_link_valid_url(self) -> bool:
        value = self.get_share_link_value()
        return value.startswith("http://") or value.startswith("https://")
