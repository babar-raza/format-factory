"""Tests for ComposeVerifyLoop — refdev-style compose/verify groundwork.

Taskcard: LFI-3-D01
Sprint: FF-LIBFORGE-BROAD-IMPLEMENTATION-001
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT))

from tools.supervisor.compose_verify_loop import (
    ComposeVerifyLoop,
    ComposeResult,
    VerifyResult,
    LLMBackendStub,
)

VALID_PYTHON = '"""A valid generated module."""\ndef hello(): return "world"\n'
INVALID_PYTHON = "def broken(: this is not python\n"


@pytest.fixture
def loop():
    return ComposeVerifyLoop(repo_root=str(_REPO_ROOT))


# ---------------------------------------------------------------------------
# LLMBackendStub
# ---------------------------------------------------------------------------


class TestLLMBackendStub:
    def test_is_disabled_by_default(self):
        stub = LLMBackendStub()
        assert stub.enabled is False

    def test_compose_raises_not_implemented(self):
        stub = LLMBackendStub()
        with pytest.raises(NotImplementedError):
            stub.compose("template", {})


# ---------------------------------------------------------------------------
# ComposeResult
# ---------------------------------------------------------------------------


class TestComposeResult:
    def test_to_dict(self):
        r = ComposeResult(ok=True, attempts=1, max_attempts=3)
        d = r.to_dict()
        assert d["ok"] is True
        assert d["attempts"] == 1

    def test_to_json_serializable(self):
        r = ComposeResult(ok=False, attempts=2, max_attempts=3, rollback_required=True)
        parsed = json.loads(r.to_json())
        assert parsed["rollback_required"] is True

    def test_verify_history_serializes(self):
        v = VerifyResult(
            attempt=1, ok=True, test_command="py_compile",
            test_exit_code=0, stdout="", stderr=""
        )
        r = ComposeResult(ok=True, attempts=1, max_attempts=3, verify_history=[v])
        d = r.to_dict()
        assert len(d["verify_history"]) == 1
        json.dumps(d)  # must not raise


# ---------------------------------------------------------------------------
# Successful synthetic compose/verify
# ---------------------------------------------------------------------------


class TestSuccessfulCompose:
    def test_valid_python_passes(self, loop, tmp_path):
        result = loop.run(
            feature_name="hello_feature",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.ok is True
        assert result.attempts == 1
        assert result.test_exit_code == 0

    def test_generated_file_created(self, loop, tmp_path):
        result = loop.run(
            feature_name="test_feat",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.generated_file is not None
        assert Path(result.generated_file).exists()

    def test_changed_files_listed(self, loop, tmp_path):
        result = loop.run(
            feature_name="files_test",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert len(result.changed_files) >= 1

    def test_no_rollback_on_success(self, loop, tmp_path):
        result = loop.run(
            feature_name="no_rollback",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.rollback_required is False


# ---------------------------------------------------------------------------
# Failing verification
# ---------------------------------------------------------------------------


class TestFailingVerification:
    def test_invalid_syntax_fails(self, loop, tmp_path):
        result = loop.run(
            feature_name="bad_syntax",
            template_content=INVALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.ok is False
        assert result.test_exit_code != 0

    def test_rollback_marked_on_failure(self, loop, tmp_path):
        result = loop.run(
            feature_name="rollback_test",
            template_content=INVALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.rollback_required is True

    def test_verify_history_captures_failure(self, loop, tmp_path):
        result = loop.run(
            feature_name="history_fail",
            template_content=INVALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert len(result.verify_history) >= 1
        assert result.verify_history[-1].ok is False

    def test_stderr_captured_for_feedback(self, loop, tmp_path):
        result = loop.run(
            feature_name="stderr_test",
            template_content=INVALID_PYTHON,
            workspace=str(tmp_path),
        )
        # stderr should have some content about the syntax error
        combined = (result.stderr or "") + "".join(v.stderr for v in result.verify_history)
        assert len(combined) > 0


# ---------------------------------------------------------------------------
# Max attempts
# ---------------------------------------------------------------------------


class TestMaxAttempts:
    def test_max_attempts_respected_without_llm(self, loop, tmp_path):
        """Without LLM, loop exits after 1 attempt on failure."""
        result = loop.run(
            feature_name="max_test",
            template_content=INVALID_PYTHON,
            max_attempts=3,
            workspace=str(tmp_path),
        )
        # Without LLM backend, stops after first failure (no retry)
        assert result.attempts == 1
        assert result.max_attempts == 3

    def test_successful_verify_stops_early(self, loop, tmp_path):
        result = loop.run(
            feature_name="early_stop",
            template_content=VALID_PYTHON,
            max_attempts=5,
            workspace=str(tmp_path),
        )
        assert result.ok is True
        assert result.attempts == 1  # Stopped at first success


# ---------------------------------------------------------------------------
# No product source mutation
# ---------------------------------------------------------------------------


class TestNoProductSourceMutation:
    def test_workspace_stays_in_temp(self, loop):
        """Generated files go to temp dir, not product source."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = loop.run(
                feature_name="isolation_test",
                template_content=VALID_PYTHON,
                workspace=tmpdir,
            )
            gen_file = Path(result.generated_file)
            # Generated file must be under tmpdir, not under src/
            assert "src" not in str(gen_file) or tmpdir in str(gen_file)
            assert gen_file.is_relative_to(Path(tmpdir))

    def test_result_is_json_serializable(self, loop, tmp_path):
        result = loop.run(
            feature_name="serial_test",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        json.dumps(result.to_dict())  # must not raise

    def test_log_file_created(self, loop, tmp_path):
        result = loop.run(
            feature_name="log_test",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.log_path is not None
        assert Path(result.log_path).exists()


# ---------------------------------------------------------------------------
# FreezeGate integration hook (Lane D)
# ---------------------------------------------------------------------------


class TestFreezeGateHook:
    def test_freeze_gate_hook_disabled_by_default(self, loop, tmp_path):
        """Without freeze_gate_format_id, freeze_gate_result is None."""
        result = loop.run(
            feature_name="gate_disabled",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.freeze_gate_result is None

    def test_freeze_gate_hook_runs_when_enabled(self, tmp_path):
        """With freeze_gate_format_id='zst', freeze gate runs after successful verify."""
        loop_with_gate = ComposeVerifyLoop(
            freeze_gate_format_id="zst",
            freeze_gate_kinds=["binding_roundtrip"],
        )
        result = loop_with_gate.run(
            feature_name="gate_enabled",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.ok is True
        assert result.freeze_gate_result is not None
        assert result.freeze_gate_result["format_id"] == "zst"
        assert result.freeze_gate_result["overall_status"] == "PASS"

    def test_freeze_gate_hook_skipped_on_verify_failure(self, tmp_path):
        """Freeze gate hook is NOT run when verify fails (no false PASS)."""
        loop_with_gate = ComposeVerifyLoop(
            freeze_gate_format_id="zst",
        )
        result = loop_with_gate.run(
            feature_name="gate_skip_on_fail",
            template_content=INVALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.ok is False
        assert result.freeze_gate_result is None

    def test_freeze_gate_result_is_json_serializable(self, tmp_path):
        """Full ComposeResult with freeze gate result serializes to JSON."""
        loop_with_gate = ComposeVerifyLoop(
            freeze_gate_format_id="zst",
            freeze_gate_kinds=["contract_validation"],
        )
        result = loop_with_gate.run(
            feature_name="gate_serial",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        json.dumps(result.to_dict())  # must not raise


# ---------------------------------------------------------------------------
# Queue-shaped dry-run + G3 scan — v2 (LFI-6-C)
# ---------------------------------------------------------------------------

FORBIDDEN_PYTHON = "import os\nos.system('rm -rf /')\n"


class TestQueueShapeTracking:
    """v2: queue_item_id, taskcard_id, target_format are tracked in result."""

    def test_queue_item_id_in_result(self, tmp_path):
        result = ComposeVerifyLoop().run(
            feature_name="q_track",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
            queue_item_id="QI-001",
        )
        assert result.queue_item_id == "QI-001"

    def test_taskcard_id_in_result(self, tmp_path):
        result = ComposeVerifyLoop().run(
            feature_name="tc_track",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
            taskcard_id="LFI-6-C",
        )
        assert result.taskcard_id == "LFI-6-C"

    def test_target_format_in_result(self, tmp_path):
        result = ComposeVerifyLoop().run(
            feature_name="fmt_track",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
            target_format="ndjson",
        )
        assert result.target_format == "ndjson"

    def test_all_queue_shape_fields_serializable(self, tmp_path):
        result = ComposeVerifyLoop().run(
            feature_name="full_queue",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
            queue_item_id="QI-002",
            taskcard_id="LFI-6-C",
            target_format="csv",
        )
        d = result.to_dict()
        assert d["queue_item_id"] == "QI-002"
        assert d["taskcard_id"] == "LFI-6-C"
        assert d["target_format"] == "csv"
        json.dumps(d)  # must not raise


class TestDryRun:
    """v2: dry_run=True runs G3 scan but skips file writing and verification."""

    def test_dry_run_returns_ok_for_safe_code(self):
        result = ComposeVerifyLoop().run(
            feature_name="dry_safe",
            template_content=VALID_PYTHON,
            dry_run=True,
        )
        assert result.ok is True
        assert result.dry_run is True
        assert result.attempts == 0

    def test_dry_run_no_files_written(self, tmp_path):
        result = ComposeVerifyLoop().run(
            feature_name="dry_nowrite",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
            dry_run=True,
        )
        assert result.generated_file is None
        assert result.changed_files == []

    def test_dry_run_g3_scan_runs(self):
        result = ComposeVerifyLoop().run(
            feature_name="dry_g3",
            template_content=VALID_PYTHON,
            dry_run=True,
        )
        assert result.g3_scan_result is not None
        assert result.g3_safe is True

    def test_dry_run_blocks_forbidden_code(self):
        result = ComposeVerifyLoop().run(
            feature_name="dry_forbidden",
            template_content=FORBIDDEN_PYTHON,
            dry_run=True,
        )
        assert result.ok is False
        assert result.g3_safe is False
        # G3 gate blocked before dry_run path; no files written in either case
        assert result.changed_files == []
        assert result.generated_file is None


class TestG3ScanGate:
    """v2: G3 scan gate fires before file writing."""

    def test_safe_code_passes_g3(self, tmp_path):
        result = ComposeVerifyLoop().run(
            feature_name="g3_safe",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.g3_safe is True
        assert result.g3_scan_result is not None

    def test_forbidden_code_blocked_by_g3(self):
        result = ComposeVerifyLoop().run(
            feature_name="g3_block",
            template_content=FORBIDDEN_PYTHON,
        )
        assert result.ok is False
        assert result.g3_safe is False
        assert "G3 scan FAIL" in (result.error or "")

    def test_forbidden_code_no_files_written(self, tmp_path):
        result = ComposeVerifyLoop().run(
            feature_name="g3_nowrite",
            template_content=FORBIDDEN_PYTHON,
            workspace=str(tmp_path),
        )
        assert result.generated_file is None
        assert result.changed_files == []
        assert result.rollback_required is False  # nothing was written

    def test_g3_scan_result_in_full_dict(self, tmp_path):
        result = ComposeVerifyLoop().run(
            feature_name="g3_dict",
            template_content=VALID_PYTHON,
            workspace=str(tmp_path),
        )
        d = result.to_dict()
        assert "g3_scan_result" in d
        assert "g3_safe" in d
        json.dumps(d)  # must not raise
