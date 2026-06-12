"""
test_r57_pending_marker_strictness.py — R57 Train B: PENDING marker strictness tests.

Verifies that BUNDLE_VALIDATION_PASS_2_SHA: PENDING and BUNDLE_VALIDATION_PASS_1_SHA: PENDING
are caught by:
  1. PENDING_MARKER_PATTERNS (scanned by check_no_pending_reports)
  2. STATUS_LINE_PATTERNS inside check_repo_reports_pending

These patterns were missing in R56, causing IV-R56-003/004.

R57 Sprint: FORMAT-FACTORY-R57-SELF_VERIFYING-RC-REPLAY-PRODUCT-EXPANSION-PHASE8-MEGA-TRAIN-001
IV-R56-003, IV-R56-004
"""
from __future__ import annotations

import io
import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.validate_evidence_bundle import (
    PENDING_MARKER_PATTERNS,
    check_no_pending_reports,
    check_repo_reports_pending,
)


class TestPendingMarkerPatternsCoverage:
    """PENDING_MARKER_PATTERNS must include SHA-keyed variants."""

    def test_pass2_sha_pending_in_patterns(self):
        """BUNDLE_VALIDATION_PASS_2_SHA: PENDING must be in PENDING_MARKER_PATTERNS."""
        assert "BUNDLE_VALIDATION_PASS_2_SHA: PENDING" in PENDING_MARKER_PATTERNS, (
            "IV-R56-003/004: BUNDLE_VALIDATION_PASS_2_SHA: PENDING missing from PENDING_MARKER_PATTERNS"
        )

    def test_pass1_sha_pending_in_patterns(self):
        """BUNDLE_VALIDATION_PASS_1_SHA: PENDING must be in PENDING_MARKER_PATTERNS."""
        assert "BUNDLE_VALIDATION_PASS_1_SHA: PENDING" in PENDING_MARKER_PATTERNS, (
            "IV-R56-003/004: BUNDLE_VALIDATION_PASS_1_SHA: PENDING missing from PENDING_MARKER_PATTERNS"
        )

    def test_original_patterns_still_present(self):
        """Existing patterns must not have been removed."""
        assert "BUNDLE_VALIDATION: PENDING" in PENDING_MARKER_PATTERNS
        assert "validation_status: PENDING" in PENDING_MARKER_PATTERNS
        assert "PENDING (bundle not yet built)" in PENDING_MARKER_PATTERNS


class TestCheckNoPendingReportsDetectsShaPending:
    """check_no_pending_reports must catch BUNDLE_VALIDATION_PASS_2_SHA: PENDING."""

    def test_pass2_sha_pending_caught_in_metadata(self):
        """A metadata file containing BUNDLE_VALIDATION_PASS_2_SHA: PENDING causes FAIL."""
        metadata = {
            "final-verdict.md": (
                "# R56 Final Verdict\n\n"
                "**Verdict:** R56_CLOSURE_REPAIR_AND_PRODUCT_EXPANSION_COMPLETE\n\n"
                "BUNDLE_VALIDATION_PASS_2_SHA: PENDING\n"
            )
        }
        hits = check_no_pending_reports(metadata)
        assert len(hits) > 0, "Should have detected BUNDLE_VALIDATION_PASS_2_SHA: PENDING"
        matched_files = [f for f, _ in hits]
        assert "final-verdict.md" in matched_files

    def test_pass1_sha_pending_caught_in_metadata(self):
        """A metadata file containing BUNDLE_VALIDATION_PASS_1_SHA: PENDING causes FAIL."""
        metadata = {
            "final-verdict.md": (
                "BUNDLE_VALIDATION_PASS_1_SHA: PENDING\n"
            )
        }
        hits = check_no_pending_reports(metadata)
        assert len(hits) > 0, "Should have detected BUNDLE_VALIDATION_PASS_1_SHA: PENDING"

    def test_clean_verdict_not_flagged(self):
        """A verdict with real SHA values must not be flagged."""
        metadata = {
            "final-verdict.md": (
                "# R57 Final Verdict\n\n"
                "BUNDLE_VALIDATION_PASS_2_SHA: 5043fe754c23a5ce2ee3ce97dd4ebfc2facfd2d224bc43ec82b955828a152ca7\n"
                "BUNDLE_VALIDATION_PASS_1_SHA: 7dca57b2746836d5866222f8bcbc2af296a6deb85b14d73887077f4895e332fc\n"
            )
        }
        hits = check_no_pending_reports(metadata)
        assert len(hits) == 0, f"Real SHA values should not be flagged: {hits}"


class TestCheckRepoReportsPendingDetectsShaPending:
    """check_repo_reports_pending must catch SHA-keyed PENDING in bundled final-verdict.md."""

    def _make_bundle_with_verdict(self, verdict_content: str) -> str:
        """Create a temp zip with repo/reports/r57/final-verdict.md."""
        import tempfile
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("repo/reports/r57/final-verdict.md", verdict_content)
        buf.seek(0)
        data = buf.read()
        with tempfile.NamedTemporaryFile(suffix="_r57-test.zip", delete=False) as f:
            f.write(data)
            return f.name

    def test_pass2_sha_pending_caught_in_repo_reports(self, tmp_path):
        """check_repo_reports_pending detects BUNDLE_VALIDATION_PASS_2_SHA: PENDING."""
        verdict = (
            "# R57 Final Verdict\n\n"
            "**Verdict:** R57_SOME_COMPLETE\n\n"
            "BUNDLE_VALIDATION_PASS_2_SHA: PENDING\n"
        )
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("repo/reports/r57/final-verdict.md", verdict)
        buf.seek(0)

        bundle_path = tmp_path / "test-r57.zip"
        bundle_path.write_bytes(buf.read())

        with zipfile.ZipFile(bundle_path, "r") as zf:
            hits = check_repo_reports_pending(zf)

        assert len(hits) > 0, "Should detect BUNDLE_VALIDATION_PASS_2_SHA: PENDING in repo reports"

    def test_clean_verdict_not_flagged_in_repo(self, tmp_path):
        """A verdict with a real SHA value is not flagged."""
        verdict = (
            "# R57 Final Verdict\n\n"
            "BUNDLE_VALIDATION_PASS_2_SHA: 5043fe754c23a5ce2ee3ce97dd4ebfc2facfd2d224bc43ec82b955828a152ca7\n"
        )
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("repo/reports/r57/final-verdict.md", verdict)
        buf.seek(0)

        bundle_path = tmp_path / "test-r57-clean.zip"
        bundle_path.write_bytes(buf.read())

        with zipfile.ZipFile(bundle_path, "r") as zf:
            hits = check_repo_reports_pending(zf)

        assert len(hits) == 0, f"Real SHA should not be flagged: {hits}"
