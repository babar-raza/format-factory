"""Tests for bounded_repair_engine.py.

Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-3-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from tools.supervisor.bounded_repair_engine import (
    BoundedRepairEngine,
    FailureClass,
    RepairResult,
)


# ---------------------------------------------------------------------------
# classify_failure
# ---------------------------------------------------------------------------

class TestClassifyFailure:
    def setup_method(self):
        self.engine = BoundedRepairEngine()

    def test_import_error(self):
        text = "ImportError: No module named 'abw'"
        assert self.engine.classify_failure(text) == FailureClass.IMPORT_ERROR

    def test_no_module_named(self):
        text = "ModuleNotFoundError: No module named 'ndjson.ndjson_codec'"
        assert self.engine.classify_failure(text) == FailureClass.IMPORT_ERROR

    def test_syntax_error(self):
        text = "SyntaxError: invalid syntax (abw_codec.py, line 42)"
        assert self.engine.classify_failure(text) == FailureClass.SYNTAX_ERROR

    def test_attribute_error(self):
        text = "AttributeError: 'NoneType' object has no attribute 'paragraphs'"
        assert self.engine.classify_failure(text) == FailureClass.ATTRIBUTE_ERROR

    def test_assertion_error(self):
        text = "AssertionError: assert 3 == 4\nFAILED tests/test_foo.py::test_bar"
        assert self.engine.classify_failure(text) == FailureClass.ASSERTION_ERROR

    def test_name_error(self):
        text = "NameError: name 'get_shapes' is not defined"
        assert self.engine.classify_failure(text) == FailureClass.NAME_ERROR

    def test_type_error(self):
        text = "TypeError: unsupported operand type(s) for +: 'int' and 'str'"
        assert self.engine.classify_failure(text) == FailureClass.TYPE_ERROR

    def test_timeout(self):
        text = "FAILED: test timed out after 30s"
        assert self.engine.classify_failure(text) == FailureClass.TIMEOUT

    def test_empty_string(self):
        assert self.engine.classify_failure("") == FailureClass.UNKNOWN

    def test_none_handled(self):
        assert self.engine.classify_failure(None) == FailureClass.UNKNOWN

    def test_syntax_takes_priority_over_import(self):
        # SyntaxError should match before ImportError
        text = "SyntaxError: invalid syntax\nImportError: ..."
        assert self.engine.classify_failure(text) == FailureClass.SYNTAX_ERROR

    def test_collection_error(self):
        text = "ERROR collecting tests/foo.py\nImportError while importing"
        assert self.engine.classify_failure(text) == FailureClass.COLLECTION_ERROR


# ---------------------------------------------------------------------------
# apply_repair — max attempts
# ---------------------------------------------------------------------------

class TestMaxAttempts:
    def test_max_attempts_enforced(self, tmp_path):
        engine = BoundedRepairEngine(max_attempts=2)
        # Simulate 2 attempts first
        fake_src = tmp_path / "src.py"
        fake_src.write_text("x = 1\n", encoding="utf-8")
        key = "src.py"
        engine._attempt_counts[key] = 2  # Already at max
        result = engine.apply_repair(key, FailureClass.IMPORT_ERROR, "error", repo_root=tmp_path)
        assert not result.success
        assert result.action_taken == "MAX_ATTEMPTS_REACHED"

    def test_attempts_remaining(self):
        engine = BoundedRepairEngine(max_attempts=3)
        assert engine.attempts_remaining("foo.py") == 3
        engine._attempt_counts["foo.py"] = 1
        assert engine.attempts_remaining("foo.py") == 2

    def test_reset_attempts(self):
        engine = BoundedRepairEngine(max_attempts=3)
        engine._attempt_counts["foo.py"] = 3
        engine.reset_attempts("foo.py")
        assert engine.attempts_remaining("foo.py") == 3


# ---------------------------------------------------------------------------
# apply_repair — SYNTAX_ERROR rollback
# ---------------------------------------------------------------------------

class TestSyntaxErrorRepair:
    def test_syntax_error_triggers_action(self, tmp_path):
        engine = BoundedRepairEngine()
        fake_src = tmp_path / "src.py"
        fake_src.write_text("def foo(:\n", encoding="utf-8")
        result = engine.apply_repair(
            "src.py", FailureClass.SYNTAX_ERROR, "SyntaxError: ...",
            repo_root=tmp_path
        )
        assert result.failure_class == FailureClass.SYNTAX_ERROR
        assert "ROLLBACK" in result.action_taken or "SYNTAX" in result.action_taken


# ---------------------------------------------------------------------------
# apply_repair — ATTRIBUTE_ERROR
# ---------------------------------------------------------------------------

class TestAttributeErrorRepair:
    def test_adds_stub(self, tmp_path):
        engine = BoundedRepairEngine()
        src = tmp_path / "src.py"
        src.write_text("class Foo:\n    pass\n", encoding="utf-8")
        error = "AttributeError: 'Foo' object has no attribute 'bar_method'"
        result = engine.apply_repair(
            "src.py", FailureClass.ATTRIBUTE_ERROR, error,
            repo_root=tmp_path
        )
        assert result.success
        assert "bar_method" in src.read_text(encoding="utf-8")

    def test_missing_attribute_name(self, tmp_path):
        engine = BoundedRepairEngine()
        src = tmp_path / "src.py"
        src.write_text("x = 1\n", encoding="utf-8")
        result = engine.apply_repair(
            "src.py", FailureClass.ATTRIBUTE_ERROR, "AttributeError: ...",
            repo_root=tmp_path
        )
        assert not result.success

    def test_file_not_found(self, tmp_path):
        engine = BoundedRepairEngine()
        result = engine.apply_repair(
            "nonexistent.py", FailureClass.ATTRIBUTE_ERROR, "...",
            repo_root=tmp_path
        )
        assert not result.success
        assert "NOT_FOUND" in result.action_taken


# ---------------------------------------------------------------------------
# apply_repair — ASSERTION_ERROR (no-op)
# ---------------------------------------------------------------------------

class TestAssertionErrorRepair:
    def test_no_repair_applied(self, tmp_path):
        engine = BoundedRepairEngine()
        src = tmp_path / "src.py"
        src.write_text("x = 1\n", encoding="utf-8")
        original = src.read_text(encoding="utf-8")
        result = engine.apply_repair(
            "src.py", FailureClass.ASSERTION_ERROR, "AssertionError",
            repo_root=tmp_path
        )
        assert not result.success
        assert "NOT_AUTONOMOUS" in result.action_taken
        assert src.read_text(encoding="utf-8") == original  # File unchanged


# ---------------------------------------------------------------------------
# apply_repair — NAME_ERROR
# ---------------------------------------------------------------------------

class TestNameErrorRepair:
    def test_adds_stub_name(self, tmp_path):
        engine = BoundedRepairEngine()
        src = tmp_path / "src.py"
        src.write_text("x = 1\n", encoding="utf-8")
        error = "NameError: name 'my_function' is not defined"
        result = engine.apply_repair(
            "src.py", FailureClass.NAME_ERROR, error,
            repo_root=tmp_path
        )
        assert result.success
        content = src.read_text(encoding="utf-8")
        assert "my_function" in content


# ---------------------------------------------------------------------------
# apply_repair — TIMEOUT
# ---------------------------------------------------------------------------

class TestTimeoutRepair:
    def test_no_repair_for_timeout(self, tmp_path):
        engine = BoundedRepairEngine()
        src = tmp_path / "src.py"
        src.write_text("x = 1\n", encoding="utf-8")
        result = engine.apply_repair(
            "src.py", FailureClass.TIMEOUT, "timed out",
            repo_root=tmp_path
        )
        assert not result.success
        assert "TIMEOUT" in result.action_taken


# ---------------------------------------------------------------------------
# RepairResult
# ---------------------------------------------------------------------------

class TestRepairResult:
    def test_repr(self):
        r = RepairResult(True, FailureClass.IMPORT_ERROR, "FIXED", "detail")
        assert "RepairResult" in repr(r)
        assert "IMPORT_ERROR" in repr(r)

    def test_fields(self):
        r = RepairResult(False, FailureClass.UNKNOWN, "NONE", "no repair")
        assert r.success is False
        assert r.failure_class == FailureClass.UNKNOWN
        assert r.action_taken == "NONE"
        assert r.detail == "no repair"
