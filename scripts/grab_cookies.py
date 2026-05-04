#!/usr/bin/env python3
"""
grab_cookies.py — Chrome Cookie Extractor for Selenium Auth
============================================================
Reads encrypted Supabase session cookies directly from your local Chrome
profile and outputs them as JSON for use with the Selenium smoke suite.

Usage:
  # Print cookies as JSON (pipe to env var)
  python3 scripts/grab_cookies.py --domain speakerhero.app

  # Run the full test suite immediately using the extracted cookies
  python3 scripts/grab_cookies.py --domain speakerhero.app --run-tests

  # Custom env / browser profile
  python3 scripts/grab_cookies.py --domain speakerhero.app --env sales_sim_prod --profile "Profile 1"

How it works:
  1. Copies Chrome's Cookies SQLite DB to /tmp (Chrome locks it while open)
  2. Queries all cookies for the target domain
  3. Decrypts cookie values using AES-128-CBC + PBKDF2 key from macOS Keychain
  4. Outputs JSON array compatible with Selenium's driver.add_cookie()

Requirements:
  - macOS only (uses 'security' CLI for Keychain access)
  - Chrome must be installed (or pass --profile path to any Chromium-based browser)
  - pip install cryptography  (already in platform-selenium venv)

Notes:
  - Chrome must not have the Cookies DB locked exclusively — if it is, close Chrome
    or the script uses a temp copy so it usually works fine either way.
  - Only sb-* (Supabase) cookies are extracted by default. Pass --all-cookies
    to extract every cookie for the domain.
"""

import os
import re
import sys
import json
import time
import base64
import shutil
import sqlite3
import hashlib
import subprocess
import tempfile
import argparse
import urllib.request
from pathlib import Path

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    from cryptography.hazmat.backends import default_backend
except ImportError:
    sys.exit("ERROR: 'cryptography' not installed. Run: pip install cryptography")


# ── Constants ──────────────────────────────────────────────────────────────────

CHROME_PROFILES_DIR = Path.home() / "Library/Application Support/Google/Chrome"
DEFAULT_PROFILE     = "Default"
KEYCHAIN_SERVICE    = "Chrome Safe Storage"
KEYCHAIN_ACCOUNT    = "Chrome"
PBKDF2_ITERATIONS   = 1003
PBKDF2_KEY_LEN      = 16
PBKDF2_SALT         = b"saltysalt"
AES_IV              = b" " * 16  # 16 spaces


# ── Keychain ───────────────────────────────────────────────────────────────────

COOKIE_CACHE_FILE = Path.home() / ".speakerhero_cookies.json"
CACHE_MAX_AGE_SEC = 50 * 60  # 50 minutes — just under Supabase's 1h JWT lifetime


def load_cookie_cache(domain: str) -> list[dict] | None:
    """Return cached cookies if the cache file exists and is fresh."""
    if not COOKIE_CACHE_FILE.exists():
        return None
    try:
        data = json.loads(COOKIE_CACHE_FILE.read_text())
        if data.get("domain") != domain:
            return None
        age = time.time() - data.get("saved_at", 0)
        if age > CACHE_MAX_AGE_SEC:
            print(f"  (Cache expired {age/3600:.1f}h ago — re-extracting from Chrome)")
            return None
        print(f"  (Using cached cookies from {COOKIE_CACHE_FILE} — {age/60:.0f}m old)")
        return data["cookies"]
    except Exception:
        return None


def save_cookie_cache(domain: str, cookies: list[dict]) -> None:
    try:
        COOKIE_CACHE_FILE.write_text(json.dumps({
            "domain": domain,
            "saved_at": time.time(),
            "cookies": cookies,
        }, indent=2))
        COOKIE_CACHE_FILE.chmod(0o600)  # owner-only read
    except Exception as e:
        print(f"  (Warning: could not cache cookies — {e})")

