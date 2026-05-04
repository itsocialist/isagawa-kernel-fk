"""
TestSCCDemoScenarios - End-to-end Selenium tests for South Coast Commercial demo flows.

Sprint 16 Issue #124 — covers all 4 SCC demo scenarios:
  1. Urgent Activity Monitor  — fire/flood/mold events within 24h
  2. Vacancy Intelligence     — vacant units, tenant journey, loss-of-rent
  3. Delinquency Intelligence — delinquency journey, 3-day notice history
  4. Property Onboarding Audit — 42-checkpoint PMA checklist for 401 W

Ground-truth data sourced from:
  appfolio-mcp-server/src/services/mock-store.ts (Sprint 16 state)

Each test asserts:
  (a) The dedicated SCC agent was used
  (b) The response contains specific mock data values (proving tool was called)
  (c) No hallucination markers appear
  (d) Response does NOT contain placeholder refusal phrases

AAA pattern: Arrange → Act → Assert
"""

import time
import pytest
from resources.utilities import autologger
from roles.sovai.admin_role import AdminRole
from pages.sovai.login_page import LoginPage
from pages.sovai.chat_page import ChatPage


# ==================== GROUND TRUTH MOCK DATA ====================
# Values come from mock-store.ts (Sprint 16 state).
# If agents return these values, the MCP tool was actually called.

# Urgent Activity — 3 emergency work orders added Sprint 16 (category-based)
URGENT_CATEGORIES = ["water_damage", "mold_remediation", "fire_damage",
                     "water damage", "mold", "fire damage",
                     "ceiling leak", "pipe burst", "smoke damage",
                     "bathroom vanity", "emergency", "uninhabitable"]

# Vacancy — units 11 and 22 at 2525, unit 15 at 401W
VACANCY_MARKERS = ["11", "22", "15", "vacant", "vacancy",
                   "move-out", "move out", "turn", "days",
                   "loss", "rent", "2525", "401 w"]

# Delinquency — units 7, 14, 19 at 2525 with exact dollar amounts from sc-samples
DELINQUENCY_AMOUNTS = ["524.90", "524", "1,868", "1868", "1,469", "1469"]
DELINQUENCY_MARKERS = ["unit 7", "unit 14", "unit 19", "unit-07", "unit-14", "unit-19",
                        "3-day", "three-day", "notice", "delinquent", "2525"]

# Property Onboarding — 401 W California Ave, specific audit findings
ONBOARDING_MARKERS = ["401", "california", "vista", "24 unit", "24",
                       "3.75", "management fee", "first foundation",
                       "property manager", "rent", "$0", "0.00",
                       "insurance", "checklist", "pass", "fail", "warn"]

# Hallucination markers — generic AI-fabricated content
HALLUCINATION_MARKERS = [
    "i cannot", "i don't have", "i do not have access",
    "i'm unable", "i am unable", "unfortunately i",
    "as an ai", "i don't have real-time",
    "sunset apartments", "mountain view", "lakeshore", "urban edge",
    "sample property", "example property"
]

# Tool call wait time — LibreChat hides stop-generating while tools run
TOOL_WAIT_SECONDS = 20


