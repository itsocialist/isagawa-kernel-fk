"""
HostSetupPage - CIQ Jeopardy host game setup screen (/host).

Locator notes (no IDs - using CSS class + text XPath):
  - Pack select: <select class="input">
  - Start button: <button class="btn btn-primary btn-large"> text "Create Game Room"
  - Room code: element with class 'room-code'
  - Controls button: button containing text 'Controls'
"""

from selenium.webdriver.common.by import By
from resources.utilities import autologger


class HostSetupPage:
    """
    Page Object for the Host Setup page (/host).
    """

    # Locators
    PACK_SELECT       = (By.CSS_SELECTOR, "select.input, select")
    PACK_OPTION       = (By.CSS_SELECTOR, "select option")
    ROOM_CODE_DISPLAY = (By.CSS_SELECTOR, ".room-code, [class*='room-code']")
    START_GAME_BTN    = (By.XPATH, "//button[contains(text(),'Create Game') or contains(text(),'Start')]")
    WAITING_HEADER    = (By.XPATH, "//h1[contains(text(),'Waiting')] | //h2[contains(text(),'Waiting')]")
    PLAYER_LIST       = (By.CSS_SELECTOR, ".players-list, .player-list, [class*='player']")
    CONTROLS_BTN      = (By.XPATH, "//button[contains(text(),'Control')]")
    HOST_HEADING      = (By.XPATH, "//h1[contains(text(),'Host') or contains(text(),'Game')]")
    GAME_CODE_SECTION = (By.XPATH, "//*[contains(text(),'Game Code') or contains(text(),'Room Code')]")

    def __init__(self, browser):
        self.browser = browser

    # ── Navigation ────────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def navigate(self):
        """Navigate directly to /host and wait for packs to load."""
        import time
        self.browser.navigate_to(self.browser.config["url"] + "/host")
        time.sleep(2)  # allow React to mount and fetch packs from API

    # ── Actions ───────────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def select_pack_by_name(self, name: str):
        """Select a question pack from the dropdown by visible text."""
        self.browser.select_by_text(*self.PACK_SELECT, text=name)

    @autologger.automation_logger("Page")
    def select_first_available_pack(self):
        """Select the first non-placeholder option in the pack dropdown."""
        packs = self.get_available_packs()
        if packs:
            self.browser.select_by_text(*self.PACK_SELECT, text=packs[0])
            return packs[0]
        return None

    @autologger.automation_logger("Page")
    def click_start_game(self):
        """Click Create Game Room / Start Game."""
        self.browser.click(*self.START_GAME_BTN)

    @autologger.automation_logger("Page")
    def click_open_controls(self):
        """Click Controls button."""
        self.browser.click(*self.CONTROLS_BTN)

    # ── State checks ─────────────────────────────────────────────────────────

    @autologger.automation_logger("Page")
    def is_loaded(self) -> bool:
        """Return True when the host setup heading or pack select is visible."""
        return (self.browser.is_element_displayed(*self.HOST_HEADING) or
                self.browser.is_element_present(*self.PACK_SELECT))

    @autologger.automation_logger("Page")
    def is_in_waiting_room(self) -> bool:
        """Return True when the waiting-room state is active (game code visible)."""
        return (self.browser.is_element_displayed(*self.WAITING_HEADER) or
                self.browser.is_element_displayed(*self.GAME_CODE_SECTION))

    @autologger.automation_logger("Page")
    def get_room_code(self) -> str:
        """Return the displayed room code text."""
        try:
            return self.browser.get_text(*self.ROOM_CODE_DISPLAY).strip()
        except Exception:
            # Fallback: look for 4-char code in page source
            return ""

    @autologger.automation_logger("Page")
    def get_available_packs(self) -> list:
        """Return list of selectable pack names (exclude blank/placeholder options).

        Retries up to 3s to handle async React mount → API fetch timing.
        """
        import time
        deadline = time.time() + 3
        while time.time() < deadline:
            options = self.browser.find_elements(*self.PACK_OPTION)
            packs = [
                o.text for o in options
                if o.text.strip() and o.get_attribute("value") and
                   "choose" not in o.text.lower() and "no pack" not in o.text.lower()
            ]
            if packs:
                return packs
            time.sleep(0.5)
        return []

    @autologger.automation_logger("Page")
    def is_controls_button_visible(self) -> bool:
        """Return True if the Controls button is visible."""
        return self.browser.is_element_displayed(*self.CONTROLS_BTN)

    @autologger.automation_logger("Page")
    def is_daily_double_text_present(self) -> bool:
        """
        Return True if any 'Daily Double' text is present on the page.
        Used to verify Daily Double has been fully removed.
        """
        source = self.browser.get_page_source()
        return "Daily Double" in source or "DAILY DOUBLE" in source
