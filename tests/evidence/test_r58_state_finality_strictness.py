"""
test_r58_state_finality_strictness.py — R58 Train C: State finality strictness.

Verifies that state/current-state.md PENDING verdict is caught by the validator.

R58 Sprint: FORMAT-FACTORY-R58-TRUE-SELF-VERIFYING-RC-REBUILD-PHASE9-EXPANSION-MEGA-TRAIN-001
IV-R57-004
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


class TestStateFinalityStrictness:
    """check_state_sprint_pending must catch PENDING verdict in state."""

    def test_pending_verdict_fails(self, tmp_path):
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/state/current-state.md", "**Latest sprint:** R58 - PENDING")
        from tools.evidence.validate_evidence_bundle import check_state_sprint_pending
        with zipfile.ZipFile(zp) as zf:
            errors = check_state_sprint_pending(zf)
        assert any("STATE_SPRINT_PENDING" in e for e in errors)

    def test_json_pending_fails(self, tmp_path):
        zp = tmp_path / "r58.zip"
        import json
        state = {"latest_sprint": {"latest_sprint_number": "R58", "verdict": "PENDING"}}
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/state/current-state.json", json.dumps(state))
        from tools.evidence.validate_evidence_bundle import check_state_sprint_pending
        with zipfile.ZipFile(zp) as zf:
            errors = check_state_sprint_pending(zf)
        assert any("STATE_SPRINT_PENDING" in e for e in errors)

    def test_complete_verdict_passes(self, tmp_path):
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/state/current-state.md",
                        "**Latest sprint:** R58 - R58_TRUE_SELF_VERIFYING_RC_REPLAYABLE_PHASE9_PARTIAL_PASS")
        from tools.evidence.validate_evidence_bundle import check_state_sprint_pending
        with zipfile.ZipFile(zp) as zf:
            errors = check_state_sprint_pending(zf)
        assert errors == []

    def test_no_state_file_passes(self, tmp_path):
        """No state file means skip check (not fail)."""
        zp = tmp_path / "r58.zip"
        with zipfile.ZipFile(zp, "w") as zf:
            zf.writestr("repo/README.md", "test")
        from tools.evidence.validate_evidence_bundle import check_state_sprint_pending
        with zipfile.ZipFile(zp) as zf:
            errors = check_state_sprint_pending(zf)
        assert errors == []
