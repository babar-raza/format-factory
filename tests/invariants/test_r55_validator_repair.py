"""
test_r55_validator_repair.py — Tests for INV-011..014 (R55 Train A).

Tests that the four new physical invariants (state snapshot staleness,
completion matrix coverage, open taskcard sprint assignment, and final
verdict SHA placeholder guard) function correctly against synthetic fixtures.

R55 Sprint: FORMAT-FACTORY-R55-MULTI-MEGA-TRAIN-PRODUCT-RC-PHASE6-ACQUISITION-AI-VALIDATOR-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.check_repo_invariants import (
    check_inv011_state_snapshot_sprint_current,
    check_inv012_completion_matrix_covers_registry,
    check_inv013_open_taskcards_have_target_sprint,
    check_inv014_final_verdict_sha_not_placeholder,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_tmp_root(tmp_path: Path, structure: dict) -> Path:
    """Create a minimal fake repo root with the given file structure."""
    for rel, content in structure.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if content is not None:
            p.write_text(content, encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# INV-011: state_snapshot_sprint_matches_latest_contract
# ---------------------------------------------------------------------------

class TestInv011StateSnapshotSprintCurrent:

    def test_no_state_file_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "tools/evidence/contracts/r10.yaml": "run_number: R10\n",
        })
        result = check_inv011_state_snapshot_sprint_current(root)
        assert result["passed"] is False
        assert "not found" in result["details"][0]

    def test_state_matches_contract_passes(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "state/current-state.md": "**Latest sprint:** R10 - SOME_VERDICT\n",
            "tools/evidence/contracts/r10.yaml": "run_number: R10\n",
        })
        result = check_inv011_state_snapshot_sprint_current(root)
        assert result["passed"] is True

    def test_state_ahead_of_contract_passes(self, tmp_path):
        """State can be ahead (new sprint started but contract not yet finalized)."""
        root = make_tmp_root(tmp_path, {
            "state/current-state.md": "**Latest sprint:** R11 - no_final_verdict\n",
            "tools/evidence/contracts/r10.yaml": "run_number: R10\n",
        })
        result = check_inv011_state_snapshot_sprint_current(root)
        assert result["passed"] is True

    def test_state_behind_contract_fails(self, tmp_path):
        """State shows R9 but contract is R10 — stale snapshot."""
        root = make_tmp_root(tmp_path, {
            "state/current-state.md": "**Latest sprint:** R9 - SOME_VERDICT\n",
            "tools/evidence/contracts/r10.yaml": "run_number: R10\n",
        })
        result = check_inv011_state_snapshot_sprint_current(root)
        assert result["passed"] is False
        assert "R9" in result["details"][0]
        assert "R10" in result["details"][0]

    def test_no_contracts_dir_skipped(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "state/current-state.md": "**Latest sprint:** R9 - SOME_VERDICT\n",
        })
        result = check_inv011_state_snapshot_sprint_current(root)
        assert result["passed"] is True

    def test_real_repo_passes(self):
        result = check_inv011_state_snapshot_sprint_current(PROJECT_ROOT)
        assert result["passed"] is True, result["details"]

    def test_unparseable_state_sprint_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "state/current-state.md": "**Latest sprint:** unknown\n",
            "tools/evidence/contracts/r10.yaml": "run_number: R10\n",
        })
        result = check_inv011_state_snapshot_sprint_current(root)
        assert result["passed"] is False
        assert "parse" in result["details"][0].lower()


# ---------------------------------------------------------------------------
# INV-012: completion_matrix_has_all_registry_formats
# ---------------------------------------------------------------------------

class TestInv012CompletionMatrixCoversRegistry:

    def test_no_registry_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "registry/format-completion-matrix.yaml": "formats: []\n",
        })
        result = check_inv012_completion_matrix_covers_registry(root)
        assert result["passed"] is False
        assert "not found" in result["details"][0]

    def test_no_matrix_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "registry/format-registry.yaml": "formats:\n  - format_id: fods\n",
        })
        result = check_inv012_completion_matrix_covers_registry(root)
        assert result["passed"] is False
        assert "not found" in result["details"][0]

    def test_all_formats_covered_passes(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "registry/format-registry.yaml": "formats:\n  - format_id: fods\n  - format_id: fodt\n",
            "registry/format-completion-matrix.yaml": (
                "formats:\n"
                "  - format_id: fods\n    actual_maturity_class: production_track_real\n"
                "  - format_id: fodt\n    actual_maturity_class: production_track_real\n"
            ),
        })
        result = check_inv012_completion_matrix_covers_registry(root)
        assert result["passed"] is True

    def test_missing_format_in_matrix_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "registry/format-registry.yaml": "formats:\n  - format_id: fods\n  - format_id: zst\n",
            "registry/format-completion-matrix.yaml": (
                "formats:\n"
                "  - format_id: fods\n    actual_maturity_class: production_track_real\n"
            ),
        })
        result = check_inv012_completion_matrix_covers_registry(root)
        assert result["passed"] is False
        assert any("zst" in d for d in result["details"])

    def test_real_repo_passes(self):
        result = check_inv012_completion_matrix_covers_registry(PROJECT_ROOT)
        assert result["passed"] is True, result["details"]


# ---------------------------------------------------------------------------
# INV-013: open_taskcards_have_target_sprint
# ---------------------------------------------------------------------------

class TestInv013OpenTaskcardsHaveTargetSprint:

    def test_no_taskcards_dir_skipped(self, tmp_path):
        result = check_inv013_open_taskcards_have_target_sprint(tmp_path)
        assert result["passed"] is True
        assert "skipped" in result["details"][0].lower()

    def test_open_with_target_passes(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "taskcards/TC-0099-test.md": (
                "**Status:** OPEN\n"
                "**Sprint target:** R55 or later\n"
                "## Gap\nSome gap.\n"
            ),
        })
        result = check_inv013_open_taskcards_have_target_sprint(root)
        assert result["passed"] is True

    def test_open_without_target_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "taskcards/TC-0099-test.md": (
                "**Status:** OPEN\n"
                "## Gap\nSome gap without target.\n"
            ),
        })
        result = check_inv013_open_taskcards_have_target_sprint(root)
        assert result["passed"] is False
        assert "TC-0099-test.md" in result["details"][0]

    def test_closed_without_target_ok(self, tmp_path):
        """CLOSED_VERIFIED cards don't need a Sprint target."""
        root = make_tmp_root(tmp_path, {
            "taskcards/TC-0099-test.md": (
                "**Status:** CLOSED_VERIFIED\n"
                "## Closure\nClosed in R53, 2026-05-22.\n"
            ),
        })
        result = check_inv013_open_taskcards_have_target_sprint(root)
        assert result["passed"] is True

    def test_mixed_taskcards(self, tmp_path):
        """One OPEN with target = pass; one CLOSED without target = pass."""
        root = make_tmp_root(tmp_path, {
            "taskcards/TC-0001-open.md": (
                "**Status:** OPEN\n"
                "**Sprint target:** R55\n"
            ),
            "taskcards/TC-0002-closed.md": (
                "**Status:** CLOSED_VERIFIED\n"
                "## Closure\nR53, 2026-05-22.\n"
            ),
        })
        result = check_inv013_open_taskcards_have_target_sprint(root)
        assert result["passed"] is True

    def test_real_repo_passes(self):
        result = check_inv013_open_taskcards_have_target_sprint(PROJECT_ROOT)
        assert result["passed"] is True, result["details"]


