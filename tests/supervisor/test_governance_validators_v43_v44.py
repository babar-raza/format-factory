"""Tests for V43 (canonical_registry_entry_exists) and V44 (facade_delegates_to_spec).

V43 behavior:
  - WARN when shared/qname-registry/ does not exist (bootstrap phase)
  - PASS when registry exists and all spec/ files have spec_qname attribute
  - FAIL when registry exists but a spec/ file lacks spec_qname attribute

V44 behavior (upgraded from monitoring stub in TC-ZS-002):
  - PASS when no Compat files import architecture_only stubs
  - WARN when compat files import architecture_only stubs
  - Never blocks sprint
"""
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
_SUP = _REPO / "tools" / "supervisor"
if str(_SUP) not in sys.path:
    sys.path.insert(0, str(_SUP))

from governance_validators import (
    validate_canonical_registry_entry_exists,
    validate_facade_delegates_to_spec,
)


_EMPTY_DECL: dict = {"planned_work_items": []}


class TestV43CanonicalRegistryEntryExists:
    def test_warn_when_registry_dir_absent(self, tmp_path):
        """V43 must return WARN when shared/qname-registry/ does not exist."""
        result = validate_canonical_registry_entry_exists(_EMPTY_DECL, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert "bootstrap" in result["summary"].lower() or "absent" in result["summary"].lower()

    def test_pass_when_registry_exists_no_spec_files(self, tmp_path):
        """V43 must return PASS when registry exists but no spec/ files exist."""
        (tmp_path / "shared" / "qname-registry").mkdir(parents=True)
        (tmp_path / "shared" / "qname-registry" / "fodt.yaml").write_text("[]")
        (tmp_path / "src" / "python").mkdir(parents=True)
        result = validate_canonical_registry_entry_exists(_EMPTY_DECL, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_pass_when_all_spec_files_have_spec_qname(self, tmp_path):
        """V43 must return PASS when registry exists and all spec/ files have spec_qname."""
        (tmp_path / "shared" / "qname-registry").mkdir(parents=True)
        spec_dir = tmp_path / "src" / "python" / "fodt" / "spec" / "text"
        spec_dir.mkdir(parents=True)
        para_file = spec_dir / "paragraph.py"
        para_file.write_text('class Paragraph:\n    spec_qname = "text:p"\n')
        result = validate_canonical_registry_entry_exists(_EMPTY_DECL, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert len(result["items"]) == 0

    def test_fail_when_spec_file_missing_spec_qname(self, tmp_path):
        """V43 must return FAIL when registry exists but a spec/ file lacks spec_qname."""
        (tmp_path / "shared" / "qname-registry").mkdir(parents=True)
        spec_dir = tmp_path / "src" / "python" / "fodt" / "spec" / "text"
        spec_dir.mkdir(parents=True)
        bad_file = spec_dir / "paragraph.py"
        bad_file.write_text("class Paragraph:\n    pass\n")
        result = validate_canonical_registry_entry_exists(_EMPTY_DECL, repo_root=tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        assert "missing spec_qname" in result["items"][0]["reason"]

    def test_fail_blocks_sprint(self, tmp_path):
        """V43 FAIL must set blocks_sprint=True."""
        (tmp_path / "shared" / "qname-registry").mkdir(parents=True)
        spec_dir = tmp_path / "src" / "python" / "fodt" / "spec" / "text"
        spec_dir.mkdir(parents=True)
        (spec_dir / "bad.py").write_text("class Bad:\n    pass\n")
        result = validate_canonical_registry_entry_exists(_EMPTY_DECL, repo_root=tmp_path)
        assert result["blocks_sprint"] is True

    def test_init_files_excluded(self, tmp_path):
        """V43 must NOT check __init__.py files (they don't need spec_qname)."""
        (tmp_path / "shared" / "qname-registry").mkdir(parents=True)
        spec_dir = tmp_path / "src" / "python" / "fodt" / "spec" / "text"
        spec_dir.mkdir(parents=True)
        # __init__.py without spec_qname — should be excluded
        (spec_dir / "__init__.py").write_text("")
        result = validate_canonical_registry_entry_exists(_EMPTY_DECL, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert len(result["items"]) == 0

    def test_validator_key(self, tmp_path):
        """V43 must use validator key 'canonical_registry_entry_exists'."""
        result = validate_canonical_registry_entry_exists(_EMPTY_DECL, repo_root=tmp_path)
        assert result["validator"] == "canonical_registry_entry_exists"


class TestV44FacadeDelegatesToSpec:
    def test_always_warn(self):
        """V44 returns PASS when no compat files import architecture_only stubs (real inspection mode)."""
        result = validate_facade_delegates_to_spec(_EMPTY_DECL)
        assert result["result"] == "PASS"

    def test_never_blocks_sprint(self):
        """V44 must never set blocks_sprint=True."""
        result = validate_facade_delegates_to_spec(_EMPTY_DECL)
        assert result["blocks_sprint"] is False

    def test_no_items(self):
        """V44 must return empty items list when no violations exist."""
        result = validate_facade_delegates_to_spec(_EMPTY_DECL)
        assert result["items"] == []

    def test_validator_key(self):
        """V44 must use validator key 'facade_delegates_to_spec'."""
        result = validate_facade_delegates_to_spec(_EMPTY_DECL)
        assert result["validator"] == "facade_delegates_to_spec"

    def test_warn_with_any_declaration(self):
        """V44 returns PASS when no compat violations exist, regardless of declaration contents."""
        for decl in [
            {},
            {"planned_work_items": [{"item_type": "GOVERNANCE_ASSET"}]},
            {"planned_work_items": [{"item_type": "PRODUCT_SOURCE", "gap_ledger_ref": "GAP-001"}]},
        ]:
            result = validate_facade_delegates_to_spec(decl)
            assert result["result"] == "PASS"


class TestV43V44InRunAll:
    def test_v43_v44_included_in_run_all(self):
        """V43 and V44 must be registered in governance_validator_runner's results list.

        We verify this by inspecting the runner source code directly (avoids the
        pre-existing ModuleNotFoundError: 'tools' issue in run_all integration tests).
        """
        runner_path = _REPO / "tools" / "supervisor" / "governance_validator_runner.py"
        source = runner_path.read_text(encoding="utf-8")
        assert "validate_canonical_registry_entry_exists" in source, (
            "V43 (validate_canonical_registry_entry_exists) missing from governance_validator_runner.py"
        )
        assert "validate_facade_delegates_to_spec" in source, (
            "V44 (validate_facade_delegates_to_spec) missing from governance_validator_runner.py"
        )

    def test_total_validator_count_is_44_in_runner_source(self):
        """governance_validator_runner.py must list exactly 49 validator calls in results list."""
        runner_path = _REPO / "tools" / "supervisor" / "governance_validator_runner.py"
        source = runner_path.read_text(encoding="utf-8")
        # Count call lines: contain "(declaration" (actual calls, not import lines)
        call_lines = [
            line.strip() for line in source.splitlines()
            if "(declaration" in line and (
                line.strip().startswith("validate_") or line.strip().startswith("_validate_")
            )
        ]
        assert len(call_lines) == 49, (
            f"Expected 49 validator calls in runner, got {len(call_lines)}"
        )

    def test_v43_v44_defined_in_governance_validators(self):
        """V43/V44 function definitions must exist in governance_validators.py."""
        gv_path = _REPO / "tools" / "supervisor" / "governance_validators.py"
        source = gv_path.read_text(encoding="utf-8")
        assert "def validate_canonical_registry_entry_exists" in source, "V43 def missing"
        assert "def validate_facade_delegates_to_spec" in source, "V44 def missing"

    def test_run_all_reexported_from_governance_validators(self):
        """run_all_governance_validators must be importable from governance_validators."""
        gv_path = _REPO / "tools" / "supervisor" / "governance_validators.py"
        source = gv_path.read_text(encoding="utf-8")
        assert "from governance_validator_runner import run_all_governance_validators" in source, (
            "Re-export of run_all_governance_validators missing from governance_validators.py"
        )
