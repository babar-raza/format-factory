"""
test_r58_embedded_sidecar_rejected.py — R58 Train B: Sidecar embedded inside ZIP must fail.

Tests that the validator rejects bundles containing a sidecar committed to the repo
(and thus embedded inside the ZIP under repo/).

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
IV-R57-002
"""
from __future__ import annotations

import json
import sys
import zipfile
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


class TestEmbeddedSidecarRejection:
    """Embedded sidecar in repo portion of ZIP must be detected and rejected."""

    def test_no_sidecar_in_zip_passes(self, tmp_path):
        """Bundle without embedded sidecar passes the check."""
        bundle_name = "r58-clean.zip"
        zp = tmp_path / bundle_name
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/README.md", "test")
            zf.writestr("bundle-metadata/sprint-id.txt", "R58")
        from tools.evidence.validate_evidence_bundle import check_repo_sidecar_not_inside_zip
        with zipfile.ZipFile(zp) as zf:
            errors = check_repo_sidecar_not_inside_zip(zf, str(zp))
        assert errors == []

    def test_sidecar_for_different_bundle_passes(self, tmp_path):
        """A sidecar for a DIFFERENT bundle inside the ZIP is OK (historical record)."""
        bundle_name = "r58-bundle.zip"
        other_sidecar = json.dumps({
            "sidecar_version": "1.0",
            "bundle_filename": "r57-pass2-final.zip",  # different bundle
            "sha256": "a" * 64,
            "validation_result": "PASS",
        })
        zp = tmp_path / bundle_name
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/README.md", "test")
            zf.writestr("repo/reports/r57/r57-pass2-final.zip.sha256-proof.json", other_sidecar)
        from tools.evidence.validate_evidence_bundle import check_repo_sidecar_not_inside_zip
        with zipfile.ZipFile(zp) as zf:
            errors = check_repo_sidecar_not_inside_zip(zf, str(zp))
        assert errors == [], f"Sidecar for different bundle should not fail: {errors}"

    def test_sidecar_for_this_bundle_in_repo_fails(self, tmp_path):
        """Sidecar for THIS bundle committed to repo and thus inside ZIP fails."""
        bundle_name = "r58-final.zip"
        bad_sidecar = json.dumps({
            "sidecar_version": "1.0",
            "bundle_filename": bundle_name,
            "sha256": "b" * 64,
            "validation_result": "PASS",
        })
        zp = tmp_path / bundle_name
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/README.md", "test")
            zf.writestr(f"repo/reports/r58/{bundle_name}.sha256-proof.json", bad_sidecar)
        from tools.evidence.validate_evidence_bundle import check_repo_sidecar_not_inside_zip
        with zipfile.ZipFile(zp) as zf:
            errors = check_repo_sidecar_not_inside_zip(zf, str(zp))
        assert len(errors) == 1
        assert "SIDECAR_INSIDE_ZIP" in errors[0]
        assert bundle_name in errors[0]

    def test_pycache_in_bundle_fails(self, tmp_path):
        """Bundle with __pycache__ entries fails pycache check."""
        zp = tmp_path / "r58-dirty.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/src/python/fods/__pycache__/parser.cpython-313.pyc", b"\x00" * 10)
            zf.writestr("repo/README.md", "test")
        from tools.evidence.validate_evidence_bundle import check_pycache_in_bundle
        with zipfile.ZipFile(zp) as zf:
            errors = check_pycache_in_bundle(zf)
        assert len(errors) == 1
        assert "BUNDLE_PYCACHE_PRESENT" in errors[0]

    def test_no_pycache_in_bundle_passes(self, tmp_path):
        """Bundle without __pycache__ entries passes."""
        zp = tmp_path / "r58-clean.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/src/python/fods/parser.py", "# clean")
            zf.writestr("bundle-metadata/sprint-id.txt", "R58")
        from tools.evidence.validate_evidence_bundle import check_pycache_in_bundle
        with zipfile.ZipFile(zp) as zf:
            errors = check_pycache_in_bundle(zf)
        assert errors == []

    def test_state_sprint_pending_fails(self, tmp_path):
        """Bundle with state showing PENDING sprint fails."""
        zp = tmp_path / "r58-pending.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/state/current-state.md", "Latest sprint: R58 - PENDING")
            zf.writestr("bundle-metadata/sprint-id.txt", "R58")
        from tools.evidence.validate_evidence_bundle import check_state_sprint_pending
        with zipfile.ZipFile(zp) as zf:
            errors = check_state_sprint_pending(zf)
        assert any("STATE_SPRINT_PENDING" in e for e in errors)

    def test_state_sprint_complete_passes(self, tmp_path):
        """Bundle with state showing COMPLETE sprint passes."""
        zp = tmp_path / "r58-complete.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/state/current-state.md",
                        "Latest sprint: R58 - R58_TRUE_SELF_VERIFYING_RC_REPLAYABLE_PHASE9_PARTIAL_PASS")
            zf.writestr("bundle-metadata/sprint-id.txt", "R58")
        from tools.evidence.validate_evidence_bundle import check_state_sprint_pending
        with zipfile.ZipFile(zp) as zf:
            errors = check_state_sprint_pending(zf)
        assert errors == []

    def test_scoreboard_lane_in_progress_fails(self, tmp_path):
        """Bundle with IN_PROGRESS lane in scoreboard fails."""
        zp = tmp_path / "r58-inprogress.zip"
        scoreboard = """# R58 Scoreboard
| L | Final bundle | IN_PROGRESS | — |
**SCOREBOARD_STATUS: TRAIN_L_IN_PROGRESS**
"""
        verdict = "**Verdict:** R58_PRODUCT_EXPANSION_PASS_RC_REPLAY_PARTIAL"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/reports/r58/multi-mega-train-scoreboard.md", scoreboard)
            zf.writestr("repo/reports/r58/final-verdict.md", verdict)
            zf.writestr("bundle-metadata/sprint-id.txt", "R58")
        from tools.evidence.validate_evidence_bundle import check_scoreboard_lanes_in_progress
        with zipfile.ZipFile(zp) as zf:
            errors = check_scoreboard_lanes_in_progress(zf)
        assert any("IN_PROGRESS" in e for e in errors)

    def test_scoreboard_all_complete_passes(self, tmp_path):
        """Bundle with all COMPLETE lanes passes."""
        zp = tmp_path / "r58-allcomplete.zip"
        scoreboard = """# R58 Scoreboard
| L | Final bundle | COMPLETE | reports/r58/final-verdict.md |
**SCOREBOARD_STATUS: ALL_TRAINS_COMPLETE**
"""
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/reports/r58/multi-mega-train-scoreboard.md", scoreboard)
            zf.writestr("bundle-metadata/sprint-id.txt", "R58")
        from tools.evidence.validate_evidence_bundle import check_scoreboard_lanes_in_progress
        with zipfile.ZipFile(zp) as zf:
            errors = check_scoreboard_lanes_in_progress(zf)
        assert errors == []
