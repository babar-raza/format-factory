"""
tests/evidence/test_r82_rejects_deferred_stub_latest_state.py

R82 Train P: Validator must detect when state/current-state.md points to a deferred stub sprint.

Defect fixed: D79-10/11/12 — R79 bundle's state showed R81_DEFERRED_NOT_YET_EXECUTED
while the uploaded sprint was R79, causing a sprint-state mismatch.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
CURRENT_STATE_MD = REPO_ROOT / "state" / "current-state.md"

DEFERRED_STUB_VERDICTS = {
    "R81_DEFERRED_NOT_YET_EXECUTED",
    "DEFERRED_NOT_YET_EXECUTED",
    "NOT_STARTED",
    "NOT_YET_EXECUTED",
}


def _get_latest_sprint_verdict(state_md: Path) -> str:
    """Extract verdict from Latest sprint line."""
    content = state_md.read_text(encoding="utf-8")
    m = re.search(r"Latest sprint: \w+ - (.+)", content)
    if m:
        return m.group(1).strip()
    return "unknown"


def _is_deferred_stub_verdict(verdict: str) -> bool:
    return any(stub in verdict for stub in DEFERRED_STUB_VERDICTS)


class TestRejectsDeferredStubState:
    """State must not point to a deferred stub sprint as the latest executed sprint."""

    def test_deferred_verdict_is_detected(self):
        verdict = "R81_DEFERRED_NOT_YET_EXECUTED"
        assert _is_deferred_stub_verdict(verdict)

    def test_real_executed_verdict_is_not_deferred(self):
        verdict = "R79_FODS_INSTALLED_PACKAGE_PRODUCT_SLICE_READY_ZST_REPLAY_CLARIFIED_PUBLICATION_BLOCKED"
        assert not _is_deferred_stub_verdict(verdict)

    def test_current_state_does_not_point_to_deferred_stub(self):
        """After R82 authority normalization, state must not show a deferred stub verdict."""
        if not CURRENT_STATE_MD.exists():
            return
        verdict = _get_latest_sprint_verdict(CURRENT_STATE_MD)
        # This test is informational during active sprint execution
        # After Train S (state sync), this must pass
        assert not _is_deferred_stub_verdict(verdict), (
            f"state/current-state.md shows deferred stub verdict: '{verdict}'. "
            "Run state_snapshot.py after R82 final verdict is set."
        )

    def test_r79_verdict_is_not_deferred(self):
        """Historical check: R79 final-verdict.md is not a deferred stub."""
        r79_verdict = REPO_ROOT / "reports" / "r79" / "final-verdict.md"
        if not r79_verdict.exists():
            return
        content = r79_verdict.read_text(encoding="utf-8")
        assert "DEFERRED_NOT_YET_EXECUTED" not in content, \
            "R79 final-verdict.md must not contain DEFERRED_NOT_YET_EXECUTED"
        assert "R79_FODS_INSTALLED_PACKAGE_PRODUCT_SLICE_READY" in content, \
            "R79 must have its proper verdict"
