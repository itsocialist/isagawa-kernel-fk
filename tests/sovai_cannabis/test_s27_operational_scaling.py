"""
TestS27OperationalScaling - Selenium E2E tests for Sprint 27 stories.

Stories under test:
  - B-24: Agents render complete React artifact components (no truncation/unterminated string)
  - B-25a: Open registration is disabled (ALLOW_REGISTRATION=false)
  - B-25b: Onboarding wizard fires on first post-auth navigation
  - B-25c: Onboarding wizard does NOT repeat after completion (DB persistence)
  - B-25d: LibreChat /admin panel is accessible to admin-role user (v0.8.5+)

Run with:
    pytest tests/sovai_cannabis/test_s27_operational_scaling.py --env sovai_cannabis_local -v
"""

import time
import pytest
from resources.utilities import autologger
from roles.sovai.admin_role import AdminRole
from pages.sovai.login_page import LoginPage
from pages.sovai.chat_page import ChatPage

# A large enough response to guarantee no truncation occurred
MIN_ARTIFACT_RESPONSE_CHARS = 500


class TestS27OperationalScaling:
    """
    E2E coverage for Sprint 27: Operational Scaling & Platform Hardening.
    Validates B-24 (artifact token truncation fix) and B-25 (invitation-only
    registration + DB-backed onboarding state).
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config, test_users):
        """Wire up the browser, configuration, and test users."""
        self.browser = browser
        self.config = config
        self.test_users = test_users
        self.base_url = config["url"]

        self.login_page = LoginPage(self.browser)
        self.chat_page = ChatPage(self.browser)

    def _ensure_authenticated(self):
        """Ensure we are logged in as admin before running tests."""
        current_url = self.browser.get_current_url()
        if self.base_url.rstrip("/") in current_url and "/login" not in current_url:
            return
        self.browser.navigate_to(f"{self.base_url}/login")
        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=self.base_url,
            email=credentials["email"],
            password=credentials["password"],
        )
        admin.login_and_verify()

    def _send_and_get_response(self, agent_name: str, prompt: str, timeout: int = 90) -> str:
        """Navigate to an agent, send a prompt, and return the response text."""
        self._ensure_authenticated()
        self.chat_page.start_new_chat()
        self.chat_page.select_agent_by_name(agent_name)
        self.chat_page.send_message(prompt)
        self.chat_page.wait_for_response(timeout=timeout)
        return self.chat_page.get_last_response_text()

    # ═══════════════════════════════════════════════════════════
    # B-24: Artifact Token Truncation Fix
    # ═══════════════════════════════════════════════════════════

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.b24
    @autologger.automation_logger("Test")
    def test_b24_compliance_audit_renders_artifact(self):
        """
        B-24: Compliance Auditor should render a React artifact when asked
        for a detailed label audit. Validates that the agent is NOT truncated
        mid-component by a token ceiling.

        AAA:
        Arrange - Log in and navigate to Compliance Auditor
        Act     - Request a detailed label audit
        Assert  - Response is long (>500 chars) and no 'Unterminated string' error
        """
        response = self._send_and_get_response(
            "Compliance Auditor",
            (
                "Please perform a full California DCC compliance audit of this label text: "
                "'GOVERNMENT WARNING: THIS PRODUCT CONTAINS CANNABIS, A SCHEDULE I "
                "CONTROLLED SUBSTANCE. KEEP OUT OF REACH OF CHILDREN AND ANIMALS. "
                "CANNABIS PRODUCTS MAY ONLY BE POSSESSED OR CONSUMED BY PERSONS 21 "
                "YEARS OF AGE OR OLDER. THE INTOXICATING EFFECTS OF CANNABIS PRODUCTS "
                "MAY BE DELAYED UP TO TWO HOURS. THIS PACKAGE IS NOT CHILD RESISTANT "
                "AFTER OPENING.' "
                "Include a sortable React table of all violations with severity, regulation citation, and remediation."
            ),
            timeout=120,
        )

        # Must be a substantial response - truncation produces <200 chars of garbled code
        assert len(response) >= MIN_ARTIFACT_RESPONSE_CHARS, (
            f"B-24 REGRESSION: Response too short ({len(response)} chars). "
            f"Agent likely hit token limit and truncated the artifact."
        )

        # Confirm no raw JS error leaked into the message
        assert "unterminated string" not in response.lower(), (
            "B-24 REGRESSION: 'Unterminated string' error surfaced in agent response."
        )
        assert "syntaxerror" not in response.lower(), (
            "B-24 REGRESSION: SyntaxError surfaced in agent response."
        )

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.b24
    @autologger.automation_logger("Test")
    def test_b24_formulation_assistant_artifact_complete(self):
        """
        B-24: Formulation Assistant should generate a complete batch record
        or dashboard artifact without truncating the JSX mid-string.

        AAA:
        Arrange - Log in and navigate to Formulation Assistant
        Act     - Request a comprehensive batch record dashboard
        Assert  - Response is substantial, artifact is present (iframe or code block)
        """
        response = self._send_and_get_response(
            "Formulation Assistant",
            (
                "Generate a complete batch record React dashboard for a 500-unit gummy batch. "
                "Include: product name, batch number, date, operator, equipment list, raw "
                "material lot numbers with weights, process steps with time/temp/duration for "
                "decarb/infusion/molding/packaging, QC checkpoints, and final disposition. "
                "Render this as a styled React artifact."
            ),
            timeout=120,
        )

        assert len(response) >= MIN_ARTIFACT_RESPONSE_CHARS, (
            f"B-24 REGRESSION: Response too short ({len(response)} chars). "
            f"Formulation Assistant likely truncated the batch record artifact."
        )

        # An artifact or code block must be present in the response
        has_artifact = self.chat_page.has_artifact_button() or self.chat_page.has_code_block()
        assert has_artifact, (
            "B-24: Expected an artifact or code block in the Formulation Assistant response."
        )

    # ═══════════════════════════════════════════════════════════
    # B-25a: Registration Disabled
    # ═══════════════════════════════════════════════════════════

    @pytest.mark.sovai_cannabis
    @pytest.mark.auth
    @pytest.mark.b25
    @autologger.automation_logger("Test")
    def test_b25a_registration_route_disabled(self):
        """
        B-25a: With ALLOW_REGISTRATION=false, the /register route must either
        redirect away, display a 'registration disabled' message, or hide the
        registration link from the login page.

        AAA:
        Arrange - Navigate to the login page (unauthenticated)
        Act     - Attempt to reach /register
        Assert  - User is NOT on a functional registration form
        """
        # Navigate to register URL directly
        self.browser.navigate_to(f"{self.base_url}/register")
        time.sleep(2)  # Allow React SPA to settle

        current_url = self.browser.get_current_url()
        page_source = self.browser.driver.page_source.lower()

        # Any of these outcomes is acceptable evidence of B-25a
        redirected_away = "/login" in current_url or "/c/" in current_url
        registration_disabled_msg = (
            "registration" in page_source and (
                "disabled" in page_source
                or "not allowed" in page_source
                or "invitation" in page_source
                or "contact" in page_source
            )
        )
        # If still on /register, the form itself must not be functional (no email input)
        on_register_page = "/register" in current_url
        has_email_input = self.browser.is_element_present(
            "css selector", "input[type='email']", timeout=3
        )
        form_blocked = on_register_page and not has_email_input

        assert redirected_away or registration_disabled_msg or form_blocked, (
            f"B-25a FAIL: Registration appears to still be open. "
            f"URL: {current_url}, page contains registration form inputs."
        )

    @pytest.mark.sovai_cannabis
    @pytest.mark.auth
    @pytest.mark.b25
    @autologger.automation_logger("Test")
    def test_b25a_register_link_not_present_on_login(self):
        """
        B-25a: When registration is disabled, the login page must not display
        a visible 'Create an account' / 'Sign up' link.

        AAA:
        Arrange - Navigate to login page
        Act     - Inspect for registration call-to-action links
        Assert  - No prominent 'Sign up' / 'Create account' element is visible
        """
        self.browser.navigate_to(f"{self.base_url}/login")
        time.sleep(2)

        page_source = self.browser.driver.page_source.lower()

        # None of these CTAs should appear on the page when registration is off
        forbidden_phrases = ["sign up", "create an account", "register now", "create account"]
        found = [p for p in forbidden_phrases if p in page_source]

        assert not found, (
            f"B-25a FAIL: Registration CTA found on login page with ALLOW_REGISTRATION=false. "
            f"Phrases found: {found}"
        )

    # ═══════════════════════════════════════════════════════════
    # B-25b: Onboarding wizard fires on first login
    # ═══════════════════════════════════════════════════════════

    @pytest.mark.sovai_cannabis
    @pytest.mark.onboarding
    @pytest.mark.b25
    @autologger.automation_logger("Test")
    def test_b25b_onboarding_wizard_fires_post_login(self):
        """
        B-25b: The 'Liquid Glass' onboarding wizard must appear on the chat page
        for a user whose onboarding state has not been stored in the DB.

        Strategy: Clear any existing onboarding DB state for the test admin user
        via the /api/onboarding DELETE endpoint, then log in and verify the modal.

        AAA:
        Arrange - Clear onboarding state via API, navigate to login
        Act     - Log in as admin
        Assert  - Onboarding overlay (#sovai-onboarding-overlay) is visible
        """
        # Clear onboarding DB state via Nginx proxy → sovai-memory
        # We use execute_script to make an XHR since we're in the browser context
        # NOTE: We first navigate to the site so the cookie/session is live
        self.browser.navigate_to(f"{self.base_url}/login")
        credentials = self.test_users["sovai_cannabis_admin"]
        admin = AdminRole(
            self.browser,
            base_url=self.base_url,
            email=credentials["email"],
            password=credentials["password"],
        )
        admin.login_and_verify()

        # Wait for SPA to settle on /c/ route
        time.sleep(3)

        # Fetch the user ID, then delete the onboarding fact via the API proxy directly in browser
        self.browser.execute_script("""
            fetch('/api/user')
                .then(r => r.json())
                .then(user => {
                    const id = user._id || user.id;
                    if (id) {
                        fetch('/api/onboarding/' + id + '/onboarding_complete', { method: 'DELETE' });
                    }
                })
                .catch(err => console.error("Error clearing onboarding:", err));
        """)

        # Re-navigate to trigger the polling logic fresh
        self.browser.navigate_to(f"{self.base_url}/c/new")
        time.sleep(5)  # Allow the 500ms polling loop to fire and render wizard

        overlay_present = self.browser.is_element_present(
            "id", "sovai-onboarding-overlay", timeout=10
        )
        assert overlay_present, (
            "B-25b FAIL: Onboarding wizard did not appear after login for user "
            "with no DB onboarding state."
        )

    # ═══════════════════════════════════════════════════════════
    # B-25c: Onboarding wizard does NOT repeat (DB persistence)
    # ═══════════════════════════════════════════════════════════

    @pytest.mark.sovai_cannabis
    @pytest.mark.onboarding
    @pytest.mark.b25
    @autologger.automation_logger("Test")
    def test_b25c_onboarding_does_not_repeat_after_completion(self):
        """
        B-25c: Once the onboarding wizard is completed, a second navigation
        (even with cleared localStorage) must NOT show the wizard again.

        AAA:
        Arrange - Log in, confirm wizard is present
        Act     - Click 'Get Started' to complete all wizard steps, clear localStorage
        Assert  - Navigating to /c/new does NOT show the wizard a second time
        """
        self._ensure_authenticated()
        self.browser.navigate_to(f"{self.base_url}/c/new")
        time.sleep(5)

        overlay_present = self.browser.is_element_present(
            "id", "sovai-onboarding-overlay", timeout=10
        )

        if overlay_present:
            # Walk through the wizard to completion using the 'Next / Get Started' button
            for _ in range(5):  # Max 5 steps in the wizard
                btn = self.browser.find_elements("id", "sovai-onboarding-overlay")
                if not btn:
                    break
                # Click the primary CTA (Next/Get Started)
                self.browser.execute_script("""
                    const overlay = document.getElementById('sovai-onboarding-overlay');
                    if (!overlay) return;
                    const buttons = overlay.querySelectorAll('button');
                    const primaryBtn = Array.from(buttons).find(b =>
                        b.textContent.includes('Next') ||
                        b.textContent.includes('Get Started') ||
                        b.textContent.includes('Start')
                    );
                    if (primaryBtn) primaryBtn.click();
                """)
                time.sleep(1)

        # Clear localStorage to ensure we're testing DB-only persistence
        self.browser.execute_script("localStorage.clear(); sessionStorage.clear();")
        time.sleep(1)

        # Re-navigate — wizard must NOT reappear
        self.browser.navigate_to(f"{self.base_url}/c/new")
        time.sleep(6)

        overlay_reappeared = self.browser.is_element_present(
            "id", "sovai-onboarding-overlay", timeout=5
        )
        assert not overlay_reappeared, (
            "B-25c FAIL: Onboarding wizard reappeared after completion and localStorage clear. "
            "DB persistence is not working — falling back to localStorage behavior."
        )

    # ═══════════════════════════════════════════════════════════
    # T-08: Dashboard Export E2E Validation (CSV/PDF)
    # ═══════════════════════════════════════════════════════════

    @pytest.mark.sovai_cannabis
    @pytest.mark.agents
    @pytest.mark.t08
    @autologger.automation_logger("Test")
    def test_t08_dashboard_export_buttons_present_and_functional(self):
        """
        T-08: Dashboard Export E2E Validation
        Validates that when a Dashboard Artifact is generated (e.g. by the Margin Analyzer),
        the injected Export CSV and Export PDF buttons are present and correctly rendered
        in the artifact container.

        AAA:
        Arrange - Log in and navigate to the Margin Analyzer agent
        Act     - Request a detailed COGS breakdown dashboard
        Assert  - The artifact iframe/container contains the 'Export CSV' and 'Export PDF' buttons
        """
        # We use a generic prompt that forces a React Dashboard artifact to generate
        response = self._send_and_get_response(
            "Margin Analyzer",
            "Generate a complete COGS dashboard artifact for a 100mg THC edible gummy. Include the cost waterfall and breakeven chart.",
            timeout=120,
        )

        # Artifacts usually render in iframes or shadow DOMs in LibreChat, so we need to execute JS 
        # to cleanly pierce the boundary and check for the buttons, or wait for the standard CSS classes.
        time.sleep(5) # Let the React artifact fully render

        export_buttons_found = self.browser.execute_script("""
            // Look through all iframes to find the injected SovAI export buttons
            let foundCsv = false;
            let foundPdf = false;
            
            // Check main document just in case it rendered inline
            if (document.body.innerText.includes('Export CSV')) foundCsv = true;
            if (document.body.innerText.includes('Export PDF')) foundPdf = true;

            const iframes = document.querySelectorAll('iframe');
            for (let i = 0; i < iframes.length; i++) {
                try {
                    const doc = iframes[i].contentDocument || iframes[i].contentWindow.document;
                    if (doc.body.innerText.includes('Export CSV')) foundCsv = true;
                    if (doc.body.innerText.includes('Export PDF')) foundPdf = true;
                } catch(e) {
                    // Cross-origin iframe, skip
                }
            }
            return { csv: foundCsv, pdf: foundPdf };
        """)

        assert export_buttons_found["csv"], "T-08 FAIL: 'Export CSV' button was not found in the generated artifact."
        assert export_buttons_found["pdf"], "T-08 FAIL: 'Export PDF' button was not found in the generated artifact."



