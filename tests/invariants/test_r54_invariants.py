"""
test_r54_invariants.py — Tests for INV-006..010 (R54 Lane 12).

Tests that the five new physical invariants (sidecar protocol, placeholder
guard, contract metadata floor, fodt writer capability, and closed taskcard
evidence) function correctly against synthetic fixtures.

R54 Sprint: FORMAT-FACTORY-R54-SIDECAR-ENFORCEMENT-FODT-PRESERVATION-PHASE5-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from tools.evidence.check_repo_invariants import (
    check_inv006_sidecar_not_tracked,
    check_inv007_no_proof_placeholder,
    check_inv008_contract_metadata_floor,
    check_inv009_fodt_writer_list_table,
    check_inv010_closed_taskcards_have_evidence,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_tmp_root(tmp_path: Path, structure: dict) -> Path:
    """Create a minimal fake repo root with the given file structure.
    structure: {relative_path: content_string}. None content = empty dir.
    """
    for rel, content in structure.items():
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if content is not None:
            p.write_text(content, encoding="utf-8")
    return tmp_path


# ---------------------------------------------------------------------------
# INV-006: sidecar_proof_file_not_in_bundle_zip
# ---------------------------------------------------------------------------

class TestInv006SidecarNotTracked:
    def test_no_git_dir_returns_pass(self, tmp_path):
        root = make_tmp_root(tmp_path, {})
        result = check_inv006_sidecar_not_tracked(root)
        assert result["passed"] is True
        assert "NO_GIT_REPO" in result["details"][0]

    def test_real_repo_passes(self):
        """The actual repo should have no sidecar tracked (gitignored in .local/)."""
        result = check_inv006_sidecar_not_tracked(PROJECT_ROOT)
        assert result["passed"] is True, result["details"]


# ---------------------------------------------------------------------------
# INV-007: no_proof_file_placeholder_in_final_verdict
# ---------------------------------------------------------------------------

class TestInv007NoProofPlaceholder:
    def test_no_reports_dir_returns_pass(self, tmp_path):
        result = check_inv007_no_proof_placeholder(tmp_path)
        assert result["passed"] is True

    def test_clean_verdict_passes(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "reports/r99/final-verdict.md": "## Verdict\nBUNDLE_VALIDATION: PASS\n",
        })
        result = check_inv007_no_proof_placeholder(root)
        assert result["passed"] is True

    def test_placeholder_in_latest_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "reports/r99/final-verdict.md":
                "## Verdict\n*To be updated after build.*\nBUNDLE_VALIDATION: PENDING\n",
        })
        result = check_inv007_no_proof_placeholder(root)
        assert result["passed"] is False
        assert "updated after" in result["details"][0]

    def test_placeholder_in_old_sprint_ignored(self, tmp_path):
        """Old sprint with placeholder should not fail — only latest sprint checked."""
        root = make_tmp_root(tmp_path, {
            "reports/r10/final-verdict.md":
                "*To be updated after build.*\nBUNDLE_VALIDATION: PENDING\n",
            "reports/r99/final-verdict.md":
                "## Verdict\nBUNDLE_VALIDATION: PASS\n",
        })
        result = check_inv007_no_proof_placeholder(root)
        assert result["passed"] is True
        assert "r99" in result["details"][0]

    def test_real_repo_passes(self):
        result = check_inv007_no_proof_placeholder(PROJECT_ROOT)
        assert result["passed"] is True, result["details"]


# ---------------------------------------------------------------------------
# INV-008: contract_metadata_floor_readable
# ---------------------------------------------------------------------------

class TestInv008ContractMetadataFloor:
    def test_no_contracts_dir_fails(self, tmp_path):
        result = check_inv008_contract_metadata_floor(tmp_path)
        assert result["passed"] is False

    def test_contract_with_valid_floor_passes(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "tools/evidence/contracts/r99-test.yaml":
                "run_number: R99\nmin_metadata_count: 30\nrequired_repo_files: []\n",
        })
        result = check_inv008_contract_metadata_floor(root)
        assert result["passed"] is True
        assert "30" in result["details"][0]

    def test_contract_missing_floor_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "tools/evidence/contracts/r99-test.yaml":
                "run_number: R99\nrequired_repo_files: []\n",
        })
        result = check_inv008_contract_metadata_floor(root)
        assert result["passed"] is False
        assert "missing" in result["details"][0]

    def test_contract_floor_zero_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "tools/evidence/contracts/r99-test.yaml":
                "run_number: R99\nmin_metadata_count: 0\n",
        })
        result = check_inv008_contract_metadata_floor(root)
        assert result["passed"] is False

    def test_real_repo_passes(self):
        result = check_inv008_contract_metadata_floor(PROJECT_ROOT)
        assert result["passed"] is True, result["details"]


# ---------------------------------------------------------------------------
# INV-009: fodt_writer_has_list_and_table_support
# ---------------------------------------------------------------------------

class TestInv009FodtWriterListTable:
    def test_writer_missing_fails(self, tmp_path):
        result = check_inv009_fodt_writer_list_table(tmp_path)
        assert result["passed"] is False
        assert "not found" in result["details"][0]

    def test_writer_missing_write_list_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "src/python/fodt/writer.py":
                "def _write_table(parent, table):\n    pass\n",
        })
        result = check_inv009_fodt_writer_list_table(root)
        assert result["passed"] is False
        assert any("_write_list" in d for d in result["details"])

    def test_writer_missing_write_table_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "src/python/fodt/writer.py":
                "def _write_list(parent, lst):\n    pass\n",
        })
        result = check_inv009_fodt_writer_list_table(root)
        assert result["passed"] is False
        assert any("_write_table" in d for d in result["details"])

    def test_writer_with_both_passes(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "src/python/fodt/writer.py":
                "def _write_list(parent, lst):\n    pass\n\ndef _write_table(parent, table):\n    pass\n",
        })
        result = check_inv009_fodt_writer_list_table(root)
        assert result["passed"] is True

    def test_real_repo_passes(self):
        result = check_inv009_fodt_writer_list_table(PROJECT_ROOT)
        assert result["passed"] is True, result["details"]


# ---------------------------------------------------------------------------
# INV-010: closed_taskcards_have_closure_evidence
# ---------------------------------------------------------------------------

class TestInv010ClosedTaskcardsHaveEvidence:
    def test_no_taskcards_dir_returns_pass(self, tmp_path):
        result = check_inv010_closed_taskcards_have_evidence(tmp_path)
        assert result["passed"] is True

    def test_open_taskcard_skipped(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "taskcards/TC-0001-test.md": "Status: OPEN\n## Description\nNot done.\n",
        })
        result = check_inv010_closed_taskcards_have_evidence(root)
        assert result["passed"] is True

    def test_closed_with_evidence_passes(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "taskcards/TC-0001-test.md":
                "Status: CLOSED_VERIFIED\n## Closure\nclosed_sprint: R53, 2026-05-22\n",
        })
        result = check_inv010_closed_taskcards_have_evidence(root)
        assert result["passed"] is True

    def test_closed_without_evidence_fails(self, tmp_path):
        root = make_tmp_root(tmp_path, {
            "taskcards/TC-0001-test.md":
                "Status: CLOSED_VERIFIED\n## Description\nDone somehow.\n",
        })
        result = check_inv010_closed_taskcards_have_evidence(root)
        assert result["passed"] is False
        assert "TC-0001-test.md" in result["details"][0]

    def test_real_repo_passes(self):
        result = check_inv010_closed_taskcards_have_evidence(PROJECT_ROOT)
        assert result["passed"] is True, result["details"]
