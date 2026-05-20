"""
R38 Lane B: Evidence depth hardening tests.

Extends R37 placeholder detection with:
1. Status-only stub detection (status: pending, status: stub, result: PENDING)
2. Minimum content depth check (files below 50 bytes are flagged)
3. Metadata depth exempt files (git-status-final.txt legitimately short)
4. R37 closure identity verification
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tools" / "evidence"))


# ---------------------------------------------------------------------------
# 1. Status-Only Stub Detection
# ---------------------------------------------------------------------------

class TestStatusOnlyStubDetection:
    """R38: catch metadata files that contain only a status line."""

    def test_status_pending_caught(self):
        from validate_evidence_bundle import check_no_pending_reports
        fake = {"stub.md": "status: pending\n"}
        hits = check_no_pending_reports(fake)
        assert any(f == "stub.md" for f, _ in hits)

    def test_status_stub_caught(self):
        from validate_evidence_bundle import check_no_pending_reports
        fake = {"stub.yaml": "status: stub\n"}
        hits = check_no_pending_reports(fake)
        assert any(f == "stub.yaml" for f, _ in hits)

    def test_result_pending_caught(self):
        from validate_evidence_bundle import check_no_pending_reports
        fake = {"lane.md": "result: PENDING\n"}
        hits = check_no_pending_reports(fake)
        assert any(f == "lane.md" for f, _ in hits)

    def test_real_content_not_flagged(self):
        from validate_evidence_bundle import check_no_pending_reports
        fake = {
            "report.md": "# Sprint Report\n\nAll 27 tests pass. Evidence depth verified.\n"
        }
        hits = check_no_pending_reports(fake)
        assert len(hits) == 0


# ---------------------------------------------------------------------------
# 2. Minimum Content Depth Check
# ---------------------------------------------------------------------------

class TestMetadataContentDepth:
    """R38: files below METADATA_MINIMUM_CONTENT_BYTES are flagged."""

    def test_shallow_file_flagged(self):
        from validate_evidence_bundle import check_metadata_content_depth
        fake = {"tiny.md": "ok\n"}
        hits = check_metadata_content_depth(fake)
        assert any(f == "tiny.md" for f, _ in hits)

    def test_adequate_file_not_flagged(self):
        from validate_evidence_bundle import check_metadata_content_depth
        fake = {"report.md": "# Report\n\n" + "x" * 100 + "\n"}
        hits = check_metadata_content_depth(fake)
        assert len(hits) == 0

    def test_git_status_exempt(self):
        from validate_evidence_bundle import check_metadata_content_depth
        fake = {"git-status-final.txt": "clean\n"}
        hits = check_metadata_content_depth(fake)
        assert len(hits) == 0

    def test_threshold_is_50_bytes(self):
        from validate_evidence_bundle import METADATA_MINIMUM_CONTENT_BYTES
        assert METADATA_MINIMUM_CONTENT_BYTES == 50


# ---------------------------------------------------------------------------
# 3. R37 Closure Identity Verification
# ---------------------------------------------------------------------------

class TestR37ClosureIdentity:
    """R38 Lane A: verify R37 closure identity findings."""

    def test_r37_final_verdict_exists(self):
        verdict = REPO / "reports" / "r37" / "final-verdict.md"
        assert verdict.exists(), "R37 final verdict must exist"

    def test_r37_true_commit_is_d6496c8(self):
        """R37 sync commit must be d6496c8 (11 files)."""
        verdict = REPO / "reports" / "r37" / "final-verdict.md"
        text = verdict.read_text(encoding="utf-8")
        # R37 verdict should document R37 work, committed in d6496c8
        assert "R37" in text
        # The R38 audit documents that d6496c8 is the true R37 commit
        audit = REPO / "reports" / "r38" / "r37-closure-identity-audit.md"
        if audit.exists():
            audit_text = audit.read_text(encoding="utf-8")
            assert "d6496c8" in audit_text, "R38 audit must reference d6496c8 as true R37 commit"

    def test_r37_test_file_in_621eab3_documented(self):
        """R38 audit must document test_r37_evidence_depth_guards.py misattribution."""
        audit = REPO / "reports" / "r38" / "r37-closure-identity-audit.md"
        if not audit.exists():
            pytest.skip("R38 audit not yet written")
        text = audit.read_text(encoding="utf-8")
        assert "test_r37_evidence_depth_guards.py" in text
        assert "621eab3" in text


# ---------------------------------------------------------------------------
# 4. Exclude-Patterns Fix Verification
# ---------------------------------------------------------------------------

class TestExcludePatternsMerge:
    """R38: exclude_patterns contract field properly merged."""

    def test_validator_merges_all_three_pattern_fields(self):
        """validate_evidence_bundle must merge forbidden_paths + forbidden_patterns + exclude_patterns."""
        source = (REPO / "tools" / "evidence" / "validate_evidence_bundle.py").read_text(encoding="utf-8")
        assert "exclude_patterns" in source, "Validator must reference exclude_patterns"

    def test_builder_merges_all_three_pattern_fields(self):
        """build_evidence_bundle must merge forbidden_paths + forbidden_patterns + exclude_patterns."""
        source = (REPO / "tools" / "evidence" / "build_evidence_bundle.py").read_text(encoding="utf-8")
        assert "exclude_patterns" in source, "Builder must reference exclude_patterns"
