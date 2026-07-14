"""Tests for QName spec_qname ClassVar enforcement (TC-GFB-024-01, FF-MR-2026-001).

Requirements: REQ-TEST-001 — Negative control: missing spec_qname blocks validator.

Validators tested:
- V111: validate_public_symbol_without_qname_authority (governance_validators_ext4.py)
  Returns {"passed": bool, "violations": [...]} — passed=False when spec_qname missing.
- V112: validate_model_type_without_spec_authority (governance_validators_ext4.py)
  Same return shape.

Note: V111/V112 check for plain assignment `spec_qname = '...'` via ast.Assign.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))


class TestV111MissingSpecQname:
    """NC-001: spec/ classes without spec_qname must fail V111."""

    def test_v111_fails_when_spec_qname_missing(self) -> None:
        """V111 must have passed=False when a spec/ class has no spec_qname."""
        from governance_validators_ext4 import validate_public_symbol_without_qname_authority

        source_code = (
            "class FakeModel:\n"
            "    def __init__(self):\n"
            "        self.value = None\n"
        )
        result = validate_public_symbol_without_qname_authority(
            source_code, file_path="src/python/fods/spec/fake/fake_model.py"
        )
        assert result["passed"] is False, (
            f"V111 must have passed=False for spec/ class missing spec_qname, got: {result}"
        )
        assert result["violations"], "V111 must report at least one violation"

    def test_v111_passes_when_spec_qname_assigned(self) -> None:
        """V111 must have passed=True when spec/ class has spec_qname plain assignment."""
        from governance_validators_ext4 import validate_public_symbol_without_qname_authority

        # V111 checks ast.Assign (plain assignment), not ast.AnnAssign (annotated ClassVar)
        source_code = (
            "class TableCell:\n"
            "    spec_qname = 'table:table-cell'\n"
            "    def __init__(self):\n"
            "        self.value = None\n"
        )
        result = validate_public_symbol_without_qname_authority(
            source_code, file_path="src/python/fods/spec/table/table_cell.py"
        )
        assert result["passed"] is True, (
            f"V111 must have passed=True for spec/ class with spec_qname, got: {result}"
        )
        assert not result["violations"], f"V111 must report no violations: {result}"

    def test_v111_ignores_non_spec_files(self) -> None:
        """V111 must not flag classes in non-spec/ files."""
        from governance_validators_ext4 import validate_public_symbol_without_qname_authority

        source_code = (
            "class FodsParser:\n"
            "    def __init__(self):\n"
            "        self.data = {}\n"
        )
        result = validate_public_symbol_without_qname_authority(
            source_code, file_path="src/python/fods/fods_parser.py"
        )
        # Non-spec/ files are not checked by V111
        assert result["passed"] is True, (
            f"V111 must not flag non-spec/ files: {result}"
        )


class TestV112MissingSpecQname:
    """NC-001: spec/ model classes without spec_qname must fail V112."""

    def test_v112_fails_when_spec_qname_missing(self) -> None:
        """V112 must have passed=False when a spec/ class has no spec_qname."""
        from governance_validators_ext4 import validate_model_type_without_spec_authority

        source_code = (
            "class CsvRecord:\n"
            "    def __init__(self):\n"
            "        self.fields = []\n"
        )
        result = validate_model_type_without_spec_authority(
            source_code, file_path="src/python/csv/spec/record/record.py"
        )
        assert result["passed"] is False, (
            f"V112 must have passed=False for spec/ model without spec_qname, got: {result}"
        )
        assert result["violations"], "V112 must report at least one violation"

    def test_v112_passes_when_spec_qname_assigned(self) -> None:
        """V112 must have passed=True when spec/ class has spec_qname."""
        from governance_validators_ext4 import validate_model_type_without_spec_authority

        source_code = (
            "class CsvRecord:\n"
            "    spec_qname = 'csv:record'\n"
            "    def __init__(self):\n"
            "        self.fields = []\n"
        )
        result = validate_model_type_without_spec_authority(
            source_code, file_path="src/python/csv/spec/record/record.py"
        )
        assert result["passed"] is True, (
            f"V112 must have passed=True for spec/ model with spec_qname, got: {result}"
        )

    def test_v112_ignores_non_spec_non_model_files(self) -> None:
        """V112 must ignore files not in spec/ or Model/ directories."""
        from governance_validators_ext4 import validate_model_type_without_spec_authority

        source_code = "class Foo:\n    pass\n"
        result = validate_model_type_without_spec_authority(
            source_code, file_path="src/python/csv/csv_parser.py"
        )
        assert result["passed"] is True, (
            f"V112 must not flag non-spec/ non-Model/ files: {result}"
        )


class TestDryRunDetectsGaps:
    """dry_run_migration.py must correctly detect spec_qname gaps."""

    def test_dry_run_detects_missing_spec_qname_in_csv(self) -> None:
        """dry_run must flag spec/ classes without spec_qname ClassVar."""
        sys.path.insert(0, str(REPO_ROOT / "tools" / "backfill"))
        from dry_run_migration import _find_classes_missing_spec_qname

        results = _find_classes_missing_spec_qname("csv")
        # All flagged entries should be in spec/ directories
        for r in results:
            assert "spec" in r["source_file"], (
                f"dry_run should only flag spec/ classes, got: {r['source_file']}"
            )

    def test_dry_run_src_mutations_always_zero(self) -> None:
        """dry_run_migration.run_dry_run must always report src_mutations=0."""
        sys.path.insert(0, str(REPO_ROOT / "tools" / "backfill"))
        from dry_run_migration import run_dry_run

        result = run_dry_run("csv", target_profile="MINIMAL")
        assert result["src_mutations"] == 0, (
            f"dry_run must never mutate src/ — src_mutations={result['src_mutations']}"
        )
        assert result["dry_run"] is True, "result must have dry_run=True"
