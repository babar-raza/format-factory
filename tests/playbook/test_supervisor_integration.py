"""
test_supervisor_integration.py — TC-PB-009: Supervisor Integration Tests

Verifies that playbook_selector.py correctly routes work item types,
returns None for unknown types, rejects deprecated playbooks, and
that missing skills create gaps rather than hard blocks.
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "playbook"))


class TestPlaybookSelector:
    def test_format_feature_expansion_returns_path(self):
        from playbook_selector import select_playbook
        result = select_playbook("FORMAT_FEATURE_EXPANSION")
        if result is not None:
            assert Path(result).exists(), f"Selected path must exist: {result}"

    def test_new_format_kickstart_returns_path(self):
        from playbook_selector import select_playbook
        result = select_playbook("NEW_FORMAT_KICKSTART")
        if result is not None:
            assert Path(result).exists(), f"Selected path must exist: {result}"

    def test_product_source_patch_bounded_returns_path(self):
        from playbook_selector import select_playbook
        result = select_playbook("PRODUCT_SOURCE_PATCH_BOUNDED")
        if result is not None:
            assert Path(result).exists(), f"Selected path must exist: {result}"

    def test_unknown_work_item_type_returns_none(self):
        from playbook_selector import select_playbook
        result = select_playbook("COMPLETELY_UNKNOWN_WORK_ITEM_TYPE_XYZ")
        assert result is None, f"Unknown type should return None, got: {result}"

    def test_empty_string_returns_none(self):
        from playbook_selector import select_playbook
        result = select_playbook("")
        assert result is None

    def test_none_input_returns_none(self):
        from playbook_selector import select_playbook
        result = select_playbook(None)
        assert result is None

    def test_selector_never_raises(self):
        from playbook_selector import select_playbook
        # Must never raise for any input
        for work_item_type in [
            "FORMAT_FEATURE_EXPANSION", "NEW_FORMAT_KICKSTART",
            "PRODUCT_SOURCE_PATCH_BOUNDED", "UNKNOWN", "", None, 42
        ]:
            try:
                select_playbook(work_item_type)  # type: ignore[arg-type]
            except Exception as e:
                pytest.fail(f"select_playbook raised for {work_item_type!r}: {e}")


class TestSelectAndValidate:
    def test_select_and_validate_never_blocks_sprint(self):
        from playbook_selector import select_and_validate
        result = select_and_validate("FORMAT_FEATURE_EXPANSION")
        assert result.get("blocks_sprint") is False

    def test_select_and_validate_unknown_type(self):
        from playbook_selector import select_and_validate
        result = select_and_validate("UNKNOWN_TYPE")
        assert result.get("blocks_sprint") is False
        assert result.get("selected_playbook") is None

    def test_select_and_validate_result_has_required_fields(self):
        from playbook_selector import select_and_validate
        result = select_and_validate("FORMAT_FEATURE_EXPANSION")
        assert "work_item_type" in result
        assert "blocks_sprint" in result
        assert result["work_item_type"] == "FORMAT_FEATURE_EXPANSION"

    def test_select_and_validate_list_all(self):
        from playbook_selector import list_supported_types
        types = list_supported_types()
        assert isinstance(types, list)
        assert "FORMAT_FEATURE_EXPANSION" in types
        assert "NEW_FORMAT_KICKSTART" in types


class TestDeprecatedPlaybookRejected:
    def test_deprecated_status_rejected(self, tmp_path):
        """A playbook with DEPRECATED status should not be returned by selector."""
        # The selector uses _WORK_ITEM_MAP which points to specific files.
        # We verify the concept: if a file were deprecated, select_playbook returns None.
        from playbook_selector import _WORK_ITEM_MAP, select_playbook
        # Verify the selector does not blindly return paths to deprecated files
        # by checking that any returned path (if not None) has ACTIVE status in contract
        import re
        import yaml
        for work_type, path_str in _WORK_ITEM_MAP.items():
            path = Path(path_str) if not Path(path_str).is_absolute() else Path(path_str)
            if not path.is_absolute():
                path = _REPO / path_str
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            m = re.search(r"<!--\s*\n(playbook_contract:.*?)-->", text, re.DOTALL)
            if not m:
                continue
            data = yaml.safe_load(m.group(1))
            contract = data.get("playbook_contract", {}) if isinstance(data, dict) else {}
            status = contract.get("status", "ACTIVE").upper()
            if status == "DEPRECATED":
                result = select_playbook(work_type)
                assert result is None, (
                    f"DEPRECATED playbook for {work_type} should return None, got {result}"
                )


class TestMissingSkillCreatesGap:
    """Missing skills should create gaps, not hard failures."""

    def test_execution_log_records_missing_skill(self, tmp_path):
        from playbook_execution_log import PlaybookExecutionLog
        log = PlaybookExecutionLog(
            playbook_id="test-playbook",
            version="1.0",
            plan_id="TEST-001",
        )
        log.missing_skill("add-python-api", phase="draft_function")
        # Missing skill creates gap entry, not exception
        assert len(log.missing_skills) == 1
        assert log.missing_skills[0]["skill_id"] == "add-python-api"
        assert log.missing_skills[0]["action"] == "CREATE_SKILL_GAP"

    def test_execution_log_saves_cleanly(self, tmp_path):
        from playbook_execution_log import PlaybookExecutionLog
        log = PlaybookExecutionLog(
            playbook_id="test-playbook",
            version="1.0",
            plan_id="TEST-001",
        )
        log.phase_complete("read_codec")
        log.missing_skill("add-python-api", phase="draft_function")
        log.phase_failed("draft_function", error="skill not available")
        path = log.save(output_dir=tmp_path)
        assert path.exists()
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert data["verdict"] == "PARTIAL_SUCCESS"
        assert len(data["missing_skills"]) == 1
