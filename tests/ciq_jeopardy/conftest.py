"""
conftest.py — CIQ Jeopardy multi-browser fixtures.

Provides function-scoped browser fixtures that allow a single test
to drive multiple simultaneous browser instances (host + players).

Fixtures:
    host_session      - single host browser + pages
    player_session    - single player browser + pages
    two_player_session - host + 2 player browsers in one dict
"""

import json
import logging
import pytest
from pathlib import Path

# Framework path is already on sys.path via the parent conftest, but add
# it explicitly here so this conftest works when run in isolation too.
import sys
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
if FRAMEWORK_PATH not in sys.path:
    sys.path.insert(0, FRAMEWORK_PATH)

from resources.chromedriver.driver import create_driver
from interfaces.browser_interface import BrowserInterface
from pages.ciq_jeopardy.home_page import HomePage
from pages.ciq_jeopardy.host_setup_page import HostSetupPage
from pages.ciq_jeopardy.game_board_page import GameBoardPage
from pages.ciq_jeopardy.player_page import PlayerPage
from roles.ciq_jeopardy.host_role import HostRole
from roles.ciq_jeopardy.player_role import PlayerRole


logger = logging.getLogger("CIQJeopardyMultiplayer")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_config(request) -> dict:
    """Load environment config for the current --env selection."""
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / "framework" / "resources" / "config" / "environment_config.json"
    env_id = request.config.getoption("--env")
    with open(config_path, "r", encoding="utf-8") as f:
        environments = json.load(f)
    if env_id not in environments:
        raise ValueError(f"Unknown env: {env_id}")
    return environments[env_id]


def _make_session(request, cfg: dict) -> dict:
    """
    Create a fresh browser session and wire up all CIQ Jeopardy page objects.
    Returns a dict with keys: browser, home, setup, board, driver.
    Registers auto-teardown via request.addfinalizer.
    """
    headless = request.config.getoption("--headless")
    browser_type = request.config.getoption("--browser")
    drv = create_driver(headless=headless, browser=browser_type)

    def _quit():
        try:
            drv.quit()
        except Exception:
            pass
    request.addfinalizer(_quit)

    b = BrowserInterface(drv, cfg, logger)
    return {
        "browser": b,
        "driver": drv,
        "home":   HomePage(b),
        "setup":  HostSetupPage(b),
        "board":  GameBoardPage(b),
    }


def _make_player_session(request, cfg: dict) -> dict:
    """
    Create a fresh player browser session.
    Returns a dict with keys: browser, player_page, player_role, driver.
    """
    headless = request.config.getoption("--headless")
    browser_type = request.config.getoption("--browser")
    drv = create_driver(headless=headless, browser=browser_type)

    def _quit():
        try:
            drv.quit()
        except Exception:
            pass
    request.addfinalizer(_quit)

    b = BrowserInterface(drv, cfg, logger)
    return {
        "browser":      b,
        "driver":       drv,
        "player_page":  PlayerPage(b),
        "player_role":  PlayerRole(b),
    }


# ---------------------------------------------------------------------------
# Function-scoped fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def host_session(request):
    """
    A dedicated browser session wired up as the host.

    Usage:
        def test_something(host_session):
            host_session["setup"].navigate()
    """
    cfg = _load_config(request)
    return _make_session(request, cfg)


@pytest.fixture(scope="function")
def player_session(request):
    """
    A dedicated browser session wired up as a single player.

    Usage:
        def test_something(player_session):
            player_session["player_page"].navigate()
    """
    cfg = _load_config(request)
    return _make_player_session(request, cfg)


@pytest.fixture(scope="function")
def two_player_session(request):
    """
    Three simultaneous browser sessions: one host + two players.

    Returns a dict:
        {
          "host":     { browser, home, setup, board },
          "player1":  { browser, player_page, player_role },
          "player2":  { browser, player_page, player_role },
        }

    All three drivers are auto-quit after the test via finalizers.
    """
    cfg = _load_config(request)
    return {
        "host":    _make_session(request, cfg),
        "player1": _make_player_session(request, cfg),
        "player2": _make_player_session(request, cfg),
    }
