"""
BoothCall Test Configuration

Provides auth session injection for auth-gated tests.
Injects the NextAuth session cookie into the Selenium browser
at session start, before any tests run.
"""

import subprocess
import json
import logging
import os
import pytest
from pathlib import Path

logger = logging.getLogger("BoothCall")

# Path to the BoothCall project for session extraction
BOOTHCALL_PROJECT = Path(__file__).parent.parent.parent.parent / "booth-call"


def _extract_session_token() -> str | None:
    """
    Extract active session token from BoothCall database.

    Runs the get-session.ts script in the booth-call project
    and returns the session token string if found.
    """
    # Check for env override first (for CI/CD)
    env_token = os.environ.get("BOOTHCALL_SESSION_TOKEN")
    if env_token:
        logger.info("Using session token from BOOTHCALL_SESSION_TOKEN env var")
        return env_token

    script_path = BOOTHCALL_PROJECT / "scripts" / "get-session.ts"
    if not script_path.exists():
        logger.warning(f"Session extraction script not found: {script_path}")
        return None

    try:
        # Source nvm to get node/npx in PATH
        shell_cmd = (
            f'export NVM_DIR="$HOME/.nvm" && '
            f'[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && '
            f'npx tsx {script_path}'
        )
        result = subprocess.run(
            ["zsh", "-c", shell_cmd],
            capture_output=True,
            text=True,
            cwd=str(BOOTHCALL_PROJECT),
            timeout=30,
        )
        if result.returncode != 0:
            logger.warning(f"Session extraction failed: {result.stderr[:300]}")
            return None

        sessions = json.loads(result.stdout.strip())
        if sessions and len(sessions) > 0:
            return sessions[0]["sessionToken"]
        return None
    except Exception as e:
        logger.warning(f"Session extraction error: {repr(e)}")
        return None


@pytest.fixture(scope="session", autouse=True)
def inject_boothcall_session(driver, config):
    """
    Session-scoped fixture that injects the BoothCall auth cookie
    into the Selenium browser before any tests run.

    NextAuth v5 stores the session token in `authjs.session-token` cookie.
    """
    base_url = config.get("url", "")

    token = _extract_session_token()
    if not token:
        logger.warning("No active session found — auth-gated tests will be skipped")
        yield
        return

    logger.info(f"Injecting session token: {token[:8]}...")

    # Navigate to the domain first (cookies require a domain context)
    driver.get(base_url)

    import time
    time.sleep(1)

    # Inject the NextAuth session cookie
    driver.add_cookie({
        "name": "authjs.session-token",
        "value": token,
        "path": "/",
        "httpOnly": True,
        "secure": False,  # localhost doesn't use HTTPS
        "sameSite": "Lax",
    })

    # Navigate to /events to verify auth worked
    driver.get(base_url + "/events")
    time.sleep(2)

    current_url = driver.current_url
    if "/login" not in current_url:
        logger.info(f"✅ Auth injection successful — on: {current_url}")
    else:
        logger.warning("⚠️ Auth injection failed — still on login page")

    yield
