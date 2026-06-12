"""
test_libforge_isolated_job_runner.py — Tests for libforge_isolated_job_runner.py

Sprint: FF-LIBFORGE-REFOCUS-INTEGRATION-001
Lane E: Autonomy / Isolation
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

from tools.supervisor.libforge_isolated_job_runner import (
    JobRequest,
    JobResult,
    JobStatus,
    run_job,
    result_to_dict,
    result_to_json,
)


# ---------------------------------------------------------------------------
# TestValidDryRunJob
# ---------------------------------------------------------------------------

class TestValidDryRunJob:
    def test_basic_dry_run_returns_job_result(self):
        req = JobRequest(job_id="test-001", format_id="zst")
        result = run_job(req)
        assert isinstance(result, JobResult)

    def test_dry_run_status_is_dry_run(self):
        req = JobRequest(job_id="test-002", format_id="zst", dry_run=True)
        result = run_job(req)
        assert result.status == JobStatus.DRY_RUN

    def test_dry_run_changed_files_empty(self):
        req = JobRequest(job_id="test-003", format_id="zst", dry_run=True)
        result = run_job(req)
        assert result.changed_files == []

    def test_dry_run_rollback_not_required(self):
        req = JobRequest(job_id="test-004", format_id="zst", dry_run=True)
        result = run_job(req)
        assert result.rollback_required is False

    def test_job_id_preserved_in_result(self):
        req = JobRequest(job_id="my-job-999", format_id="abw")
        result = run_job(req)
        assert result.job_id == "my-job-999"

    def test_format_id_preserved_in_result(self):
        req = JobRequest(job_id="test-006", format_id="abw")
        result = run_job(req)
        assert result.format_id == "abw"

    def test_workspace_used_is_set(self):
        req = JobRequest(job_id="test-007", format_id="zst")
        result = run_job(req)
        # workspace_used may be empty string after cleanup in dry_run, but should not fail
        assert isinstance(result.workspace_used, str)

    def test_steps_list_populated(self):
        req = JobRequest(job_id="test-008", format_id="zst")
        result = run_job(req)
        assert len(result.steps) >= 2  # validate + workspace_setup at minimum

    def test_no_error_on_clean_dry_run(self):
        req = JobRequest(job_id="test-009", format_id="zst")
        result = run_job(req)
        assert result.error is None


# ---------------------------------------------------------------------------
# TestInvalidRequest
# ---------------------------------------------------------------------------

class TestInvalidRequest:
    def test_empty_job_id_returns_invalid(self):
        req = JobRequest(job_id="", format_id="zst")
        result = run_job(req)
        assert result.status == JobStatus.INVALID

    def test_empty_format_id_returns_invalid(self):
        req = JobRequest(job_id="j1", format_id="")
        result = run_job(req)
        assert result.status == JobStatus.INVALID

    def test_invalid_result_has_error_message(self):
        req = JobRequest(job_id="", format_id="")
        result = run_job(req)
        assert result.error is not None
        assert len(result.error) > 0

    def test_invalid_gate_config_type_fails(self):
        req = JobRequest(job_id="j2", format_id="zst", gate_config="not_a_dict")
        result = run_job(req)
        assert result.status == JobStatus.INVALID

    def test_invalid_result_step_shows_fail(self):
        req = JobRequest(job_id="", format_id="zst")
        result = run_job(req)
        assert any(s.status == "fail" for s in result.steps)


# ---------------------------------------------------------------------------
# TestG3AstScan
# ---------------------------------------------------------------------------

class TestG3AstScan:
    def test_clean_python_passes_g3(self):
        safe_code = "def add(a, b):\n    return a + b\n"
        req = JobRequest(job_id="g3-001", format_id="zst", python_source=safe_code)
        result = run_job(req)
        g3 = result.gate_results.get("g3_ast_scan", {})
        assert g3.get("status") == "pass"

    def test_eval_call_fails_g3(self):
        unsafe_code = "result = eval(user_input)\n"
        req = JobRequest(job_id="g3-002", format_id="zst", python_source=unsafe_code)
        result = run_job(req)
        g3 = result.gate_results.get("g3_ast_scan", {})
        assert g3.get("status") == "fail"

    def test_exec_call_fails_g3(self):
        unsafe_code = "exec('import os')\n"
        req = JobRequest(job_id="g3-003", format_id="zst", python_source=unsafe_code)
        result = run_job(req)
        g3 = result.gate_results.get("g3_ast_scan", {})
        assert g3.get("status") == "fail"

    def test_os_system_fails_g3(self):
        unsafe_code = "import os\nos.system('rm -rf /')\n"
        req = JobRequest(job_id="g3-004", format_id="zst", python_source=unsafe_code)
        result = run_job(req)
        g3 = result.gate_results.get("g3_ast_scan", {})
        assert g3.get("status") == "fail"

    def test_subprocess_run_fails_g3(self):
        unsafe_code = "import subprocess\nsubprocess.run(['ls'])\n"
        req = JobRequest(job_id="g3-005", format_id="zst", python_source=unsafe_code)
        result = run_job(req)
        g3 = result.gate_results.get("g3_ast_scan", {})
        assert g3.get("status") == "fail"

    def test_no_python_source_skips_g3(self):
        req = JobRequest(job_id="g3-006", format_id="zst")
        result = run_job(req)
        g3 = result.gate_results.get("g3_ast_scan", {})
        assert g3.get("status") == "skip"

    def test_g3_violation_details_in_results(self):
        unsafe_code = "eval('x')\nexec('y')\n"
        req = JobRequest(job_id="g3-007", format_id="zst", python_source=unsafe_code)
        result = run_job(req)
        g3 = result.gate_results.get("g3_ast_scan", {})
        details = g3.get("details", {})
        assert "violations" in details
        assert len(details["violations"]) >= 2


# ---------------------------------------------------------------------------
# TestFreezeGateStep
# ---------------------------------------------------------------------------

class TestFreezeGateStep:
    def test_no_gate_config_skips_freeze_gate(self):
        req = JobRequest(job_id="fg-001", format_id="zst")
        result = run_job(req)
        fg = result.gate_results.get("freeze_gate", {})
        assert fg.get("status") == "skip"

    def test_gate_config_dict_triggers_freeze_gate(self):
        """With gate_config, FreezeGateRunner is attempted (may soft-skip if unavailable)."""
        req = JobRequest(
            job_id="fg-002",
            format_id="zst",
            gate_config={"gate_kind": "binding_roundtrip", "format_id": "zst"},
        )
        result = run_job(req)
        fg = result.gate_results.get("freeze_gate", {})
        # Either attempted (pass/fail/dry_run) or soft-skipped (skip) — not absent
        assert fg.get("status") in ("pass", "fail", "dry_run", "skip")

    def test_freeze_gate_result_in_gate_results(self):
        req = JobRequest(job_id="fg-003", format_id="zst")
        result = run_job(req)
        assert "freeze_gate" in result.gate_results


# ---------------------------------------------------------------------------
# TestComposeVerifyStep
# ---------------------------------------------------------------------------

class TestComposeVerifyStep:
    def test_no_compose_verify_skips_step(self):
        req = JobRequest(job_id="cv-001", format_id="zst", use_compose_verify=False)
        result = run_job(req)
        cv = result.gate_results.get("compose_verify", {})
        assert cv.get("status") == "skip"

    def test_compose_verify_requested_attempts_step(self):
        """With use_compose_verify=True, step is attempted (may soft-skip if unavailable)."""
        req = JobRequest(job_id="cv-002", format_id="zst", use_compose_verify=True)
        result = run_job(req)
        cv = result.gate_results.get("compose_verify", {})
        assert cv.get("status") in ("pass", "fail", "dry_run", "skip")

    def test_compose_verify_result_in_gate_results(self):
        req = JobRequest(job_id="cv-003", format_id="zst")
        result = run_job(req)
        assert "compose_verify" in result.gate_results


# ---------------------------------------------------------------------------
# TestSerialization
# ---------------------------------------------------------------------------

class TestSerialization:
    def test_result_to_dict_returns_dict(self):
        req = JobRequest(job_id="ser-001", format_id="zst")
        result = run_job(req)
        d = result_to_dict(result)
        assert isinstance(d, dict)

    def test_result_to_dict_has_required_keys(self):
        req = JobRequest(job_id="ser-002", format_id="abw")
        result = run_job(req)
        d = result_to_dict(result)
        for key in ("job_id", "format_id", "status", "dry_run", "steps", "gate_results", "verification"):
            assert key in d, f"Missing key: {key}"

    def test_result_to_json_is_valid_json(self):
        req = JobRequest(job_id="ser-003", format_id="zst")
        result = run_job(req)
        json_str = result_to_json(result)
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)

    def test_result_to_json_job_id_matches(self):
        req = JobRequest(job_id="ser-004-unique", format_id="dif")
        result = run_job(req)
        parsed = json.loads(result_to_json(result))
        assert parsed["job_id"] == "ser-004-unique"

    def test_verification_summary_in_dict(self):
        req = JobRequest(job_id="ser-005", format_id="zst")
        result = run_job(req)
        d = result_to_dict(result)
        v = d["verification"]
        assert "valid" in v
        assert "total_steps" in v
        assert "pass_count" in v

    def test_serialized_steps_are_list(self):
        req = JobRequest(job_id="ser-006", format_id="zst")
        result = run_job(req)
        d = result_to_dict(result)
        assert isinstance(d["steps"], list)
        for step in d["steps"]:
            assert "step_name" in step
            assert "status" in step


# ---------------------------------------------------------------------------
# TestNoProductSourceMutation
# ---------------------------------------------------------------------------

class TestNoProductSourceMutation:
    def test_dry_run_does_not_write_product_source(self):
        """Verify no files under src/ are modified."""
        src_dir = _REPO / "src"
        # Snapshot mtime of a known product source file
        sample = src_dir / "python" / "zst" / "zst_codec.py"
        if not sample.exists():
            return  # Skip if file missing
        mtime_before = sample.stat().st_mtime

        req = JobRequest(job_id="safe-001", format_id="zst", dry_run=True)
        run_job(req)

        mtime_after = sample.stat().st_mtime
        assert mtime_after == mtime_before, "Product source was unexpectedly mutated"

    def test_changed_files_empty_in_dry_run(self):
        req = JobRequest(job_id="safe-002", format_id="zst", dry_run=True)
        result = run_job(req)
        assert result.changed_files == []

    def test_rollback_not_required_in_dry_run(self):
        req = JobRequest(job_id="safe-003", format_id="zst", dry_run=True)
        result = run_job(req)
        assert result.rollback_required is False
