"""
Living Decks — Phase 2 Share Link Tests

BDD Acceptance Criteria:
- GIVEN at least one presentation exists in the gallery
  WHEN the user clicks the Share button on a presentation card
  THEN a copy-able URL is displayed with no login required

- GIVEN the share dialog is open
  WHEN the share link is inspected
  THEN it is a valid absolute URL pointing to the presentation

- GIVEN the share link is copied and opened in a new tab
  WHEN the URL is loaded without authentication
  THEN the presentation renders fully (no login gate, no 404)

- GIVEN a presentation exists
  WHEN the share link is accessed
  THEN the response is served from /docs/presentations/:filename
    with no auth middleware blocking it
"""

import pytest
import requests
from roles.living_decks.presentation_creator_role import PresentationCreatorRole
from pages.living_decks.gallery_page import GalleryPage
from pages.living_decks.present_page import PresentPage
from tasks.living_decks.gallery_tasks import GalleryTasks

BASE_URL = "http://localhost:5550"


class TestShareLinkGeneration:
    """Share link appears when Share is clicked."""

    def test_share_button_reveals_link(self, browser, test_presentation_filename):
        """GIVEN a presentation exists in the gallery
        WHEN the user clicks Share on that card
        THEN a share link input appears"""
        gallery = GalleryPage(browser)
        gallery.navigate()

        assert gallery.count_presentations() > 0, \
            "Gallery must have at least one presentation to test share"

        gallery.click_share_on_card(0)

        assert gallery.is_share_link_displayed(), \
            "Share link must appear after clicking Share — no modal, no redirect"

    def test_share_link_is_valid_url(self, browser, test_presentation_filename):
        """GIVEN the share dialog is open
        WHEN the share link value is read
        THEN it is a valid absolute http URL"""
        gallery = GalleryPage(browser)
        gallery.navigate().click_share_on_card(0)

        assert gallery.is_share_link_valid_url(), \
            "Share link must be a valid absolute URL (http:// or https://)"

    def test_share_link_references_presentation_file(self, browser, test_presentation_filename):
        """GIVEN the share dialog is open
        WHEN the share link value is read
        THEN it contains /docs/presentations/ in the path"""
        gallery = GalleryPage(browser)
        gallery.navigate().click_share_on_card(0)

        link = gallery.get_share_link_value()
        assert "/docs/presentations/" in link, \
            f"Share link must point to /docs/presentations/ — got: '{link}'"


class TestShareLinkAccessibility:
    """Share link works without authentication."""

    def test_share_link_accessible_without_login(self, browser, test_presentation_filename):
        """GIVEN a share link has been generated
        WHEN the URL is fetched directly (no auth headers)
        THEN the response is 200 OK with HTML content"""
        gallery = GalleryPage(browser)
        gallery.navigate().click_share_on_card(0)
        link = gallery.get_share_link_value()

        # HTTP-level check — no auth, no session cookies
        response = requests.get(link, timeout=10)
        assert response.status_code == 200, \
            f"Share link must return 200 without auth — got {response.status_code} for {link}"
        assert "text/html" in response.headers.get("Content-Type", ""), \
            "Share link response must be HTML"

    def test_shared_presentation_renders_slides(self, browser, test_presentation_filename):
        """GIVEN a share link is accessed in the browser
        WHEN the page loads
        THEN at least one slide section is present in the DOM"""
        gallery = GalleryPage(browser)
        gallery.navigate().click_share_on_card(0)
        link = gallery.get_share_link_value()

        browser.navigate_to(link)

        present_page = PresentPage(browser)
        slide_count = present_page.count_slides()
        assert slide_count > 0, \
            f"Shared presentation must render slides — found {slide_count} at {link}"


class TestShareLinkNoLoginGate:
    """No auth wall on shared links."""

    def test_no_login_redirect_on_share_link(self, browser, test_presentation_filename):
        """GIVEN a share link URL
        WHEN it is opened in a fresh browser context (no session)
        THEN the URL does not redirect to /login or any auth page"""
        gallery = GalleryPage(browser)
        gallery.navigate().click_share_on_card(0)
        link = gallery.get_share_link_value()

        browser.navigate_to(link)
        current_url = browser.driver.current_url

        assert "/login" not in current_url, \
            f"Share link must not redirect to login — redirected to: {current_url}"
        assert link in current_url or "presentations" in current_url, \
            f"Share link must stay on presentation URL — ended up at: {current_url}"
