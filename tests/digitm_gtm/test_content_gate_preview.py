"""
TestContentGatePreview - E2E test for the content-calendar gate post preview.

Verifies the fix shipped in digitm-gtm commit 7282b18: the gate approval
panel for a CONTENT_CALENDAR stage in GATE_PENDING state must render a
preview of the first N posts (not just a two-line summary).

Seeds a complete product + run + stage + gate directly into the dev DB
via psql subprocess so the test is repeatable without waiting for an AI
pipeline run. Tears down everything on exit.

Phase A: no auth required; the app falls back to phase-a-default-user.
"""

import json
import os
import secrets
import string
import subprocess
from typing import Dict

import pytest


def _cuid() -> str:
    """Generate a cuid-shaped string (c + 24 lowercase alphanumeric chars)
    so it satisfies z.string().cuid() on the server-side tRPC inputs.
    The `sel` prefix we used before (`sel_prod_1729...`) fails that check
    and the page shows "Pipeline run not found" — not a render bug, just
    tRPC input validation rejecting the id."""
    alphabet = string.ascii_lowercase + string.digits
    return "c" + "".join(secrets.choice(alphabet) for _ in range(24))

from resources.utilities import autologger
from pages.digitm_gtm.pipeline_view_page import PipelineViewPage


DB_NAME = "digitm_gtm"


def _psql(sql: str) -> str:
    """Run a SQL statement against the dev DB via psql; return stdout."""
    result = subprocess.run(
        ["psql", DB_NAME, "-c", sql, "-t", "-A"],
        capture_output=True,
        text=True,
        env={**os.environ, "PGOPTIONS": "--client-min-messages=warning"},
        check=True,
    )
    return result.stdout.strip()


def _seed_content_gate(seed: Dict[str, str]) -> None:
    """Insert Product, PipelineRun, PipelineStage, Gate for a CONTENT_CALENDAR
    stage stuck at GATE_PENDING. Idempotent with respect to FK cleanup."""
    product_id = seed["product_id"]
    run_id = seed["run_id"]
    stage_id = seed["stage_id"]
    gate_id = seed["gate_id"]

    # Matches the artifact shape written by contentCalendar.ts — posts[] with
    # platform, content, scheduledDate, hashtags, mediaHint, contentType.
    artifacts = {
        "calendarId": "test-calendar-1",
        "calendar": {
            "startDate": "2026-04-14",
            "endDate": "2026-04-24",
            "totalPosts": 3,
            "platforms": ["reddit", "bluesky", "linkedin"],
        },
        "posts": [
            {
                "platform": "reddit",
                "content": "Introducing PIIShield — the on-device PII scanner for iOS.",
                "scheduledDate": "2026-04-14T10:00:00Z",
                "hashtags": ["launch", "privacy"],
                "mediaHint": "og_image",
                "contentType": "launch_announcement",
            },
            {
                "platform": "bluesky",
                "content": "Your camera roll is a privacy landmine. PIIShield defuses it.",
                "scheduledDate": "2026-04-15T12:00:00Z",
                "hashtags": ["indiedev"],
                "mediaHint": "social_card",
                "contentType": "engagement",
            },
            {
                "platform": "linkedin",
                "content": "Why on-device beats cloud scanning for PII detection — a technical breakdown.",
                "scheduledDate": "2026-04-16T09:00:00Z",
                "hashtags": ["security"],
                "mediaHint": "hero_banner",
                "contentType": "educational",
            },
        ],
        "savedPosts": 3,
    }

    # Escape JSON for psql single-quoted literal: '' escapes a single quote
    artifacts_literal = json.dumps(artifacts).replace("'", "''")

    _psql(
        f"""
        INSERT INTO "Product"
          (id, "userId", name, description, audience, "updatedAt", "createdAt")
        VALUES
          ('{product_id}', 'phase-a-default-user',
           'Selenium Gate Preview Test',
           'Seeded product for the content-calendar gate preview Selenium test. Auto-deleted.',
           'QA engineers verifying content gate preview',
           NOW(), NOW());
        """
    )
    _psql(
        f"""
        INSERT INTO "PipelineRun"
          (id, "productId", status, mode, "startedAt", "updatedAt", "createdAt", "totalTokensUsed")
        VALUES
          ('{run_id}', '{product_id}', 'GATE_PENDING', 'dry-run',
           NOW(), NOW(), NOW(), 7214);
        """
    )
    _psql(
        f"""
        INSERT INTO "PipelineStage"
          (id, "pipelineRunId", "stageType", status, "tokensUsed", "modelUsed",
           artifacts, "createdAt", "updatedAt")
        VALUES
          ('{stage_id}', '{run_id}', 'CONTENT_CALENDAR', 'GATE_PENDING',
           7214, 'claude-sonnet-4-6',
           '{artifacts_literal}'::jsonb,
           NOW(), NOW());
        """
    )
    _psql(
        f"""
        INSERT INTO "Gate"
          (id, "pipelineRunId", "stageType", status, summary, artifacts, "expiresAt", "createdAt", "updatedAt")
        VALUES
          ('{gate_id}', '{run_id}', 'CONTENT_CALENDAR', 'PENDING',
           'Seeded: 30-day content calendar with 3 test posts. Review voice and tone.',
           '{artifacts_literal}'::jsonb,
           NOW() + INTERVAL '7 days', NOW(), NOW());
        """
    )