# ---------------------------------------------------------------------------
# INV-014: final_verdict_pass_sha_not_placeholder
# ---------------------------------------------------------------------------

class TestInv014FinalVerdictShaNotPlaceholder:

    def test_no_reports_dir_skipped(self, tmp_path):
        result = check_inv014_final_verdict_sha_not_placeholder(tmp_path)
        assert result["passed"] is True

    def test_no_bundle_pass_line_skipped(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "reports/r10/final-verdict.md": (
                "## Verdict\nR10_STATE_FOO\n\nBUNDLE_VALIDATION: PENDING\n"
            ),
        })
        result = check_inv014_final_verdict_sha_not_placeholder(root)
        assert result["passed"] is True

    def test_bundle_pass_with_real_sha_passes(self, tmp_path):
        sha = "a" * 64
        root = make_tmp_root(tmp_path, {
            "reports/r10/final-verdict.md": (
                f"Pass 1 SHA-256: `{sha}`\n\nBUNDLE_VALIDATION: PASS\n"
            ),
        })
        result = check_inv014_final_verdict_sha_not_placeholder(root)
        assert result["passed"] is True

    def test_tbd_placeholder_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "reports/r10/final-verdict.md": (
                "Pass 1 SHA-256: TBD\n\nBUNDLE_VALIDATION: PASS\n"
            ),
        })
        result = check_inv014_final_verdict_sha_not_placeholder(root)
        # TBD is not a valid hex SHA — check fails (either "placeholder" or "no SHA line")
        assert result["passed"] is False

    def test_pending_placeholder_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "reports/r10/final-verdict.md": (
                "Pass 1 SHA-256: PENDING\n\nBUNDLE_VALIDATION: PASS\n"
            ),
        })
        result = check_inv014_final_verdict_sha_not_placeholder(root)
        assert result["passed"] is False

    def test_missing_sha_line_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "reports/r10/final-verdict.md": (
                "No SHA here.\n\nBUNDLE_VALIDATION: PASS\n"
            ),
        })
        result = check_inv014_final_verdict_sha_not_placeholder(root)
        assert result["passed"] is False
        assert "no 'Pass 1 SHA-256'" in result["details"][0]

    def test_real_repo_passes(self):
        """Real repo's latest final-verdict (R54) should have a real SHA."""
        result = check_inv014_final_verdict_sha_not_placeholder(PROJECT_ROOT)
        assert result["passed"] is True, result["details"]
