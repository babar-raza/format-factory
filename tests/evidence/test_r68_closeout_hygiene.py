"""R68 Train E: Validator closeout-hygiene token checks.

Proves that validate_evidence_bundle.py rejects bundles containing:
  - [to be filled] in final-independent-verification.md
  - Post-bundle authoritative count: TBD in python-tests-summary.txt
  - UNKNOWN (3 — in python-tests-summary.txt
  - [commit SHA to be filled] in final reports

R68 Sprint: FORMAT-FACTORY-R68-FINAL-CLOSEOUT-HYGIENE-LOCAL-RC-SEAL-MEGA-TRAIN-001
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path

_ev = Path(__file__).resolve().parents[2] / "tools" / "evidence"
if str(_ev) not in sys.path:
    sys.path.insert(0, str(_ev))

import pytest
from validate_evidence_bundle import check_closeout_hygiene_tokens, CLOSEOUT_HYGIENE_TOKENS


def _make_zip_with_files(files: dict[str, str]) -> zipfile.ZipFile:
    """Create an in-memory ZIP with the given filename→content mapping."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


class TestCloseoutHygieneTokensFunction:
    """Unit tests for check_closeout_hygiene_tokens()."""

    def test_clean_bundle_returns_no_hits(self):
        zf = _make_zip_with_files({
            "repo/reports/r68/final-independent-verification.md":
                "FINAL_IV: R68_COMPLETE\n| git status | PASS |\n",
            "bundle-metadata/python-tests-summary.txt":
                "Full suite result: 5130 passed, 3 failed (pre-existing), 27 skipped\n"
                "POST_BUNDLE_PYTHON_TESTS: 5130 passed, 3 pre-existing failed\n",
        })
        hits = check_closeout_hygiene_tokens(zf)
        assert hits == [], f"Expected no hits but got: {hits}"

    def test_to_be_filled_in_final_iv_report_flagged(self):
        zf = _make_zip_with_files({
            "repo/reports/r67/final-independent-verification.md":
                "| git status | [to be filled] |\nFINAL_IV: [to be filled at closeout]\n",
        })
        hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) == 1
        assert "[to be filled]" in hits[0][1]
        assert "final-independent-verification.md" in hits[0][0]

    def test_tbd_in_python_tests_summary_flagged(self):
        zf = _make_zip_with_files({
            "bundle-metadata/python-tests-summary.txt":
                "Post-bundle authoritative count: TBD (updated at closeout)\n",
        })
        hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) == 1
        assert "post-bundle authoritative count: tbd" in hits[0][1]

    def test_unknown_failures_in_tests_summary_flagged(self):
        zf = _make_zip_with_files({
            "bundle-metadata/python-tests-summary.txt":
                "UNKNOWN (3 — output truncation; likely pre-existing)\n",
        })
        hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) == 1
        assert "unknown (3 —" in hits[0][1]

    def test_commit_sha_to_be_filled_flagged(self):
        zf = _make_zip_with_files({
            "repo/reports/r67/final-independent-verification.md":
                "- feat(r67): mega-train — [commit SHA to be filled]\n",
        })
        hits = check_closeout_hygiene_tokens(zf)
        assert len(hits) == 1

    def test_unscanned_file_not_checked(self):
        """Files not in CLOSEOUT_HYGIENE_REPORT_FILES are ignored."""
        zf = _make_zip_with_files({
            "bundle-metadata/git-log.txt":
                "Merge commit SHA: [to be filled] (historical ref)\n",
            "bundle-metadata/blockers-status.txt":
                "Post-bundle authoritative count: TBD\n",
        })
        hits = check_closeout_hygiene_tokens(zf)
        # git-log.txt is not in CLOSEOUT_HYGIENE_REPORT_FILES
        # blockers-status.txt is not in CLOSEOUT_HYGIENE_REPORT_FILES
        assert hits == []

    def test_multiple_tokens_only_one_hit_per_file(self):
        """Only the first token match per file is reported (no duplicates)."""
        zf = _make_zip_with_files({
            "repo/reports/r67/final-independent-verification.md":
                "| col1 | [to be filled] |\nFINAL_IV: [to be filled at closeout]\n"
                "- feat: [commit SHA to be filled]\n",
        })
        hits = check_closeout_hygiene_tokens(zf)
        # Only one hit per file (first token match wins)
        assert len(hits) == 1

    def test_lane_ownership_pending_flagged(self):
        """lane-ownership.md with PENDING status rows is not scanned by this function.

        lane-ownership.md is in CLOSEOUT_HYGIENE_REPORT_FILES but the
        PENDING token for lane status is not in CLOSEOUT_HYGIENE_TOKENS —
        those are caught by check_scoreboard_lanes_in_progress.
        This test confirms that clean lane-ownership.md passes.
        """
        zf = _make_zip_with_files({
            "repo/reports/r68/lane-ownership.md":
                "| A | Coordinator | COMPLETE |\n| B | Coordinator | COMPLETE |\n",
        })
        hits = check_closeout_hygiene_tokens(zf)
        assert hits == []


class TestCloseoutHygieneTokenList:
    """Verify the token list contains expected entries."""

    def test_to_be_filled_token_present(self):
        assert "[to be filled]" in CLOSEOUT_HYGIENE_TOKENS

    def test_tbd_token_present(self):
        assert "post-bundle authoritative count: tbd" in CLOSEOUT_HYGIENE_TOKENS

    def test_unknown_token_present(self):
        assert "unknown (3 —" in CLOSEOUT_HYGIENE_TOKENS

    def test_commit_sha_token_present(self):
        assert "[commit sha to be filled]" in CLOSEOUT_HYGIENE_TOKENS
