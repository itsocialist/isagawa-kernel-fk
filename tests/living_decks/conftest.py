"""
Living Decks — pytest fixtures

Provides: browser, test_presentation_filename
"""

import os
import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from interfaces.browser_interface import BrowserInterface

BASE_URL = "http://localhost:5550"


@pytest.fixture(scope="session")
def browser_driver():
    """Session-scoped Chrome WebDriver."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def browser(browser_driver):
    """Function-scoped BrowserInterface wrapping the session driver."""
    config = {
        "base_url": BASE_URL,
        "explicit_wait": 20,
        "screenshot_dir": "screenshots/living_decks",
        "screenshots_on_failure": True,
    }
    import logging
    logger = logging.getLogger("living_decks_tests")
    bi = BrowserInterface(browser_driver, config, logger)
    yield bi
    # Reset after each test
    browser_driver.delete_all_cookies()


@pytest.fixture(scope="session")
def test_presentation_filename():
    """
    Provides a real presentation filename for editing tests.
    Generates one via the API if the gallery is empty.
    """
    # Check gallery for existing presentations
    try:
        resp = requests.get(f"{BASE_URL}/api/presentations", timeout=10)
        if resp.status_code == 200:
            presentations = resp.json()
            if presentations:
                return presentations[0].get("filename") or presentations[0].get("file")
    except Exception:
        pass

    # Generate a minimal test presentation via the API
    resp = requests.post(
        f"{BASE_URL}/api/generate-full-deck",
        json={
            "prompt": "TDD test deck: three slides on software testing principles",
            "theme": "technical-dark",
            "slideCount": 3,
        },
        timeout=120,
    )
    assert resp.status_code == 200, f"Failed to generate test presentation: {resp.text}"
    data = resp.json()
    filename = data.get("filename") or data.get("file")
    assert filename, f"No filename in generation response: {data}"
    return filename