def _cleanup_content_gate(seed: Dict[str, str]) -> None:
    """Delete everything the test created. FKs cascade from Product so
    nothing gets orphaned."""
    _psql(f"DELETE FROM \"Product\" WHERE id = '{seed['product_id']}';")


@pytest.fixture
def content_gate_seed():
    """Seeds Product/Run/Stage/Gate for a CONTENT_CALENDAR gate-pending
    scenario and cleans up after the test."""
    seed = {
        "product_id": _cuid(),
        "run_id": _cuid(),
        "stage_id": _cuid(),
        "gate_id": _cuid(),
    }
    _seed_content_gate(seed)
    try:
        yield seed
    finally:
        _cleanup_content_gate(seed)


class TestContentGatePreview:
    """E2E: content-calendar gate approval shows post preview cards."""

    @pytest.fixture(autouse=True)
    def setup(self, browser, config):
        self.browser = browser
        self.config = config
        self.pipeline = PipelineViewPage(self.browser)

    @pytest.mark.digitm_gtm
    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_content_gate_renders_post_preview_cards(self, content_gate_seed):
        """
        Given a CONTENT_CALENDAR stage in GATE_PENDING with 3 seeded posts,
        When the user opens the pipeline view,
        Then the approval panel shows a preview block with 3 post cards,
        each containing the post's content, hashtags, and platform badge.
        """
        base_url = self.config["url"]
        seed = content_gate_seed

        # Arrange + Act — navigate to the seeded run
        self.pipeline.navigate(
            base_url, seed["product_id"], seed["run_id"]
        ).wait_for_page_loaded()

        # Sanity — chevron strip + a selected stage card are visible
        assert self.pipeline.has_chevron_strip(), "Chevron strip should render"
        assert self.pipeline.has_selected_stage_card(), \
            "A single selected stage card should render"

        # CONTENT_CALENDAR is the only GATE_PENDING stage — pickDefaultStage
        # should auto-select it. Be defensive and click the chevron anyway.
        self.pipeline.click_chevron("Content")

        # Assert — approval panel visible with preview header
        assert self.pipeline.has_pending_gates(), \
            "'Approval required' heading should be visible on the selected stage"
        assert self.pipeline.has_preview_header(), \
            "Content gate must show a 'Preview — first N of M' header"

        # Exactly 3 cards rendered (matches the seed's post count).
        # digitm-gtm commit 04291a3 merged the gate's duplicate artifact
        # panel into the stage card — preview now renders once per stage,
        # not twice, so a strict == 3 catches regressions of the merge.
        card_count = self.pipeline.count_preview_cards()
        assert card_count == 3, \
            f"Expected exactly 3 preview cards (matching seed data), got {card_count}"

        # Each seeded post's content appears in the preview
        assert self.pipeline.preview_contains_text("PIIShield"), \
            "Reddit post copy should appear in the preview"
        assert self.pipeline.preview_contains_text("camera roll is a privacy landmine"), \
            "Bluesky post copy should appear in the preview"
        assert self.pipeline.preview_contains_text("on-device beats cloud scanning"), \
            "LinkedIn post copy should appear in the preview"

        # Hashtag chips visible (from `hashtags: ["launch", "privacy"]`)
        assert self.pipeline.preview_hashtag_visible("launch"), \
            "Hashtag '#launch' should render as a chip"
        assert self.pipeline.preview_hashtag_visible("privacy"), \
            "Hashtag '#privacy' should render as a chip"

        # Approve/Reject buttons are still reachable — gate decision UI intact
        assert self.pipeline.is_approve_button_displayed(), \
            "Approve button should be visible on a CONTENT_CALENDAR gate"