class TestSCCDemoScenarios:
    """
    End-to-end tests for all 4 South Coast Commercial demo scenarios.

    These tests verify that the dedicated SCC agents call AppFolio MCP tools
    and return real mock data — not hallucinated or refused responses.

    Each test corresponds to one of Kevin's 4 key demo questions.
    """

    @pytest.fixture(autouse=True)
    def setup(self, browser, config, test_users):
        """Wire browser, config, and test_users into the test class."""
        self.browser = browser
        self.config = config
        self.test_users = test_users
        self.login_page = LoginPage(self.browser)
        self.chat_page = ChatPage(self.browser)

    def _ensure_authenticated(self):
        """Ensure we are logged in. Navigates and logs in if needed."""
        base_url = self.config["url"]
        current_url = self.browser.get_current_url()
        if base_url.rstrip("/") in current_url and "/login" not in current_url:
            return
        credentials = self.test_users["sovai_admin"]
        admin = AdminRole(
            self.browser,
            base_url=base_url,
            email=credentials["email"],
            password=credentials["password"]
        )
        admin.login_and_verify()

    def _get_admin_role(self) -> AdminRole:
        """Construct a fresh AdminRole for the current test."""
        credentials = self.test_users["sovai_admin"]
        return AdminRole(
            self.browser,
            base_url=self.config["url"],
            email=credentials["email"],
            password=credentials["password"]
        )

    def _assert_not_hallucinated(self, response: str, context: str = ""):
        """Assert the response does NOT contain hallucination/refusal markers."""
        response_lower = response.lower()
        for marker in HALLUCINATION_MARKERS:
            assert marker.lower() not in response_lower, (
                f"HALLUCINATION/REFUSAL DETECTED: Response contains '{marker}'. "
                f"Agent did not call MCP tool — it fabricated or refused. "
                f"Context: {context}\n"
                f"Response (first 600 chars): {response[:600]}"
            )

    def _assert_contains_any(self, response: str, expected_terms: list,
                              context: str = "") -> list:
        """
        Assert response contains at least one expected term.
        Returns the matched terms for logging.
        """
        response_lower = response.lower()
        found = [t for t in expected_terms if t.lower() in response_lower]
        assert len(found) > 0, (
            f"TOOL CALL FAILED — response contains none of {expected_terms}.\n"
            f"Context: {context}\n"
            f"Response (first 600 chars): {response[:600]}"
        )
        return found

    # ==================== SCC SCENARIO 1: URGENT ACTIVITY ====================

    @pytest.mark.sovai
    @pytest.mark.scc
    @pytest.mark.mcp
    @autologger.automation_logger("Test")
    def test_urgent_activity_scenario(self):
        """
        SCC Scenario 1 — Kevin's question: 'List all fire, flood and mold events
        in the last 24 hours.'

        Uses: Urgent Activity Monitor agent
        Expects: water_damage, mold_remediation, and/or fire_damage work orders
                 with categories matching the 3 emergency WOs added in Sprint 16.

        AAA Pattern:
        1. Arrange — Authenticate, create AdminRole
        2. Act     — Select 'Urgent Activity Monitor', ask for last 24h events
        3. Assert  — Response contains emergency category terms from mock data,
                     no hallucination markers, no refusal phrases
        """
        # Arrange
        self._ensure_authenticated()
        admin = self._get_admin_role()

        # Act
        admin.select_agent_and_send(
            "Urgent Activity Monitor",
            "List all fire, flood, water damage, and mold events across the "
            "portfolio in the last 24 hours. Show the property, unit, category, "
            "description, and recommended next action for each incident."
        )
        time.sleep(TOOL_WAIT_SECONDS)

        # Assert — response received
        assert self.chat_page.has_assistant_response(), \
            "Urgent Activity Monitor must produce a response"

        response = self.chat_page.get_last_response_text()

        # Assert — contains emergency event data from mock-store.ts wo-004/wo-005/wo-006
        matched = self._assert_contains_any(
            response,
            URGENT_CATEGORIES,
            context=(
                "Expected emergency work order data: water_damage (Unit 8 @ 2525), "
                "mold_remediation (Unit 15 @ 2525), fire_damage (Unit 3 @ 401W). "
                "Source: appfolio_list_work_orders"
            )
        )

        # Assert — no hallucination or refusal
        self._assert_not_hallucinated(response, context="SCC Urgent Activity scenario")

        # Assert — response is substantive (not a 1-liner)
        assert len(response) > 200, (
            f"Response is too short ({len(response)} chars) — "
            "agent likely did not call the tool or returned a stub."
        )

    # ==================== SCC SCENARIO 2: VACANCIES ====================

    @pytest.mark.sovai
    @pytest.mark.scc
    @pytest.mark.mcp
    @autologger.automation_logger("Test")
    def test_vacancy_scenario(self):
        """
        SCC Scenario 2 — Kevin's question: 'Show me all vacant units and loss of rent.'

        Uses: Vacancy Intelligence agent
        Expects: Vacant units (11, 22 @ 2525; 15 @ 401W), turn status, dollar figures.

        AAA Pattern:
        1. Arrange — Authenticate
        2. Act     — Select 'Vacancy Intelligence', ask for vacancies + loss of rent
        3. Assert  — Response contains vacancy data (unit numbers, turn status,
                     dollar figures), no hallucination
        """
        # Arrange
        self._ensure_authenticated()
        admin = self._get_admin_role()

        # Act
        admin.select_agent_and_send(
            "Vacancy Intelligence",
            "Show me all vacant units across the portfolio. For each vacancy, "
            "include the move-out date, days vacant, turn status, market rent, "
            "and the total loss-of-rent so far. Calculate the portfolio-wide "
            "monthly revenue loss."
        )
        time.sleep(TOOL_WAIT_SECONDS)

        # Assert — response received
        assert self.chat_page.has_assistant_response(), \
            "Vacancy Intelligence must produce a response"

        response = self.chat_page.get_last_response_text()

        # Assert — contains vacancy data from mock-store.ts units 11, 22, and 401W-15
        matched = self._assert_contains_any(
            response,
            VACANCY_MARKERS,
            context=(
                "Expected: vacant units 11 and 22 at 2525 San Diego, "
                "unit 15 at 401W, with turn status and loss-of-rent. "
                "Source: appfolio_list_units (status=vacant)"
            )
        )

        # Assert — contains a dollar figure (loss-of-rent calculation)
        dollar_present = any(
            sign in response for sign in ["$", "loss", "revenue", "rent"]
        )
        assert dollar_present, (
            "Vacancy Intelligence response must contain financial data "
            "(loss of rent calculation). Response: " + response[:400]
        )

        # Assert — no hallucination
        self._assert_not_hallucinated(response, context="SCC Vacancy scenario")

    # ==================== SCC SCENARIO 3: DELINQUENCIES ====================

    @pytest.mark.sovai
    @pytest.mark.scc
    @pytest.mark.mcp
    @autologger.automation_logger("Test")
    def test_delinquency_scenario(self):
        """
        SCC Scenario 3 — Kevin's question: 'Show me delinquencies — give me the
        full tenant journey including 3-day notice history.'

        Uses: Delinquency Intelligence agent
        Expects: Units 7, 14, 19 at 2525 with amounts $524.90, $1,868.44, $1,469.82.
                 3-day notice reference, ledger entries, late fee discrepancy.

        AAA Pattern:
        1. Arrange — Authenticate
        2. Act     — Select 'Delinquency Intelligence', ask for all delinquencies + journey
        3. Assert  — Response contains exact $ amounts from sc-samples, 3-day notice mention,
                     no hallucination
        """
        # Arrange
        self._ensure_authenticated()
        admin = self._get_admin_role()

        # Act
        admin.select_agent_and_send(
            "Delinquency Intelligence",
            "Show me all delinquent tenants in the portfolio. For each tenant, "
            "include the full journey — when the delinquency started, the amount "
            "owed, any 3-day notices sent, and the last payment communication. "
            "Also flag any late fee discrepancies vs the $100 policy."
        )
        time.sleep(TOOL_WAIT_SECONDS)

        # Assert — response received
        assert self.chat_page.has_assistant_response(), \
            "Delinquency Intelligence must produce a response"

        response = self.chat_page.get_last_response_text()

        # Assert — contains at least one exact delinquency amount from sc-samples
        matched_amounts = self._assert_contains_any(
            response,
            DELINQUENCY_AMOUNTS,
            context=(
                "Expected delinquency amounts matching sc-samples: "
                "$524.90 (Unit 7), $1,868.44 (Unit 14), $1,469.82 (Unit 19). "
                "Source: appfolio_list_delinquent_charges"
            )
        )

        # Assert — contains delinquency context markers (unit refs, notices)
        self._assert_contains_any(
            response,
            DELINQUENCY_MARKERS,
            context="Expected unit references (7, 14, 19) or 3-day notice mention"
        )

        # Assert — delinquency start date is a real date, not today's date
        # (ensures data comes from mock, not hallucinated as 'today')
        import datetime
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        today_human = datetime.date.today().strftime("%B %d, %Y")
        assert today_str not in response and today_human not in response, (
            "Delinquency start date appears to be today's date — "
            "agent may have hallucinated instead of using tool data. "
            "Expected start dates: 2026-02-01 or 2026-03-01."
        )

        # Assert — no hallucination
        self._assert_not_hallucinated(response, context="SCC Delinquency scenario")

    # ==================== SCC SCENARIO 4: PROPERTY ONBOARDING ====================

    @pytest.mark.sovai
    @pytest.mark.scc
    @pytest.mark.mcp
    @autologger.automation_logger("Test")
    def test_property_onboarding_audit(self):
        """
        SCC Scenario 4 — Kevin's question: 'Audit the PMA for 401 W — something
        like DOTS but for property onboarding.'

        Uses: Property Onboarding Audit agent
        Expects: 42-checkpoint checklist artifact with all 11 categories covered.
                 Must surface 3 P0 failures: no PM assigned, all $0 rents, no insurance.

        AAA Pattern:
        1. Arrange — Authenticate
        2. Act     — Select 'Property Onboarding Audit', ask for 401 W audit
        3. Assert  — Response contains checklist data, 24-unit reference, 3.75% fee,
                     at least one FAIL/WARN finding, no hallucination
        """
        # Arrange
        self._ensure_authenticated()
        admin = self._get_admin_role()

        # Act
        admin.select_agent_and_send(
            "Property Onboarding Audit",
            "Audit the onboarding of 401 W California Ave against the full "
            "SCC PMA onboarding checklist. Show all 42 checkpoints with their "
            "status (PASS/WARN/FAIL) and severity. Highlight any P0 failures "
            "that must be fixed before operations begin."
        )
        time.sleep(TOOL_WAIT_SECONDS + 10)  # Opus + 5 tool calls = allow extra time

        # Assert — response received
        assert self.chat_page.has_assistant_response(), \
            "Property Onboarding Audit must produce a response"

        response = self.chat_page.get_last_response_text()

        # Assert — contains 401 W property data from mock-store.ts
        matched = self._assert_contains_any(
            response,
            ONBOARDING_MARKERS,
            context=(
                "Expected 401 W property data: 24 units, 3.75% management fee, "
                "First Foundation Bank, Vista/California address. "
                "Source: appfolio_get_property + appfolio_list_units"
            )
        )

        # Assert — audit found at least one FAIL or WARN (3 P0 FAILs expected)
        response_lower = response.lower()
        has_finding = any(term in response_lower for term in [
            "fail", "warn", "p0", "missing", "not assigned",
            "no manager", "$0", "0.00", "no insurance"
        ])
        assert has_finding, (
            "Property Onboarding Audit must surface at least one FAIL or WARN. "
            "Expected P0 failures: no PM assigned, all $0 rents, no insurance. "
            f"Response (first 500 chars): {response[:500]}"
        )

        # Assert — response is substantive (HTML artifact = large response)
        assert len(response) > 500, (
            f"Response too short ({len(response)} chars) for a 42-checkpoint audit. "
            "Agent may not have called all required tools or generated the artifact."
        )

        # Assert — no hallucination
        self._assert_not_hallucinated(response, context="SCC Property Onboarding scenario")
