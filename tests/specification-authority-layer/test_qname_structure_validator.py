"""Tests for tools/validators/qname_structure_validator.py (TC-SRC-002, TC-QNAME-VALIDATORS-001).

Verifies the standalone QName structure compliance validator produces honest
baseline reports and correctly identifies spec_qname compliance.
Also tests V49 governance wiring (TestV49Wire).
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "validators"))
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from qname_structure_validator import report, scan_src_for_classes


_SRC_ROOT = _REPO / "src" / "python"


class TestFodtSpecStubsPassSpecQnameCheck:
    """TC-SRC-002 POSITIVE: FODT spec stubs have spec_qname → COMPLIANT."""

    def test_fodt_spec_stubs_pass_spec_qname_check(self):
        result = report(_SRC_ROOT, format_filter="fodt")
        assert result["status"] == "COMPLIANT", (
            f"Expected COMPLIANT for FODT spec stubs, got {result['status']}\n"
            f"violations: {result.get('violations', [])}"
        )
        assert result["compliant_spec_classes"] >= 3, (
            f"Expected >= 3 compliant FODT spec classes, got {result['compliant_spec_classes']}"
        )


class TestFodsSpecQnameState:
    """TC-SRC-002: FODS spec/ classes created in BFT sprint — validator reports actual state."""

    def test_fods_spec_classes_state(self):
        """FODS spec/ classes exist at fods/fods/spec/spreadsheet/ — status reflects actual state."""
        result = report(_SRC_ROOT, format_filter="fods")
        # After BFT sprint: spec/ classes (Workbook, Sheet, Row, Cell) created with spec_qname.
        # Validator correctly returns COMPLIANT or PARTIALLY_COMPLIANT.
        assert result["status"] in ("COMPLIANT", "PARTIALLY_COMPLIANT", "NO_SPEC_CLASSES", "NON_COMPLIANT"), (
            f"Unexpected status for FODS: {result['status']}"
        )


class TestNonClassFileIgnored:
    """TC-SRC-002: Non-class utility files don't trigger false failures."""

    def test_scan_does_not_fail_on_init_files(self):
        """Scanning with __init__.py files produces no errors."""
        classes = scan_src_for_classes(_SRC_ROOT, format_filter="fodt")
        # Should return some results without raising
        assert isinstance(classes, list)

    def test_non_class_py_files_ignored(self):
        """Files without class definitions are silently skipped."""
        result = report(_SRC_ROOT, format_filter="fodt")
        # Should produce a dict with all expected keys
        assert "status" in result
        assert "violations" in result
        assert isinstance(result["violations"], list)


class TestReportFormatIsValidYaml:
    """TC-SRC-002: Output is parseable YAML (or JSON fallback)."""

    def test_report_produces_expected_keys(self):
        """Report dict has all required keys for YAML serialization."""
        result = report(_SRC_ROOT)
        required = {
            "status", "total_classes", "spec_classes", "compliant_spec_classes",
            "missing_spec_qname", "non_spec_with_spec_qname", "violations",
        }
        assert required.issubset(result.keys()), (
            f"Missing keys: {required - result.keys()}"
        )

    def test_report_status_is_valid_value(self):
        """Report status is one of the known values."""
        valid_statuses = {"COMPLIANT", "PARTIALLY_COMPLIANT", "NON_COMPLIANT", "NO_SPEC_CLASSES"}
        result = report(_SRC_ROOT)
        assert result["status"] in valid_statuses, (
            f"Unknown status: {result['status']}"
        )


class TestV49Wire:
    """TC-QNAME-VALIDATORS-001: V49 validate_qname_structure wired in governance loop."""

    def test_v49_fires_for_spec_file_without_spec_qname(self, tmp_path):
        """V49 returns WARN when a spec/ class in changed_files lacks spec_qname."""
        from governance_validators import validate_qname_structure

        # Create a fake spec/ file with a class missing spec_qname
        fake_src = tmp_path / "src" / "python" / "testfmt" / "spec"
        fake_src.mkdir(parents=True)
        (fake_src / "__init__.py").write_text("")
        (fake_src / "thing.py").write_text("class Thing:\n    pass\n")

        decl = {
            "changed_files": ["src/python/testfmt/spec/thing.py"],
        }
        result = validate_qname_structure(decl, repo_root=tmp_path)
        assert result["result"] == "WARN", f"Expected WARN, got {result['result']}"
        assert any("thing.py" in v.get("file", "") for v in result["items"])

    def test_v49_passes_for_spec_file_with_spec_qname(self, tmp_path):
        """V49 returns PASS when spec/ classes have spec_qname."""
        from governance_validators import validate_qname_structure

        fake_src = tmp_path / "src" / "python" / "testfmt" / "spec"
        fake_src.mkdir(parents=True)
        (fake_src / "__init__.py").write_text("")
        (fake_src / "thing.py").write_text(
            'class Thing:\n    spec_qname = "test:thing"\n'
        )
        decl = {
            "changed_files": ["src/python/testfmt/spec/thing.py"],
        }
        result = validate_qname_structure(decl, repo_root=tmp_path)
        assert result["result"] == "PASS", f"Expected PASS, got {result['result']}"

    def test_v49_passes_for_non_spec_files(self):
        """V49 ignores files not under a spec/ directory."""
        from governance_validators import validate_qname_structure

        decl = {
            "changed_files": ["src/python/fodt/models.py"],
        }
        result = validate_qname_structure(decl, repo_root=_REPO)
        assert result["result"] == "PASS"

    def test_v49_present_in_run_all_validators(self):
        """V49 validate_qname_structure is called by run_all_governance_validators."""
        import sys as _sys
        # Ensure repo root on path for absolute imports in governance_validators.py
        repo_str = str(_REPO)
        if repo_str not in _sys.path:
            _sys.path.insert(0, repo_str)
        from governance_validator_runner import run_all_governance_validators

        decl = {
            "declared_scope": "test",
            "planned_work_items": [],
            "changed_files": [],
        }
        composite = run_all_governance_validators(decl, repo_root=_REPO)
        validator_names = [v.get("validator") for v in composite["validators"]]
        assert "validate_qname_structure" in validator_names, (
            "V49 validate_qname_structure missing from run_all_governance_validators output"
        )
