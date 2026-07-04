"""Tests for V130-V133: governance_validators_found_issue.py

V130: validate_dotnet_loc_cap_static
V131: validate_found_issue_disposition
V132: validate_found_issue_escalation
V133: validate_found_issue_invalid_disposition
"""
import json
import sys
from pathlib import Path

import pytest

SUPERVISOR_DIR = Path(__file__).parent.parent.parent / "tools" / "supervisor"
if str(SUPERVISOR_DIR) not in sys.path:
    sys.path.insert(0, str(SUPERVISOR_DIR))

from governance_validators_found_issue import (
    validate_dotnet_loc_cap_static,
    validate_found_issue_disposition,
    validate_found_issue_escalation,
    validate_found_issue_invalid_disposition,
    VALID_DISPOSITIONS,
)


# ── V130 ──────────────────────────────────────────────────────────────────────

class TestV130DotnetLocCapStatic:
    """V130: Proactive static scan of ALL .cs files vs baseline_loc_cap."""

    def test_pass_no_net_dir(self, tmp_path):
        """PASS when src/net/ does not exist."""
        result = validate_dotnet_loc_cap_static({}, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_pass_compliant_file(self, tmp_path):
        """PASS for .cs files with <=800 LOC."""
        net_dir = tmp_path / "src" / "net" / "csv"
        net_dir.mkdir(parents=True)
        content = "\n".join(f"// line {i}" for i in range(50))
        (net_dir / "CsvDocument.cs").write_text(content, encoding="utf-8")
        result = validate_dotnet_loc_cap_static({}, repo_root=tmp_path)
        assert result["result"] == "PASS"

    def test_warn_file_exceeds_800_no_baseline(self, tmp_path):
        """WARN when .cs file exceeds 800 LOC with no baseline entry."""
        net_dir = tmp_path / "src" / "net" / "fodt"
        net_dir.mkdir(parents=True)
        content = "\n".join(f"// line {i}" for i in range(850))
        (net_dir / "BigFile.cs").write_text(content, encoding="utf-8")
        result = validate_dotnet_loc_cap_static({}, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert any("BigFile.cs" in item.get("file", "") for item in result["items"])

    def test_warn_file_exceeds_frozen_cap(self, tmp_path):
        """WARN when known .cs file grows beyond its baseline_loc_cap."""
        net_dir = tmp_path / "src" / "net" / "fods"
        net_dir.mkdir(parents=True)
        cs_path = net_dir / "FodsDocumentCellProps.cs"
        content = "\n".join(f"// line {i}" for i in range(700))
        cs_path.write_text(content, encoding="utf-8")
        baseline = {
            "known_violations": {
                "src/net/fods/FodsDocumentCellProps.cs": {
                    "loc": 687, "baseline_loc_cap": 642,
                    "functions": 20, "baseline_functions_cap": 20,
                }
            }
        }
        reg_dir = tmp_path / "registry"
        reg_dir.mkdir(parents=True)
        (reg_dir / "source-structure-baseline.json").write_text(
            json.dumps(baseline), encoding="utf-8"
        )
        result = validate_dotnet_loc_cap_static({}, repo_root=tmp_path)
        assert result["result"] == "WARN"
        assert any("exceeds_frozen_cap" in item.get("reason", "") for item in result["items"])

    def test_pass_within_frozen_cap(self, tmp_path):
        """PASS when known .cs file LOC is within its baseline_loc_cap."""
        net_dir = tmp_path / "src" / "net" / "fods"
        net_dir.mkdir(parents=True)
        content = "\n".join(f"// line {i}" for i in range(900))
        (net_dir / "FodsDocument.cs").write_text(content, encoding="utf-8")
        baseline = {
            "known_violations": {
                "src/net/fods/FodsDocument.cs": {
                    "loc": 1293, "baseline_loc_cap": 1293,
                    "functions": 50, "baseline_functions_cap": 50,
                }
            }
        }
        reg_dir = tmp_path / "registry"
        reg_dir.mkdir(parents=True)
        (reg_dir / "source-structure-baseline.json").write_text(
            json.dumps(baseline), encoding="utf-8"
        )
        result = validate_dotnet_loc_cap_static({}, repo_root=tmp_path)
        assert result["result"] == "PASS"


# ── V131 ──────────────────────────────────────────────────────────────────────

class TestV131FoundIssueDisposition:
    """V131: Each found_issue entry must have a disposition field (WARN if missing)."""

    def test_pass_no_found_issues(self):
        """PASS when no found_issues in declaration."""
        result = validate_found_issue_disposition({})
        assert result["result"] == "PASS"

    def test_pass_empty_found_issues(self):
        """PASS when found_issues is empty list."""
        result = validate_found_issue_disposition({"found_issues": []})
        assert result["result"] == "PASS"

    def test_pass_all_have_disposition(self):
        """PASS when all FI items have a disposition."""
        decl = {
            "found_issues": [
                {"id": "FI-001", "disposition": "risk_not_reduced"},
                {"id": "FI-002", "disposition": "partially_done"},
            ]
        }
        result = validate_found_issue_disposition(decl)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_warn_missing_disposition(self):
        """WARN when FI item has no disposition field."""
        decl = {"found_issues": [{"id": "FI-001"}]}
        result = validate_found_issue_disposition(decl)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert any("FI-001" in item for item in result["items"])

    def test_warn_empty_disposition(self):
        """WARN when FI item has disposition='' (empty string)."""
        decl = {"found_issues": [{"id": "FI-003", "disposition": ""}]}
        result = validate_found_issue_disposition(decl)
        assert result["result"] == "WARN"


# ── V132 ──────────────────────────────────────────────────────────────────────

class TestV132FoundIssueEscalation:
    """V132: FI items with risk_not_reduced must have an escalation_plan (WARN if missing)."""

    def test_pass_no_found_issues(self):
        """PASS when no found_issues in declaration."""
        result = validate_found_issue_escalation({})
        assert result["result"] == "PASS"

    def test_pass_risk_not_reduced_with_plan(self):
        """PASS when risk_not_reduced FI has escalation_plan."""
        decl = {
            "found_issues": [{
                "id": "FI-004",
                "disposition": "risk_not_reduced",
                "escalation_plan": "File HEAL taskcard for TC-HEAL-NET-003 next sprint",
            }]
        }
        result = validate_found_issue_escalation(decl)
        assert result["result"] == "PASS"

    def test_warn_risk_not_reduced_without_plan(self):
        """WARN when risk_not_reduced FI lacks escalation_plan."""
        decl = {"found_issues": [{"id": "FI-004", "disposition": "risk_not_reduced"}]}
        result = validate_found_issue_escalation(decl)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert any("FI-004" in item for item in result["items"])

    def test_pass_other_disposition_no_plan_needed(self):
        """PASS when FI is partially_done - no escalation_plan needed."""
        decl = {"found_issues": [{"id": "FI-002", "disposition": "partially_done"}]}
        result = validate_found_issue_escalation(decl)
        assert result["result"] == "PASS"

    def test_pass_not_attempted_no_plan_needed(self):
        """PASS when FI is not_attempted - escalation_plan not required."""
        decl = {"found_issues": [{"id": "FI-006", "disposition": "not_attempted"}]}
        result = validate_found_issue_escalation(decl)
        assert result["result"] == "PASS"


# ── V133 ──────────────────────────────────────────────────────────────────────

class TestV133FoundIssueInvalidDisposition:
    """V133: FI disposition must be one of 6 valid values. FAIL (blocks_sprint=True) if invalid."""

    def test_pass_no_found_issues(self):
        """PASS when no found_issues in declaration."""
        result = validate_found_issue_invalid_disposition({})
        assert result["result"] == "PASS"

    def test_pass_empty_found_issues(self):
        """PASS when found_issues is empty list."""
        result = validate_found_issue_invalid_disposition({"found_issues": []})
        assert result["result"] == "PASS"

    @pytest.mark.parametrize("disp", sorted(VALID_DISPOSITIONS))
    def test_pass_all_valid_dispositions(self, disp):
        """PASS for all 6 valid disposition values."""
        decl = {"found_issues": [{"id": "FI-001", "disposition": disp}]}
        result = validate_found_issue_invalid_disposition(decl)
        assert result["result"] == "PASS", f"Expected PASS for valid disposition '{disp}'"

    def test_fail_invalid_disposition_pre_existing(self):
        """FAIL when disposition='pre-existing' — not in the 6-item list."""
        decl = {"found_issues": [{"id": "FI-001", "disposition": "pre-existing"}]}
        result = validate_found_issue_invalid_disposition(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any("FI-001" in item for item in result["items"])

    def test_fail_no_disposition_field(self):
        """FAIL when FI item has no disposition at all."""
        decl = {"found_issues": [{"id": "FI-005"}]}
        result = validate_found_issue_invalid_disposition(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_fail_garbage_disposition(self):
        """FAIL for arbitrary invalid string in disposition."""
        decl = {"found_issues": [{"id": "FI-006", "disposition": "done-ish"}]}
        result = validate_found_issue_invalid_disposition(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_fail_multiple_invalid_items(self):
        """FAIL lists all invalid FI items."""
        decl = {
            "found_issues": [
                {"id": "FI-001", "disposition": "pre-existing"},
                {"id": "FI-002", "disposition": "completed_verified"},  # valid
                {"id": "FI-003", "disposition": "wontfix"},
            ]
        }
        result = validate_found_issue_invalid_disposition(decl)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        fi_ids_in_items = " ".join(result["items"])
        assert "FI-001" in fi_ids_in_items
        assert "FI-003" in fi_ids_in_items
        assert "FI-002" not in fi_ids_in_items
