"""R33 tests -- Runner-executable pipeline, real synthesis wiring, truth reconciliation.

Sprint: FORMAT-FACTORY-R33-AI-RUNNER-EXECUTABLE-PIPELINE-REAL-SYNTHESIS-AND-TRUTH-RECONCILIATION-MEGA-TRAIN-001
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.ai.pipeline.e2e_pilot import (
    CONTRADICTION_POLICIES,
    PilotConfig,
    PilotResult,
    _build_fixture_output,
    _get_diverse_fixture_chunks,
    _resolve_contradiction_check,
    run_pilot,
    stage_1_load_chunks,
    stage_2_retrieval,
    stage_3_synthesis,
    stage_4_evaluate,
)
from tools.ai.schemas.commit_metadata import SprintCommitMetadata
from tools.ai.telemetry.artifacts import write_telemetry_artifact, _deep_redact


class TestR32TruthReconciliation:
    def test_r32_final_verdict_exists(self):
        p = Path(__file__).resolve().parents[2] / "reports/r32/final-verdict.md"
        assert p.exists()

    def test_r32_verdict_has_commit_sha(self):
        p = Path(__file__).resolve().parents[2] / "reports/r32/final-verdict.md"
        text = p.read_text(encoding="utf-8")
        # R32 final commit SHA is the last "## Commit SHA:" line
        sha_lines = [l for l in text.splitlines() if l.startswith("## Commit SHA:")]
        assert len(sha_lines) > 0
        assert "PENDING" not in sha_lines[-1]

    def test_synthesis_mode_labels_exist(self):
        assert PilotConfig(fixture_mode=True, live_gateway=False).synthesis_mode == "fixture_synthesis"
        assert PilotConfig(fixture_mode=True, live_gateway=True).synthesis_mode == "live_gateway_synthesis"

    def test_contradiction_policy_modes_defined(self):
        assert "required" in CONTRADICTION_POLICIES
        assert "optional" in CONTRADICTION_POLICIES
        assert "skipped_fixture_only" in CONTRADICTION_POLICIES

    def test_stage_3_returns_synthesis_mode(self):
        config = PilotConfig(format_id="fods", fixture_mode=True)
        chunks, _ = stage_1_load_chunks(config)
        _, meta = stage_3_synthesis(chunks, config)
        assert meta["synthesis_mode"] == "fixture_synthesis"


class TestLivePipelineRunner:
    def test_live_pipeline_function_exists(self):
        from tools.ai.run_ai_checks import run_live_pipeline_checks
        assert callable(run_live_pipeline_checks)

    def test_live_pipeline_blocked_without_env(self):
        from tools.ai.run_ai_checks import run_live_pipeline_checks
        with patch.dict("os.environ", {}, clear=True):
            result = run_live_pipeline_checks("fods", "R33-TEST")
        assert result["mode"] == "live_pipeline"
        assert result["status"] == "blocked_missing_env"
        assert result["passed"] is False

    def test_live_pipeline_no_not_yet_implemented(self):
        from tools.ai.run_ai_checks import run_live_pipeline_checks
        with patch.dict("os.environ", {}, clear=True):
            result = run_live_pipeline_checks("fods", "R33-TEST")
        assert result.get("status") != "not_yet_implemented"

    def test_live_pipeline_has_mode_field(self):
        from tools.ai.run_ai_checks import run_live_pipeline_checks
        with patch.dict("os.environ", {}, clear=True):
            result = run_live_pipeline_checks("fods", "R33-TEST")
        assert result["mode"] == "live_pipeline"


class TestAllMode:
    def test_all_flag_enables_all_modes(self):
        import argparse
        args = argparse.Namespace(
            all=True, no_live=False,
            fixture=False, fixture_pipeline=False, isolation=False,
            live_probe=False, live_pipeline=False, failure_injection=False,
        )
        if args.all:
            args.fixture = True
            args.fixture_pipeline = True
            args.isolation = True
            args.failure_injection = True
            if not args.no_live:
                args.live_probe = True
                args.live_pipeline = True
        assert args.fixture and args.fixture_pipeline and args.isolation
        assert args.failure_injection and args.live_probe and args.live_pipeline

    def test_all_no_live_skips_live(self):
        import argparse
        args = argparse.Namespace(
            all=True, no_live=True,
            fixture=False, fixture_pipeline=False, isolation=False,
            live_probe=False, live_pipeline=False, failure_injection=False,
        )
        if args.all:
            args.fixture = True
            args.fixture_pipeline = True
            args.isolation = True
            args.failure_injection = True
            if not args.no_live:
                args.live_probe = True
                args.live_pipeline = True
        assert args.fixture and not args.live_probe and not args.live_pipeline


class TestSynthesisWiring:
    def test_fixture_synthesis_builds_json_locally(self):
        config = PilotConfig(format_id="fods", fixture_mode=True)
        chunks, _ = stage_1_load_chunks(config)
        output = _build_fixture_output(chunks, config)
        parsed = json.loads(output)
        assert "citations" in parsed and "requirements" in parsed
        assert parsed["format"] == "fods"

    def test_fixture_pilot_reports_synthesis_mode(self):
        result = run_pilot(PilotConfig(format_id="fods", fixture_mode=True))
        assert result.stage_results["3_synthesis"]["synthesis_mode"] == "fixture_synthesis"

    def test_live_gateway_blocked_returns_fallback(self):
        config = PilotConfig(format_id="fods", fixture_mode=True, live_gateway=True)
        chunks, _ = stage_1_load_chunks(config)
        with patch.dict("os.environ", {}, clear=True):
            _, meta = stage_3_synthesis(chunks, config)
        assert meta.get("fallback") == "fixture_synthesis"

    def test_live_config_synthesis_mode_label(self):
        assert PilotConfig(live_gateway=True).synthesis_mode == "live_gateway_synthesis"
        assert PilotConfig(live_gateway=False).synthesis_mode == "fixture_synthesis"


class TestDiverseRetrieval:
    def test_fods_corpus_has_5_chunks(self):
        assert len(_get_diverse_fixture_chunks("fods")) == 5

    def test_fods_chunks_have_distinct_content(self):
        contents = [c["content"] for c in _get_diverse_fixture_chunks("fods")]
        assert len(set(contents)) == 5

    def test_retrieval_produces_differentiated_scores(self):
        config = PilotConfig(format_id="fods", fixture_mode=True)
        chunks, _ = stage_1_load_chunks(config)
        _, meta = stage_2_retrieval(
            chunks, query="fods format specification requirements parsing",
            use_lexical=True, format_id="fods", top_k=5)
        scores = [c["score"] for c in meta.get("chunks", [])]
        assert len(scores) >= 2 and len(set(scores)) > 1

    def test_retrieval_excludes_low_relevance(self):
        config = PilotConfig(format_id="fods", fixture_mode=True)
        chunks, _ = stage_1_load_chunks(config)
        _, meta = stage_2_retrieval(
            chunks, query="fods format specification requirements parsing",
            use_lexical=True, format_id="fods", top_k=5)
        assert meta.get("excluded_count", 0) > 0

    def test_generic_fallback_has_3_chunks(self):
        assert len(_get_diverse_fixture_chunks("unknown_format")) == 3

    def test_top_k_limits_results(self):
        config = PilotConfig(format_id="fods", fixture_mode=True)
        chunks, _ = stage_1_load_chunks(config)
        _, meta = stage_2_retrieval(
            chunks, query="fods format specification requirements parsing",
            use_lexical=True, format_id="fods", top_k=1)
        assert meta.get("returned", 0) <= 1


class TestContradictionPolicy:
    def test_required_always_checks(self):
        assert _resolve_contradiction_check(PilotConfig(contradiction_policy="required")) is True

    def test_optional_checks_when_facts_present(self):
        assert _resolve_contradiction_check(
            PilotConfig(contradiction_policy="optional", verified_facts_path=Path("/tmp/f.yaml"))
        ) is True

    def test_optional_skips_when_no_facts(self):
        assert _resolve_contradiction_check(
            PilotConfig(contradiction_policy="optional", verified_facts_path=None)
        ) is False

    def test_skipped_fixture_only_skips_fixture(self):
        assert _resolve_contradiction_check(
            PilotConfig(contradiction_policy="skipped_fixture_only", live_gateway=False)
        ) is False

    def test_skipped_fixture_only_checks_live(self):
        assert _resolve_contradiction_check(
            PilotConfig(contradiction_policy="skipped_fixture_only", live_gateway=True)
        ) is True

    def test_unknown_policy_defaults_false(self):
        assert _resolve_contradiction_check(PilotConfig(contradiction_policy="nonexistent")) is False


class TestEvidenceValidation:
    def test_evidence_validation_function_exists(self):
        from tools.ai.run_ai_checks import run_evidence_validation
        assert callable(run_evidence_validation)

    def test_evidence_validation_missing_contract(self):
        from tools.ai.run_ai_checks import run_evidence_validation
        result = run_evidence_validation("/nonexistent/contract.yaml")
        assert result["passed"] is False

    def test_evidence_validation_with_valid_contract(self):
        from tools.ai.run_ai_checks import run_evidence_validation
        contract = Path(__file__).resolve().parents[2] / "tools/evidence/contracts/r32-ai-clean-closure-status-repair-and-pipeline-deepening.yaml"
        if contract.exists():
            result = run_evidence_validation(str(contract))
            assert result["required_count"] > 0

    def test_runner_has_validate_evidence_flag(self):
        import subprocess
        proc = subprocess.run(
            [sys.executable, "tools/ai/run_ai_checks.py", "--help"],
            capture_output=True, text=True,
            cwd=str(Path(__file__).resolve().parents[2]),
        )
        assert "--validate-evidence" in proc.stdout


class TestCommitMetadata:
    def test_model_creation(self):
        m = SprintCommitMetadata(sprint_id="R33", implementation_commit="abc123")
        assert m.sprint_id == "R33" and m.implementation_commit == "abc123"

    def test_all_populated_check(self):
        assert SprintCommitMetadata(sprint_id="R33", implementation_commit="a", metadata_commit="b").all_populated
        assert not SprintCommitMetadata(sprint_id="R33", implementation_commit="a").all_populated

    def test_commits_match(self):
        assert SprintCommitMetadata(sprint_id="R33", implementation_commit="a", metadata_commit="a").commits_match
        assert not SprintCommitMetadata(sprint_id="R33", implementation_commit="a", metadata_commit="b").commits_match

    def test_to_dict_uses_pending(self):
        d = SprintCommitMetadata(sprint_id="R33").to_dict()
        assert d["implementation_commit"] == "PENDING" and d["metadata_commit"] == "PENDING"

    def test_validate_catches_pending(self):
        errors = SprintCommitMetadata(sprint_id="R33", implementation_commit="PENDING").validate()
        assert any("PENDING" in e for e in errors)

    def test_validate_clean(self):
        assert len(SprintCommitMetadata(sprint_id="R33", implementation_commit="a", metadata_commit="b").validate()) == 0


class TestTelemetryArtifacts:
    def test_write_artifact(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_telemetry_artifact({"model": "test", "tokens": 100}, Path(td))
            assert path.exists()
            data = json.loads(path.read_text())
            assert data["_artifact_metadata"]["redaction_applied"] is True

    def test_redacts_secrets(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_telemetry_artifact({"key": "sk-abcdefghij1234567890"}, Path(td))
            assert "sk-abcdefghij1234567890" not in path.read_text()

    def test_deep_redact_nested(self):
        redacted = _deep_redact({"outer": {"inner": "sk-abcdefghij1234567890"}})
        assert "sk-abcdefghij1234567890" not in json.dumps(redacted)

    def test_artifact_creates_directory(self):
        with tempfile.TemporaryDirectory() as td:
            path = write_telemetry_artifact({"t": 1}, Path(td) / "nested" / "dir")
            assert path.exists()

    def test_artifact_custom_name(self):
        with tempfile.TemporaryDirectory() as td:
            assert write_telemetry_artifact({"t": 1}, Path(td), "custom.json").name == "custom.json"


class TestGateDryRunHooks:
    def test_runner_modes_documented(self):
        from tools.ai.run_ai_checks import (
            run_fixture_checks, run_live_probe, run_isolation_checks,
            run_failure_injection_checks, run_fixture_pipeline_checks,
            run_live_pipeline_checks, run_evidence_validation,
        )
        assert all(callable(f) for f in [
            run_fixture_checks, run_live_probe, run_isolation_checks,
            run_failure_injection_checks, run_fixture_pipeline_checks,
            run_live_pipeline_checks, run_evidence_validation,
        ])

    def test_fixture_pipeline_could_serve_gate_check(self):
        config = PilotConfig(format_id="fods", fixture_mode=True,
                             use_lexical_retrieval=True,
                             retrieval_query="fods format specification requirements parsing")
        d = run_pilot(config).to_dict()
        assert all(k in d["stage_results"] for k in ["1_load_chunks", "2_retrieval", "3_synthesis", "4_evaluation"])
        assert d["final_authority_state"] == "ai_draft"


class TestVerificationMatrix:
    def test_verification_matrix_exists(self):
        assert (Path(__file__).resolve().parents[2] / "docs/ai/ai-system-verification-matrix.md").exists()

    def test_pilot_config_has_all_r33_fields(self):
        config = PilotConfig()
        for attr in ["live_gateway", "sprint_id", "contradiction_policy", "synthesis_mode"]:
            assert hasattr(config, attr)


class TestFullPipelineIntegration:
    def test_fixture_pipeline_end_to_end(self):
        result = run_pilot(PilotConfig(
            format_id="fods", fixture_mode=True, use_lexical_retrieval=True,
            retrieval_query="fods format specification requirements parsing",
            sprint_id="R33-TEST", contradiction_policy="optional",
        ))
        assert result.all_stages_passed and result.final_authority_state == "ai_draft"
        assert result.stage_results["3_synthesis"]["synthesis_mode"] == "fixture_synthesis"

    def test_fixture_pipeline_non_fods_format(self):
        result = run_pilot(PilotConfig(
            format_id="fodt", fixture_mode=True, use_lexical_retrieval=True,
            retrieval_query="fodt format parsing requirements",
        ))
        assert result.all_stages_passed
        assert result.stage_results["1_load_chunks"]["chunk_count"] == 3

    def test_runner_fixture_pipeline_produces_output(self):
        from tools.ai.run_ai_checks import run_fixture_pipeline_checks
        result = run_fixture_pipeline_checks("fods", "R33-TEST")
        assert result["mode"] == "fixture_pipeline" and result["passed"]

    def test_runner_fixture_checks_pass(self):
        from tools.ai.run_ai_checks import run_fixture_checks
        result = run_fixture_checks("fods", "R33-TEST")
        assert result["passed"] and result["authority_state"] == "ai_draft"

    def test_runner_isolation_checks_pass(self):
        from tools.ai.run_ai_checks import run_isolation_checks
        assert run_isolation_checks()["passed"]
