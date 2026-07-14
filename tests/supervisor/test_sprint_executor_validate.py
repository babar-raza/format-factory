"""
TC-A4: Unit tests for tools/supervisor/sprint_executor_validate.py

8 cases: fence stripping, banned field removal, missing field detection,
completed_work_items string enforcement, evidence_artifacts object enforcement,
acceptance_criteria string enforcement, --repair writes back, clean PASS.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
_VALIDATOR = _REPO / "tools" / "supervisor" / "sprint_executor_validate.py"

# Minimal valid skeleton (all 21 required fields, no banned fields)
_VALID_BASE = {
    "run_id": "test-run-001-abc1234",
    "sprint_id": "test-sprint-001",
    "evidence_root": ".local/evidences/test-run-001-abc1234",
    "start_time": "2026-06-16T00:00:00Z",
    "end_time": "2026-06-16T01:00:00Z",
    "git_head_start": "abc1234",
    "git_head_end": "abc1234",
    "git_status_final": "M src/test.py",
    "declared_scope": "test scope",
    "planned_work_items": [],
    "completed_work_items": [],
    "incomplete_work_items": [],
    "changed_files": [],
    "tests_run": 0,
    "test_results": {"passed": 0, "failed": 0, "skipped": 0, "errors": 0},
    "evidence_artifacts": [],
    "reports_created": [],
    "worker_self_verdict": "test",
    "worker_self_grade": "PASS",
    "next_recommended_work": [],
}


def _write_yaml(path: Path, doc: dict) -> None:
    path.write_text(
        yaml.dump(doc, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )


def _validate(path: Path, repair: bool = False) -> tuple[int, dict]:
    args = [sys.executable, str(_VALIDATOR), str(path)]
    if repair:
        args.append("--repair")
    result = subprocess.run(args, capture_output=True, text=True, cwd=str(_REPO))
    # Extract JSON from stdout — use raw_decode to find the first complete JSON object
    # (avoids confusion from repair messages containing { } characters)
    stdout = result.stdout.strip()
    start = stdout.find("{")
    if start >= 0:
        try:
            data, _ = json.JSONDecoder().raw_decode(stdout, start)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
    return result.returncode, data


class TestFenceStripping:
    """TC-A4-1: Markdown fences are stripped by --repair."""

    def test_strips_yaml_fences(self, tmp_path):
        test_file = tmp_path / "fenced.yaml"
        content = "```yaml\n" + yaml.dump(_VALID_BASE) + "\n```"
        test_file.write_text(content, encoding="utf-8")

        rc, data = _validate(test_file, repair=True)
        assert rc == 0, f"Expected exit 0 after fence repair, got {rc}: {data}"
        assert "Stripped markdown code fences" in data.get("repairs", [])

        repaired = test_file.read_text(encoding="utf-8")
        assert not repaired.startswith("```"), "Fences not stripped from file"

    def test_strips_plain_fences(self, tmp_path):
        test_file = tmp_path / "plain_fenced.yaml"
        content = "```\n" + yaml.dump(_VALID_BASE) + "\n```"
        test_file.write_text(content, encoding="utf-8")

        rc, data = _validate(test_file, repair=True)
        assert rc == 0


class TestBannedFieldRemoval:
    """TC-A4-2: Banned fields are removed by --repair."""

    @pytest.mark.parametrize("banned_field", [
        "schema_version", "tests_failed", "tests_passed", "tests_skipped", "worker_id",
    ])
    def test_removes_banned_field(self, tmp_path, banned_field):
        doc = dict(_VALID_BASE)
        doc[banned_field] = "should-be-removed"
        test_file = tmp_path / f"banned_{banned_field}.yaml"
        _write_yaml(test_file, doc)

        rc, data = _validate(test_file, repair=True)
        assert rc == 0, f"Expected PASS after removing {banned_field}, got: {data}"
        assert any(banned_field in r for r in data.get("repairs", [])), (
            f"Expected repair message for {banned_field}, got: {data.get('repairs')}"
        )

        repaired = yaml.safe_load(test_file.read_text(encoding="utf-8"))
        assert banned_field not in repaired, f"{banned_field} still in repaired file"


class TestMissingFieldDetection:
    """TC-A4-3: Missing required fields are reported as errors."""

    def test_reports_missing_required_field(self, tmp_path):
        doc = dict(_VALID_BASE)
        del doc["worker_self_verdict"]
        test_file = tmp_path / "missing_field.yaml"
        _write_yaml(test_file, doc)

        rc, data = _validate(test_file, repair=False)
        assert rc != 0, "Expected non-zero for missing required field"
        errors = data.get("errors", [])
        assert any("worker_self_verdict" in e for e in errors), (
            f"Expected error about worker_self_verdict, got: {errors}"
        )

    def test_reports_all_missing_fields_when_empty(self, tmp_path):
        test_file = tmp_path / "empty.yaml"
        test_file.write_text("run_id: only-one-field\n", encoding="utf-8")

        rc, data = _validate(test_file, repair=False)
        assert rc != 0
        errors = data.get("errors", [])
        # Should report multiple MISSING errors
        missing_errors = [e for e in errors if "MISSING" in e]
        assert len(missing_errors) >= 5, (
            f"Expected many MISSING errors, got: {missing_errors}"
        )


class TestCompletedWorkItemsEnforcement:
    """TC-A4-4: completed_work_items must be list of strings (item IDs)."""

    def test_repairs_dict_items_to_string(self, tmp_path):
        doc = dict(_VALID_BASE)
        doc["completed_work_items"] = [
            {"item_id": "TC-001", "title": "Some task"},
            "TC-002",  # already a string
        ]
        test_file = tmp_path / "cwi_dicts.yaml"
        _write_yaml(test_file, doc)

        rc, data = _validate(test_file, repair=True)
        assert rc == 0, f"Expected PASS after cwi repair: {data}"
        assert any("completed_work_items" in r for r in data.get("repairs", [])), (
            f"Expected repair message for completed_work_items: {data.get('repairs')}"
        )

        repaired = yaml.safe_load(test_file.read_text(encoding="utf-8"))
        for item in repaired["completed_work_items"]:
            assert isinstance(item, str), f"Expected string item, got {type(item)}: {item}"


class TestEvidenceArtifactsEnforcement:
    """TC-A4-5: evidence_artifacts items must be objects with path + type."""

    def test_repairs_string_artifacts_to_objects(self, tmp_path):
        doc = dict(_VALID_BASE)
        doc["evidence_artifacts"] = ["some/path/file.yaml"]
        test_file = tmp_path / "arts_strings.yaml"
        _write_yaml(test_file, doc)

        rc, data = _validate(test_file, repair=True)
        assert rc == 0, f"Expected PASS after artifact repair: {data}"
        assert any("evidence_artifacts" in r for r in data.get("repairs", [])), (
            f"Expected repair message for evidence_artifacts: {data.get('repairs')}"
        )

        repaired = yaml.safe_load(test_file.read_text(encoding="utf-8"))
        for art in repaired["evidence_artifacts"]:
            assert isinstance(art, dict), f"Expected dict artifact, got {type(art)}: {art}"
            assert "path" in art
            assert "type" in art

    def test_detects_artifact_missing_path(self, tmp_path):
        doc = dict(_VALID_BASE)
        doc["evidence_artifacts"] = [{"type": "file", "description": "no path"}]
        test_file = tmp_path / "arts_no_path.yaml"
        _write_yaml(test_file, doc)

        rc, data = _validate(test_file, repair=False)
        assert rc != 0
        errors = data.get("errors", [])
        assert any("path" in e for e in errors), f"Expected path error, got: {errors}"


class TestAcceptanceCriteriaEnforcement:
    """TC-A4-6: acceptance_criteria in planned_work_items must be string."""

    def test_repairs_list_acceptance_criteria(self, tmp_path):
        doc = dict(_VALID_BASE)
        doc["planned_work_items"] = [{
            "item_id": "TC-001",
            "title": "Test task",
            "status": "completed",
            "acceptance_criteria": ["criterion 1", "criterion 2"],
        }]
        test_file = tmp_path / "ac_list.yaml"
        _write_yaml(test_file, doc)

        rc, data = _validate(test_file, repair=True)
        assert rc == 0, f"Expected PASS after acceptance_criteria repair: {data}"
        assert any("acceptance_criteria" in r for r in data.get("repairs", [])), (
            f"Expected repair for acceptance_criteria: {data.get('repairs')}"
        )

        repaired = yaml.safe_load(test_file.read_text(encoding="utf-8"))
        item = repaired["planned_work_items"][0]
        assert isinstance(item["acceptance_criteria"], str), (
            f"Expected string, got {type(item['acceptance_criteria'])}"
        )


class TestRepairWritesBack:
    """TC-A4-7: --repair writes the fixed content back to the file."""

    def test_file_is_modified_in_place(self, tmp_path):
        doc = dict(_VALID_BASE)
        doc["schema_version"] = "1.0"  # banned field
        test_file = tmp_path / "repair_writeback.yaml"
        _write_yaml(test_file, doc)

        original_content = test_file.read_text(encoding="utf-8")
        assert "schema_version" in original_content

        _validate(test_file, repair=True)

        new_content = test_file.read_text(encoding="utf-8")
        assert "schema_version" not in new_content, (
            "File should have banned field removed by --repair"
        )

    def test_no_repair_flag_does_not_modify_file(self, tmp_path):
        doc = dict(_VALID_BASE)
        doc["schema_version"] = "1.0"
        test_file = tmp_path / "no_repair.yaml"
        _write_yaml(test_file, doc)

        original_content = test_file.read_text(encoding="utf-8")
        _validate(test_file, repair=False)

        new_content = test_file.read_text(encoding="utf-8")
        assert original_content == new_content, (
            "File should not be modified without --repair flag"
        )


class TestCleanDeclarationPasses:
    """TC-A4-8: A clean, valid declaration exits 0 with no errors."""

    def test_valid_declaration_passes(self, tmp_path):
        test_file = tmp_path / "valid.yaml"
        _write_yaml(test_file, _VALID_BASE)

        rc, data = _validate(test_file, repair=False)
        assert rc == 0, f"Expected PASS for valid declaration, got: {data}"
        assert data.get("passed") is True
        assert data.get("errors") == []

    def test_valid_declaration_with_artifacts_passes(self, tmp_path):
        doc = dict(_VALID_BASE)
        doc["evidence_artifacts"] = [
            {"path": "some/file.py", "type": "source", "description": "Test file",
             "related_work_items": ["TC-001"]}
        ]
        doc["planned_work_items"] = [{
            "item_id": "TC-001",
            "title": "Test task",
            "status": "completed",
            "acceptance_criteria": "Test passes",
        }]
        doc["completed_work_items"] = ["TC-001"]
        doc["tests_run"] = 5
        doc["test_results"] = {"passed": 5, "failed": 0, "skipped": 0, "errors": 0}

        test_file = tmp_path / "valid_full.yaml"
        _write_yaml(test_file, doc)

        rc, data = _validate(test_file, repair=False)
        assert rc == 0, f"Expected PASS for full valid declaration: {data}"


class TestPersistentPropertyRoundtrip:
    """TC-FGSQ-008: Phase 15 persistent-property roundtrip requirement checks."""

    def test_warn_persistent_property_missing_roundtrip_path(self, tmp_path):
        """PERSISTENT_PROPERTY work item without round_trip_test_path → WARN."""
        doc = dict(_VALID_BASE)
        doc["planned_work_items"] = [{
            "item_id": "TC-TEST-001",
            "title": "Add setter",
            "status": "completed",
            "acceptance_criteria": "Setter works",
            "work_type": "PERSISTENT_PROPERTY",
        }]
        test_file = tmp_path / "pp_no_rtp.yaml"
        _write_yaml(test_file, doc)
        rc, data = _validate(test_file, repair=False)
        assert rc == 0, "Missing round_trip_test_path should not FAIL (WARN only)"
        warns = data.get("persistent_property_warnings", [])
        assert any("round_trip_test_path is absent" in w for w in warns), warns

    def test_pass_persistent_property_with_valid_roundtrip_test(self, tmp_path):
        """PERSISTENT_PROPERTY with a valid Save/Load roundtrip test → no warning."""
        # Create fixture inside repo so relative path resolves correctly
        rel_path = "tests/supervisor/_pp_roundtrip_fixture.cs"
        rt_test = _REPO / rel_path
        rt_test.write_text("void Test() { doc.Save(path); doc.Load(path); }", encoding="utf-8")
        try:
            doc = dict(_VALID_BASE)
            doc["planned_work_items"] = [{
                "item_id": "TC-TEST-002",
                "title": "Add setter with roundtrip",
                "status": "completed",
                "acceptance_criteria": "Setter works",
                "work_type": "PERSISTENT_PROPERTY",
                "round_trip_test_path": rel_path,
            }]
            test_file = tmp_path / "pp_valid_rtp.yaml"
            _write_yaml(test_file, doc)
            rc, data = _validate(test_file, repair=False)
            warns = data.get("persistent_property_warnings", [])
            # File exists and contains Save+Load → no warning about this item
            assert not any("TC-TEST-002" in w for w in warns), warns
        finally:
            rt_test.unlink(missing_ok=True)

    def test_warn_persistent_property_roundtrip_file_missing(self, tmp_path):
        """PERSISTENT_PROPERTY round_trip_test_path points to non-existent file → WARN."""
        doc = dict(_VALID_BASE)
        doc["planned_work_items"] = [{
            "item_id": "TC-TEST-003",
            "title": "Setter with missing test",
            "status": "completed",
            "acceptance_criteria": "Works",
            "work_type": "PERSISTENT_PROPERTY",
            "round_trip_test_path": "nonexistent/RoundtripTest.cs",
        }]
        test_file = tmp_path / "pp_missing_file.yaml"
        _write_yaml(test_file, doc)
        rc, data = _validate(test_file, repair=False)
        warns = data.get("persistent_property_warnings", [])
        assert any("does not exist on disk" in w for w in warns), warns

    def test_no_warning_for_governance_change_work_type(self, tmp_path):
        """GOVERNANCE_CHANGE work items should not trigger roundtrip warnings."""
        doc = dict(_VALID_BASE)
        doc["planned_work_items"] = [{
            "item_id": "TC-GOV-001",
            "title": "Add validator",
            "status": "completed",
            "acceptance_criteria": "Validator runs",
            "work_type": "GOVERNANCE_CHANGE",
        }]
        test_file = tmp_path / "gov_change.yaml"
        _write_yaml(test_file, doc)
        rc, data = _validate(test_file, repair=False)
        warns = data.get("persistent_property_warnings", [])
        assert warns == [], warns
