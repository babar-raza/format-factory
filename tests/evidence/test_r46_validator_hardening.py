"""
R46 validator hardening tests.

Verifies that the new check_repo_reports_pending() function catches
BUNDLE_VALIDATION: PENDING inside repo/reports/<RUN>/final-verdict.md.

Root cause: R45 bundle was built before final-verdict.md was updated from
PENDING to PASS. The existing validator only scanned bundle-metadata/ files
and CURRENT_STATE_REPO_FILES (plans/master-plan.md, memory/09). The new
check closes the gap by scanning repo/reports/*/final-verdict.md entries.
"""

import io
import zipfile

import pytest

from tools.evidence.validate_evidence_bundle import (
    check_repo_reports_pending,
    PENDING_MARKER_PATTERNS,
)


def _make_zip(entries: dict) -> zipfile.ZipFile:
    """Create an in-memory ZipFile from a dict of {name: content}."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    buf.seek(0)
    return zipfile.ZipFile(buf, "r")


class TestCheckRepoReportsPending:
    """Tests for check_repo_reports_pending() — R46 MT1 Lane 1B."""

    def test_no_reports_returns_empty(self):
        """Bundle with no repo/reports/ entries — no hits."""
        zf = _make_zip({
            "bundle-metadata/git-status-final.txt": "nothing to commit",
        })
        assert check_repo_reports_pending(zf) == []

    def test_final_verdict_pass_returns_empty(self):
        """final-verdict.md containing BUNDLE_VALIDATION: PASS — no hit."""
        zf = _make_zip({
            "repo/reports/r46/final-verdict.md": "BUNDLE_VALIDATION: PASS\n",
        })
        assert check_repo_reports_pending(zf) == []

    def test_final_verdict_pending_returns_hit(self):
        """final-verdict.md containing BUNDLE_VALIDATION: PENDING — returns hit."""
        zf = _make_zip({
            "repo/reports/r46/final-verdict.md": (
                "# R46 Final Verdict\n"
                "BUNDLE_VALIDATION: PENDING\n"
            ),
        })
        hits = check_repo_reports_pending(zf)
        assert len(hits) == 1
        zip_path, pattern = hits[0]
        assert zip_path == "repo/reports/r46/final-verdict.md"
        assert "BUNDLE_VALIDATION: PENDING" in pattern

    def test_r45_defect_reproduced(self):
        """Reproduce the R45 defect: bundle built before final-verdict updated."""
        r45_bundle_content = (
            "# R45 Final Verdict\n"
            "**Sprint:** FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001\n"
            "BUNDLE_VALIDATION: PENDING\n"
            "Bundle: C:\\\\Users\\\\prora\\\\.local\\\\r45-bundle.zip\n"
        )
        zf = _make_zip({
            "repo/reports/r45/final-verdict.md": r45_bundle_content,
            "bundle-metadata/git-status-final.txt": "nothing to commit",
        })
        hits = check_repo_reports_pending(zf)
        assert len(hits) == 1
        assert hits[0][0] == "repo/reports/r45/final-verdict.md"

    def test_multiple_runs_multiple_hits(self):
        """Multiple final-verdict.md files — each PENDING one is reported."""
        zf = _make_zip({
            "repo/reports/r44/final-verdict.md": "BUNDLE_VALIDATION: PASS\n",
            "repo/reports/r45/final-verdict.md": "BUNDLE_VALIDATION: PENDING\n",
            "repo/reports/r46/final-verdict.md": "BUNDLE_VALIDATION: PENDING\n",
        })
        hits = check_repo_reports_pending(zf)
        assert len(hits) == 2
        hit_paths = {h[0] for h in hits}
        assert "repo/reports/r45/final-verdict.md" in hit_paths
        assert "repo/reports/r46/final-verdict.md" in hit_paths
        assert "repo/reports/r44/final-verdict.md" not in hit_paths

    def test_non_final_verdict_files_not_scanned(self):
        """Only final-verdict.md is scanned — not other files in repo/reports/."""
        zf = _make_zip({
            "repo/reports/r46/00-preflight.md": "BUNDLE_VALIDATION: PENDING\n",
            "repo/reports/r46/risk-register.md": "BUNDLE_VALIDATION: PENDING\n",
            "repo/reports/r46/final-verdict.md": "BUNDLE_VALIDATION: PASS\n",
        })
        hits = check_repo_reports_pending(zf)
        assert hits == []

    def test_nested_subdirectory_not_matched(self):
        """Files deeper than repo/reports/<run>/final-verdict.md are not scanned."""
        zf = _make_zip({
            "repo/reports/r46/subdir/final-verdict.md": "BUNDLE_VALIDATION: PENDING\n",
        })
        hits = check_repo_reports_pending(zf)
        assert hits == []

    def test_other_pending_patterns_detected(self):
        """Other PENDING_MARKER_PATTERNS inside final-verdict.md are also caught."""
        zf = _make_zip({
            "repo/reports/r46/final-verdict.md": (
                "# Verdict\n"
                "BUNDLE_VALIDATION: [PENDING]\n"
            ),
        })
        hits = check_repo_reports_pending(zf)
        assert len(hits) == 1

    def test_only_first_pattern_reported_per_file(self):
        """If multiple patterns match in one file, only one hit is reported per file."""
        zf = _make_zip({
            "repo/reports/r46/final-verdict.md": (
                "BUNDLE_VALIDATION: PENDING\n"
                "BUNDLE_VALIDATION: [PENDING]\n"
            ),
        })
        hits = check_repo_reports_pending(zf)
        assert len(hits) == 1

    def test_bundle_metadata_final_verdict_not_scanned(self):
        """bundle-metadata/final-verdict.md should NOT be scanned by this function."""
        zf = _make_zip({
            "bundle-metadata/final-verdict.md": "BUNDLE_VALIDATION: PENDING\n",
        })
        hits = check_repo_reports_pending(zf)
        assert hits == []

    def test_list_item_reference_not_flagged(self):
        """A markdown list item referencing BUNDLE_VALIDATION: PENDING is not flagged.

        This reproduces the R32 false-positive case where a final-verdict.md
        contained '- BUNDLE_VALIDATION: PENDING forward-documented' as a reference,
        not as an actual PENDING status line.
        """
        zf = _make_zip({
            "repo/reports/r32/final-verdict.md": (
                "# R32 Final Verdict\n"
                "- BUNDLE_VALIDATION: PENDING forward-documented\n"
                "BUNDLE_VALIDATION: PASS\n"
            ),
        })
        hits = check_repo_reports_pending(zf)
        assert hits == []

    def test_standalone_pending_in_r45_bundle(self):
        """Reproduce R45 actual defect: standalone BUNDLE_VALIDATION: PENDING is flagged."""
        zf = _make_zip({
            "repo/reports/r45/final-verdict.md": (
                "# R45 Final Verdict\n"
                "Bundle: C:\\\\path\\\\r45-bundle.zip\n"
                "BUNDLE_VALIDATION: PENDING (bundle not yet built)\n"
            ),
        })
        hits = check_repo_reports_pending(zf)
        assert len(hits) == 1
        assert hits[0][0] == "repo/reports/r45/final-verdict.md"


class TestValidatorIntegrationRepoReportsPending:
    """Integration check: verify the function exists and is importable."""

    def test_function_importable(self):
        """check_repo_reports_pending is importable from validate_evidence_bundle."""
        from tools.evidence.validate_evidence_bundle import check_repo_reports_pending
        assert callable(check_repo_reports_pending)

    def test_pending_marker_patterns_contains_bundle_validation_pending(self):
        """PENDING_MARKER_PATTERNS must include 'BUNDLE_VALIDATION: PENDING'."""
        assert "BUNDLE_VALIDATION: PENDING" in PENDING_MARKER_PATTERNS
