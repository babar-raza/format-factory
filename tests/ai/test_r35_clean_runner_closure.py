"""R35 tests -- Clean runner closure, fail-closed pipeline, validator integration.

Sprint: FORMAT-FACTORY-R35-AI-CLEAN-RUNNER-CLOSURE-VALIDATOR-FAIL-CLOSED-TELEMETRY-HARDENING-MEGA-TRAIN-001
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.ai.pipeline.e2e_pilot import (
    PilotConfig,
    run_pilot,
    stage_1_load_chunks,
    stage_3_synthesis,
)
from tools.ai.telemetry.artifacts import (
    _deep_redact,
    _strip_content_keys,
    write_telemetry_artifact,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


# --- Lane B: Evidence validation schema fix ---

class TestEvidenceValidationSchemaFix:
    def test_reads_required_repo_files_not_artifacts(self):
        from tools.ai.run_ai_checks import run_evidence_validation
        contract = REPO_ROOT / "tools/evidence/contracts/r32-ai-clean-closure-status-repair-and-pipeline-deepening.yaml"
        if contract.exists():
            result = run_evidence_validation(str(contract))
            assert result["required_count"] > 0, "required_repo_files must be read"

    def test_r33_contract_also_works(self):
        from tools.ai.run_ai_checks import run_evidence_validation
        contract = REPO_ROOT / "tools/evidence/contracts/r33-ai-runner-executable-pipeline-real-synthesis-truth-reconciliation.yaml"
        if contract.exists():
            result = run_evidence_validation(str(contract))
            assert result["required_count"] > 0

    def test_uses_canonical_contract_loader(self):
        from tools.ai.run_ai_checks import run_evidence_validation
        import inspect
        source = inspect.getsource(run_evidence_validation)
        assert "load_contract" in source, "Must use canonical loader"

    def test_missing_contract_still_fails(self):
        from tools.ai.run_ai_checks import run_evidence_validation
        result = run_evidence_validation("/nonexistent/contract.yaml")
        assert result["passed"] is False


# --- Lane C: Real evidence validator integration ---

class TestCanonicalValidatorIntegration:
    def test_load_contract_imported_from_validator(self):
        from tools.evidence.validate_evidence_bundle import load_contract
        assert callable(load_contract)

    def test_load_contract_reads_required_repo_files(self):
        from tools.evidence.validate_evidence_bundle import load_contract
        contract = REPO_ROOT / "tools/evidence/contracts/r32-ai-clean-closure-status-repair-and-pipeline-deepening.yaml"
        if contract.exists():
            data = load_contract(str(contract))
            assert len(data.get("required_repo_files", [])) > 0


# --- Lane D: R33 contract cleanup ---

class TestR33ContractCleanup:
    def test_no_emergency_blocker(self):
        import yaml
        contract = REPO_ROOT / "tools/evidence/contracts/r33-ai-runner-executable-pipeline-real-synthesis-truth-reconciliation.yaml"
        data = yaml.safe_load(contract.read_text(encoding="utf-8"))
        assert data.get("emergency_blocker_bundle") is not True
        assert "emergency_blocker_reason" not in data

    def test_metadata_floor_is_30(self):
        import yaml
        contract = REPO_ROOT / "tools/evidence/contracts/r33-ai-runner-executable-pipeline-real-synthesis-truth-reconciliation.yaml"
        data = yaml.safe_load(contract.read_text(encoding="utf-8"))
        assert data.get("min_metadata_count") == 30


# --- Lane F: Fail-closed live pipeline ---

class TestFailClosedLivePipeline:
    def test_blocked_live_does_not_fallback_to_fixture(self):
        config = PilotConfig(format_id="fods", fixture_mode=True, live_gateway=True)
        chunks, _ = stage_1_load_chunks(config)
        with patch.dict("os.environ", {}, clear=True):
            _, meta = stage_3_synthesis(chunks, config)
        assert meta.get("live_failed") is True
        assert meta.get("synthesis_mode") == "blocked_live_synthesis"
        assert "fallback" not in meta

    def test_blocked_live_pilot_reports_failure(self):
        config = PilotConfig(format_id="fods", fixture_mode=True, live_gateway=True)
        with patch.dict("os.environ", {}, clear=True):
            result = run_pilot(config)
        synth = result.stage_results.get("3_synthesis", {})
        assert synth.get("synthesis_mode") == "blocked_live_synthesis"

    def test_fixture_mode_still_works(self):
        result = run_pilot(PilotConfig(format_id="fods", fixture_mode=True))
        assert result.all_stages_passed
        assert result.stage_results["3_synthesis"]["synthesis_mode"] == "fixture_synthesis"


# --- Lane G: Live contradiction policy ---

class TestLiveContradictionRequired:
    def test_live_pipeline_uses_required_policy(self):
        import inspect
        from tools.ai.run_ai_checks import run_live_pipeline_checks
        source = inspect.getsource(run_live_pipeline_checks)
        assert 'contradiction_policy="required"' in source

    def test_required_policy_always_checks(self):
        from tools.ai.pipeline.e2e_pilot import _resolve_contradiction_check
        assert _resolve_contradiction_check(PilotConfig(contradiction_policy="required")) is True
        assert _resolve_contradiction_check(
            PilotConfig(contradiction_policy="required", verified_facts_path=None)
        ) is True


# --- Lane H: Citation visibility ---

class TestCitationVisibility:
    def test_fixture_pipeline_has_citation_details(self):
        result = run_pilot(PilotConfig(
            format_id="fods", fixture_mode=True,
            use_lexical_retrieval=True,
            retrieval_query="fods format specification requirements parsing",
        ))
        synth = result.stage_results["3_synthesis"]
        assert "citation_verified" in synth
        assert "citations_all_valid" in synth
        assert "citations_checked" in synth
        assert synth["citations_checked"] > 0

    def test_citation_failure_count_present(self):
        result = run_pilot(PilotConfig(format_id="fods", fixture_mode=True))
        synth = result.stage_results["3_synthesis"]
        assert "citations_failed" in synth


# --- Lane I: Telemetry minimization ---

class TestTelemetryMinimization:
    def test_content_keys_stripped(self):
        data = {"model": "test", "prompt": "secret prompt", "tokens": 100}
        stripped = _strip_content_keys(data)
        assert stripped["prompt"] == "[stripped]"
        assert stripped["model"] == "test"
        assert stripped["tokens"] == 100

    def test_nested_content_stripped(self):
        data = {"outer": {"response": "secret response", "status": "ok"}}
        stripped = _strip_content_keys(data)
        assert stripped["outer"]["response"] == "[stripped]"
        assert stripped["outer"]["status"] == "ok"

    def test_minimized_artifact_has_metadata(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_telemetry_artifact(
                {"model": "test", "prompt": "secret"}, Path(td)
            )
            data = json.loads(path.read_text())
            assert data["_artifact_metadata"]["content_minimized"] is True
            assert data["prompt"] == "[stripped]"

    def test_non_minimized_preserves_content(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_telemetry_artifact(
                {"model": "test", "prompt": "kept"}, Path(td), minimize=False
            )
            data = json.loads(path.read_text())
            assert data["_artifact_metadata"]["content_minimized"] is False
            assert data["prompt"] != "[stripped]"

    def test_list_content_stripped(self):
        data = {"items": [{"content": "secret", "id": 1}]}
        stripped = _strip_content_keys(data)
        assert stripped["items"][0]["content"] == "[stripped]"
        assert stripped["items"][0]["id"] == 1


# --- Lane J: Runner JSON schema and exit codes ---

class TestRunnerContract:
    def test_schema_flag_outputs_json(self):
        proc = subprocess.run(
            [sys.executable, "tools/ai/run_ai_checks.py", "--schema"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert proc.returncode == 0
        schema = json.loads(proc.stdout)
        assert schema["type"] == "object"
        assert "overall_passed" in schema["properties"]

    def test_schema_has_required_fields(self):
        proc = subprocess.run(
            [sys.executable, "tools/ai/run_ai_checks.py", "--schema"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        schema = json.loads(proc.stdout)
        assert set(schema["required"]) == {"timestamp", "sprint_id", "overall_passed"}

    def test_exit_code_0_on_pass(self):
        proc = subprocess.run(
            [sys.executable, "tools/ai/run_ai_checks.py", "--fixture", "--json",
             "--sprint-id", "R35-TEST"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=60,
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert data["overall_passed"] is True

    def test_exit_codes_documented(self):
        proc = subprocess.run(
            [sys.executable, "tools/ai/run_ai_checks.py", "--help"],
            capture_output=True, text=True, cwd=str(REPO_ROOT),
        )
        assert "--schema" in proc.stdout


# --- Lane K: Verification matrix ---

class TestVerificationMatrixV3:
    def test_matrix_has_r35_entries(self):
        matrix = (REPO_ROOT / "docs/ai/ai-system-verification-matrix.md").read_text(encoding="utf-8")
        assert "R35" in matrix

    def test_matrix_has_fail_closed_component(self):
        matrix = (REPO_ROOT / "docs/ai/ai-system-verification-matrix.md").read_text(encoding="utf-8")
        assert "Fail-Closed Live Pipeline" in matrix

    def test_matrix_has_telemetry_minimization(self):
        matrix = (REPO_ROOT / "docs/ai/ai-system-verification-matrix.md").read_text(encoding="utf-8")
        assert "Telemetry Minimization" in matrix

    def test_matrix_has_citation_visibility(self):
        matrix = (REPO_ROOT / "docs/ai/ai-system-verification-matrix.md").read_text(encoding="utf-8")
        assert "Citation Visibility" in matrix


# --- Full pipeline integration ---

class TestR35FullPipelineIntegration:
    def test_all_no_live_passes(self):
        proc = subprocess.run(
            [sys.executable, "tools/ai/run_ai_checks.py", "--all", "--no-live",
             "--json", "--sprint-id", "R35-INTEGRATION"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120,
        )
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert data["overall_passed"] is True

    def test_fixture_pipeline_has_citation_visibility(self):
        result = run_pilot(PilotConfig(
            format_id="fods", fixture_mode=True,
            use_lexical_retrieval=True,
            retrieval_query="fods format specification requirements parsing",
            sprint_id="R35-TEST",
        ))
        assert result.all_stages_passed
        synth = result.stage_results["3_synthesis"]
        assert synth["citation_verified"] is True
        assert synth["citations_all_valid"] is True

    def test_evidence_validation_finds_real_files(self):
        from tools.ai.run_ai_checks import run_evidence_validation
        contract = REPO_ROOT / "tools/evidence/contracts/r32-ai-clean-closure-status-repair-and-pipeline-deepening.yaml"
        if contract.exists():
            result = run_evidence_validation(str(contract))
            assert result["required_count"] > 0
            assert result["passed"] or len(result.get("missing", [])) > 0
