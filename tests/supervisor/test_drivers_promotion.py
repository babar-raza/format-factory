"""Tests for tools/supervisor/drivers_promotion.py.

Verifies the format-test promotion lifecycle:
- scan_incomplete_markers() detects all incomplete marker types
- validate_maintained_gate() blocks false completion
- create_promotion_task() produces correct tasks from rendered scaffolds
- write_promotion_task() writes valid YAML output
- get_promotion_status() returns correct state

TC-DRV-007: Pattern-to-format-test promotion lifecycle.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from tools.supervisor.drivers_promotion import (
    scan_incomplete_markers,
    validate_maintained_gate,
    create_promotion_task,
    write_promotion_task,
    get_promotion_status,
    GeneratedTestPromotionTask,
    PROMOTION_STATES,
)


# ---------------------------------------------------------------------------
# TestScanIncompleteMarkers
# ---------------------------------------------------------------------------

class TestScanIncompleteMarkers:
    def test_detects_fixture_required(self):
        code = "# FIXTURE_REQUIRED: replace b\"\" with real csv bytes\nresult = load(b\"\")"
        markers = scan_incomplete_markers(code)
        assert any("FIXTURE_REQUIRED" in m for m in markers), f"Expected FIXTURE_REQUIRED in {markers}"

    def test_detects_expected_value_required(self):
        code = "# EXPECTED_VALUE_REQUIRED: assert meaningful behavior"
        markers = scan_incomplete_markers(code)
        assert any("EXPECTED_VALUE_REQUIRED" in m for m in markers)

    def test_detects_oracle_required(self):
        code = "# ORACLE_REQUIRED: verify spec-derived expected value"
        markers = scan_incomplete_markers(code)
        assert any("ORACLE_REQUIRED" in m for m in markers)

    def test_detects_test_scaffold_incomplete(self):
        code = "source_bytes = b\"\"  # TEST_SCAFFOLD_INCOMPLETE"
        markers = scan_incomplete_markers(code)
        assert any("TEST_SCAFFOLD_INCOMPLETE" in m for m in markers)

    def test_detects_format_adaptation_required(self):
        code = "# FORMAT_ADAPTATION_REQUIRED"
        markers = scan_incomplete_markers(code)
        assert any("FORMAT_ADAPTATION_REQUIRED" in m for m in markers)

    def test_detects_scaffold_status_header(self):
        code = "# SCAFFOLD_STATUS: FORMAT_ADAPTATION_REQUIRED"
        markers = scan_incomplete_markers(code)
        assert len(markers) > 0

    def test_clean_code_returns_empty(self):
        code = "def test_something():\n    assert result == 42\n"
        markers = scan_incomplete_markers(code)
        assert markers == []

    def test_multiple_markers_all_returned(self):
        code = (
            "# FIXTURE_REQUIRED: provide bytes\n"
            "# EXPECTED_VALUE_REQUIRED: assert value\n"
            "# ORACLE_REQUIRED: spec check\n"
        )
        markers = scan_incomplete_markers(code)
        assert len(markers) >= 3


# ---------------------------------------------------------------------------
# TestValidateMaintainedGate
# ---------------------------------------------------------------------------

class TestValidateMaintainedGate:
    def test_fails_with_fixture_required(self):
        code = "# FIXTURE_REQUIRED: provide bytes"
        assert validate_maintained_gate(code) is False

    def test_fails_with_expected_value_required(self):
        code = "# EXPECTED_VALUE_REQUIRED: assert something"
        assert validate_maintained_gate(code) is False

    def test_fails_with_scaffold_status_header(self):
        code = "# SCAFFOLD_STATUS: FORMAT_ADAPTATION_REQUIRED"
        assert validate_maintained_gate(code) is False

    def test_passes_with_clean_code(self):
        code = (
            "def test_csv_cell_value():\n"
            "    data = b'col1,col2\\n1,2\\n'\n"
            "    result = parse_csv(data)\n"
            "    assert result.get_cell(0, 0) == '1'\n"
        )
        assert validate_maintained_gate(code) is True

    def test_empty_string_passes(self):
        # Empty string has no markers
        assert validate_maintained_gate("") is True


# ---------------------------------------------------------------------------
# TestCreatePromotionTask
# ---------------------------------------------------------------------------

class TestCreatePromotionTask:
    def _scaffold_code(self) -> str:
        return (
            "# SCAFFOLD_STATUS: FORMAT_ADAPTATION_REQUIRED\n"
            "# FIXTURE_REQUIRED: replace b'' with real csv bytes\n"
            "# EXPECTED_VALUE_REQUIRED: assert exact value\n"
        )

    def test_creates_task_from_scaffold(self):
        task = create_promotion_task(
            rendered_code=self._scaffold_code(),
            format_id="csv",
            pattern_id="A",
            template_id="getter_test",
            renderer_id="render_getter_test",
            generated_path="tests/python/csv/test_csv_getter_scaffold.py",
            target_path="tests/python/csv/test_csv_getter.py",
        )
        assert isinstance(task, GeneratedTestPromotionTask)
        assert task.format_id == "csv"
        assert task.pattern_id == "A"
        assert task.language == "python"

    def test_task_id_is_unique(self):
        code = self._scaffold_code()
        t1 = create_promotion_task(code, "csv", "A", "getter_test", "render_getter_test", "gen.py", "tgt.py")
        t2 = create_promotion_task(code, "csv", "A", "getter_test", "render_getter_test", "gen.py", "tgt.py")
        assert t1.task_id != t2.task_id

    def test_status_is_format_adaptation_required_when_markers_present(self):
        task = create_promotion_task(
            rendered_code=self._scaffold_code(),
            format_id="csv",
            pattern_id="A",
            template_id="getter_test",
            renderer_id="render_getter_test",
            generated_path="gen.py",
            target_path="tgt.py",
        )
        assert task.status == "FORMAT_ADAPTATION_REQUIRED"

    def test_status_is_scaffold_generated_when_no_markers(self):
        clean_code = "def test_something():\n    assert result == 42\n"
        task = create_promotion_task(
            rendered_code=clean_code,
            format_id="csv",
            pattern_id="A",
            template_id="getter_test",
            renderer_id="render_getter_test",
            generated_path="gen.py",
            target_path="tgt.py",
        )
        assert task.status == "SCAFFOLD_GENERATED"

    def test_incomplete_markers_captured(self):
        task = create_promotion_task(
            rendered_code=self._scaffold_code(),
            format_id="csv",
            pattern_id="A",
            template_id="getter_test",
            renderer_id="render_getter_test",
            generated_path="gen.py",
            target_path="tgt.py",
        )
        assert len(task.incomplete_markers) > 0

    def test_scaffold_cannot_be_maintained(self):
        task = create_promotion_task(
            rendered_code=self._scaffold_code(),
            format_id="csv",
            pattern_id="A",
            template_id="getter_test",
            renderer_id="render_getter_test",
            generated_path="gen.py",
            target_path="tgt.py",
        )
        # A task with FORMAT_ADAPTATION_REQUIRED is not MAINTAINED
        assert task.status != "MAINTAINED"
        assert not validate_maintained_gate(self._scaffold_code())


# ---------------------------------------------------------------------------
# TestWritePromotionTask
# ---------------------------------------------------------------------------

class TestWritePromotionTask:
    def test_writes_yaml_file(self, tmp_path):
        task = create_promotion_task(
            rendered_code="# FIXTURE_REQUIRED: provide bytes",
            format_id="csv",
            pattern_id="A",
            template_id="getter_test",
            renderer_id="render_getter_test",
            generated_path="gen.py",
            target_path="tgt.py",
        )
        out_path = write_promotion_task(task, tmp_path)
        assert out_path.exists()
        assert out_path.suffix == ".yaml"

    def test_written_file_contains_task_id(self, tmp_path):
        task = create_promotion_task(
            rendered_code="# FIXTURE_REQUIRED: provide bytes",
            format_id="csv",
            pattern_id="A",
            template_id="getter_test",
            renderer_id="render_getter_test",
            generated_path="gen.py",
            target_path="tgt.py",
        )
        out_path = write_promotion_task(task, tmp_path)
        content = out_path.read_text(encoding="utf-8")
        assert task.task_id in content

    def test_written_file_named_after_task_id(self, tmp_path):
        task = create_promotion_task(
            rendered_code="# FIXTURE_REQUIRED: provide bytes",
            format_id="csv",
            pattern_id="A",
            template_id="getter_test",
            renderer_id="render_getter_test",
            generated_path="gen.py",
            target_path="tgt.py",
        )
        out_path = write_promotion_task(task, tmp_path)
        assert out_path.stem == task.task_id


# ---------------------------------------------------------------------------
# TestGetPromotionStatus
# ---------------------------------------------------------------------------

class TestGetPromotionStatus:
    def test_returns_task_status(self):
        task = create_promotion_task(
            rendered_code="# FIXTURE_REQUIRED: provide bytes",
            format_id="csv",
            pattern_id="A",
            template_id="getter_test",
            renderer_id="render_getter_test",
            generated_path="gen.py",
            target_path="tgt.py",
        )
        assert get_promotion_status(task) == task.status

    def test_all_states_are_valid_enum_values(self):
        for state in PROMOTION_STATES:
            assert isinstance(state, str)
            assert len(state) > 0