def try_refresh_session(cookies: list[dict], supabase_url: str, anon_key: str) -> list[dict] | None:
    """
    Attempt to refresh an expired Supabase session via the REST API.
    First decodes the session to check expires_at — if still valid, returns None (no-op).
    Only calls Supabase when the access token is within 5 minutes of expiry.
    Returns updated cookie list on successful refresh, None otherwise.
    """
    try:
        # Reassemble split sb-* cookies and decode session JSON
        parts = {c["name"]: c["value"] for c in cookies if c["name"].startswith("sb-")}
        base_key = None
        for name in parts:
            base_key = name.rsplit(".", 1)[0] if "." in name else name
            break
        if not base_key:
            return None

        tok0 = parts.get(f"{base_key}.0", "").replace("base64-", "")
        tok1 = parts.get(f"{base_key}.1", "")
        combined = tok0 + tok1
        pad = len(combined) % 4
        if pad:
            combined += "=" * (4 - pad)
        session = json.loads(base64.b64decode(combined).decode("utf-8", errors="replace"))
        refresh_token = session.get("refresh_token", "")
        if not refresh_token:
            return None

        # ── Guard: skip refresh if access token is still valid ────────
        expires_at = session.get("expires_at", 0)
        remaining_sec = expires_at - time.time()
        if remaining_sec > 300:  # more than 5 minutes left — token is fine
            print(f"  (Token valid for {remaining_sec/60:.0f}m — no refresh needed)")
            return None

        print(f"  (Token expired {-remaining_sec/60:.0f}m ago — attempting Supabase refresh...)")
        payload = json.dumps({"refresh_token": refresh_token}).encode()
        req = urllib.request.Request(
            f"{supabase_url}/auth/v1/token?grant_type=refresh_token",
            data=payload,
            headers={"Content-Type": "application/json", "apikey": anon_key, "Authorization": f"Bearer {anon_key}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            new_session = json.loads(resp.read())

        new_exp = new_session.get("expires_at", 0)
        print(f"  (Refresh ✅ — new token valid for {(new_exp - time.time())/60:.0f}m)")

        # Re-encode the new session as split Supabase cookies
        encoded = "base64-" + base64.b64encode(json.dumps(new_session).encode()).decode()
        CHUNK = 3000
        domain = cookies[0]["domain"]
        secure = cookies[0].get("secure", False)
        return [
            {"name": f"{base_key}.0", "value": encoded[:CHUNK],  "domain": domain, "path": "/", "secure": secure, "httpOnly": False},
            {"name": f"{base_key}.1", "value": encoded[CHUNK:],  "domain": domain, "path": "/", "secure": secure, "httpOnly": False},
        ]
    except Exception as e:
        print(f"  (Refresh failed: {e} — need fresh login)")
        return None


def get_chrome_encryption_key() -> bytes:
    """Fetch Chrome's encryption password from macOS Keychain and derive the AES key."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-w", "-s", KEYCHAIN_SERVICE, "-a", KEYCHAIN_ACCOUNT],
            capture_output=True, text=True, check=True
        )
        password = result.stdout.strip().encode("utf-8")
    except subprocess.CalledProcessError:
        sys.exit(
            "ERROR: Could not read Chrome Safe Storage from Keychain.\n"
            "Make sure Chrome has been opened at least once on this Mac.\n"
            "If the dialog appeared and you clicked Allow, re-run — it may need one more confirmation."
        )

    key = hashlib.pbkdf2_hmac("sha1", password, PBKDF2_SALT, PBKDF2_ITERATIONS, dklen=PBKDF2_KEY_LEN)
    return key


# ── Decryption ─────────────────────────────────────────────────────────────────

def decrypt_cookie_value(encrypted_value: bytes, key: bytes) -> str:
    """
    Decrypt a Chrome v10 encrypted cookie value.
    Format: b'v10' + AES-128-CBC ciphertext

    After decryption, Chrome prepends a 32-byte nonce/prefix that must be
    stripped to get the actual cookie string value.
    """
    if not encrypted_value:
        return ""

    # v10 prefix means AES-128-CBC encrypted
    if encrypted_value[:3] == b"v10":
        ciphertext = encrypted_value[3:]
        cipher = Cipher(
            algorithms.AES(key),
            modes.CBC(AES_IV),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(ciphertext) + decryptor.finalize()

        # Remove PKCS7 padding
        pad_len = decrypted[-1]
        if 1 <= pad_len <= 16:
            decrypted = decrypted[:-pad_len]

        # Chrome prepends a 32-byte nonce prefix — strip everything before
        # the first printable ASCII sequence (the real value starts there)
        raw = decrypted.decode("utf-8", errors="replace")

        # Find where the actual cookie value begins (first printable run)
        match = re.search(r'[\x20-\x7E]{4,}', raw)
        if match:
            return raw[match.start():]
        return raw

    # Unencrypted (older Chrome or dev builds)
    return encrypted_value.decode("utf-8", errors="replace")


# ── Cookie Extraction ──────────────────────────────────────────────────────────

def extract_cookies(
    domain: str,
    profile: str = DEFAULT_PROFILE,
    supabase_only: bool = True,
    refresh: bool = False,
) -> list[dict]:
    """
    Extract and decrypt cookies for the given domain.
    Checks cache first (50m TTL) to avoid repeated Keychain prompts.
    Returns a list of dicts compatible with Selenium's driver.add_cookie().
    """
    # Cache check — skip Keychain entirely if we have fresh cookies
    if not refresh:
        cached = load_cookie_cache(domain)
        if cached:
            return cached

    cookies_db = CHROME_PROFILES_DIR / profile / "Cookies"
    if not cookies_db.exists():
        sys.exit(
            f"ERROR: Chrome Cookies DB not found at {cookies_db}\n"
            f"Check that Chrome is installed and you've used it at least once.\n"
            f"For a different profile, pass --profile 'Profile 1' etc."
        )

    key = get_chrome_encryption_key()

    # Copy to temp to avoid SQLite locking issues while Chrome is open
    with tempfile.NamedTemporaryFile(suffix=".cookies.db", delete=False) as tmp:
        tmp_path = tmp.name

    shutil.copy2(cookies_db, tmp_path)

    results = []
    try:
        conn = sqlite3.connect(tmp_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, encrypted_value, path, host_key, expires_utc, is_secure, is_httponly
            FROM cookies
            WHERE host_key = ? OR host_key = ?
            ORDER BY name
        """, (domain, f".{domain}"))

        for name, encrypted_value, path, host_key, expires_utc, is_secure, is_httponly in cursor.fetchall():
            if supabase_only and not name.startswith("sb-"):
                continue
            value = decrypt_cookie_value(encrypted_value, key)
            if not value:
                continue
            results.append({
                "name":     name,
                "value":    value,
                "domain":   host_key if host_key.startswith(".") else domain,
                "path":     path or "/",
                "secure":   bool(is_secure),
                "httpOnly": bool(is_httponly),
            })

        conn.close()
    finally:
        os.unlink(tmp_path)

    # Save to cache so next run skips Keychain
    if results:
        save_cookie_cache(domain, results)

    return results


# ── Test Runner ────────────────────────────────────────────────────────────────

def run_tests(cookies: list[dict], env: str) -> int:
    """Run the sales_sim Selenium suite with the extracted cookies injected."""
    cookies_json = json.dumps(cookies)
    env_vars = os.environ.copy()
    env_vars["SPEAKERHERO_COOKIES"] = cookies_json

    cmd = [
        sys.executable, "-m", "pytest",
        "tests/sales_sim/",
        f"--env={env}",
        "-v",
    ]

    print(f"\n▶  Running: {' '.join(cmd)}")
    print(f"   Injecting {len(cookies)} cookie(s) for auth\n")

    result = subprocess.run(cmd, env=env_vars)
    return result.returncode


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Extract Chrome cookies for a domain and use them for Selenium auth"
    )
    parser.add_argument(
        "--domain", default="speakerhero.app",
        help="Domain to extract cookies for (default: speakerhero.app)"
    )
    parser.add_argument(
        "--profile", default=DEFAULT_PROFILE,
        help="Chrome profile folder name (default: Default). E.g. 'Profile 1'"
    )
    parser.add_argument(
        "--env", default="sales_sim_prod",
        help="Pytest --env value (default: sales_sim_prod)"
    )
    parser.add_argument(
        "--run-tests", action="store_true",
        help="Run the Selenium suite immediately after extracting cookies"
    )
    parser.add_argument(
        "--all-cookies", action="store_true",
        help="Extract all cookies for the domain, not just sb-* (Supabase) ones"
    )
    parser.add_argument(
        "--refresh", action="store_true",
        help="Force re-extraction from Chrome (ignore cache, prompt Keychain again)"
    )
    parser.add_argument(
        "--print-export", action="store_true",
        help="Print the shell export command instead of raw JSON"
    )

    args = parser.parse_args()

    print(f"🍪  Extracting {'all' if args.all_cookies else 'Supabase (sb-*)'} cookies")
    print(f"    Domain  : {args.domain}")
    print(f"    Profile : {args.profile}")

    cookies = extract_cookies(
        domain=args.domain,
        profile=args.profile,
        supabase_only=not args.all_cookies,
        refresh=args.refresh,
    )

    if not cookies:
        print(
            f"\n⚠️  No {'Supabase ' if not args.all_cookies else ''}cookies found for {args.domain}.\n"
            f"   Make sure you are logged in to {args.domain} in Chrome.\n"
            f"   Try --all-cookies to see if any cookies exist at all."
        )
        sys.exit(1)

    # ── Auto-refresh expired tokens via Supabase REST API ─────────────────────
    # Supabase JWTs expire at 1h. If Chrome's stored cookies are stale,
    # we attempt a token refresh before injecting them into the browser.
    SUPABASE_URL  = "https://vikyizqeppgnxccwqxue.supabase.co"
    SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZpa3lpenFlcHBnbnhjY3dxeHVlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2MTA2OTYsImV4cCI6MjA2MTE4NjY5Nn0.JG3aPqrJR7iM2SAvHGERuqxjON_hDPEiMmpWVZMeXKk"
    refreshed = try_refresh_session(cookies, SUPABASE_URL, SUPABASE_ANON)
    if refreshed:
        cookies = refreshed
        save_cookie_cache(args.domain, refreshed)
    elif not args.run_tests:
        pass  # print-only mode, stale cookies OK
    else:
        print(
            "\n⚠️  Session is expired and could not be refreshed.\n"
            "   Log back in to speakerhero.app in Chrome, then re-run:\n"
            "   python3 scripts/grab_cookies.py --domain speakerhero.app --refresh --run-tests"
        )
        # Don't exit — the browser may auto-refresh via Supabase's client-side logic

    print(f"\n✅  Found {len(cookies)} cookie(s):")
    for c in cookies:
        masked = c['value'][:12] + "..." if len(c['value']) > 12 else c['value']
        print(f"    {c['name']} = {masked}")

    cookies_json = json.dumps(cookies)

    if args.print_export:
        print(f"\n# Copy and paste this into your shell:\nexport SPEAKERHERO_COOKIES='{cookies_json}'\n")

    if args.run_tests:
        # Must run from platform-selenium root
        script_dir = Path(__file__).parent.parent
        os.chdir(script_dir)
        sys.exit(run_tests(cookies, args.env))


if __name__ == "__main__":
    main()
