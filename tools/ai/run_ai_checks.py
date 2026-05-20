#!/usr/bin/env python3
"""AI Pipeline Runner — standardized entry point for AI system verification.

Usage:
    python tools/ai/run_ai_checks.py --fixture
    python tools/ai/run_ai_checks.py --live-probe
    python tools/ai/run_ai_checks.py --no-live
    python tools/ai/run_ai_checks.py --fixture --format fods --report-dir reports/r31
    python tools/ai/run_ai_checks.py --sprint-id R31

Modes:
    --fixture           Run deterministic fixture pipeline (default, always safe)
    --live-probe        Run live gateway probes if env is configured
    --live-pipeline     Run live pipeline with real gateway synthesis
    --no-live           Explicitly skip all live probes
    --all               Run all check modes (combine with --no-live to skip live)
    --validate-evidence Validate evidence contract YAML path

Exit codes:
    0  All requested checks passed
    1  One or more checks failed
    2  Live probes blocked (env not configured) but --fail-on-blocked-live not set

Options:
    --format       Target format ID for format-specific checks (default: fods)
    --report-dir   Directory for reports (default: reports/current)
    --sprint-id    Sprint identifier for telemetry
    --clean-env    Clear AI env vars before running (isolation test)
    --json         Output JSON only (suppress stderr)
    --schema       Print runner output JSON schema and exit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))


def run_fixture_checks(format_id: str, sprint_id: str) -> dict:
    """Run deterministic fixture pipeline checks."""
    from tools.ai.synthesis.runner import run_synthesis
    from tools.ai.synthesis.evaluator import evaluate_synthesis
    from tools.ai.synthesis.citation_verifier import verify_all_citations
    from tools.ai.synthesis.contradiction_detector import check_output_contradictions
    from tools.ai.requirements.generator import (
        generate_requirements_from_synthesis,
        validate_requirement,
    )
    from tools.ai.schemas.models import AITaskContract, AIRole

    results = {"mode": "fixture", "format_id": format_id, "sprint_id": sprint_id}

    source_snippets = {
        f"{format_id}-spec-section": f"{format_id.upper()} is a well-defined format.",
    }
    facts = [
        {"id": "F1", "assertion": f"{format_id} is valid", "negation": f"{format_id} is invalid"},
    ]

    raw_output = json.dumps({
        "summary": f"Fixture extraction for {format_id}.",
        "citations": [
            {"source": f"{format_id}-spec-section", "text": f"{format_id.upper()} is a well-defined format"},
        ],
        "requirements": [
            {"id": f"REQ-{format_id.upper()}-FIX-001", "text": f"Parse {format_id}", "source_chunk_hash": "fixture_hash"},
        ],
    })

    contract = AITaskContract(
        task_id=f"{sprint_id}-FIXTURE-001",
        task_type="structured_extraction",
        role=AIRole.structured_extraction,
        require_citation=True,
    )

    synth = run_synthesis(contract, raw_output, source_snippets=source_snippets)
    results["synthesis_valid"] = synth.is_valid
    results["citation_verified"] = synth.citation_verified

    cit_report = verify_all_citations(synth.citations, source_texts=source_snippets)
    results["citations_all_valid"] = cit_report.all_valid

    contra = check_output_contradictions(synth.structured_output, facts=facts)
    results["contradiction_status"] = contra.status
    synth.contradiction_check_status = contra.status

    ev = evaluate_synthesis(synth)
    results["evaluator_passed"] = ev.passed
    results["evaluator_score"] = ev.score

    reqs = generate_requirements_from_synthesis(synth.structured_output, format_id)
    results["requirements_count"] = len(reqs)
    results["requirements_valid"] = all(not validate_requirement(r) for r in reqs)
    results["authority_state"] = synth.authority_state.value

    results["passed"] = all([
        results["synthesis_valid"],
        results["citation_verified"],
        results["citations_all_valid"],
        results["evaluator_passed"],
        results["authority_state"] == "ai_draft",
    ])

    return results


def run_live_probe(sprint_id: str) -> dict:
    """Run live gateway probes if env is configured."""
    from tools.ai.control_plane.config import load_ai_config
    from tools.ai.control_plane.model_discovery import discover_models
    from tools.ai.control_plane.capability_probe import probe_model

    results = {"mode": "live_probe", "sprint_id": sprint_id}
    cfg = load_ai_config()

    if not cfg.is_configured:
        results["status"] = "blocked_no_env"
        results["passed"] = False
        return results

    models = discover_models(cfg)
    results["models_discovered"] = len(models)
    results["model_ids"] = [m.model_id for m in models]
    results["endpoint_identity"] = cfg.endpoint_identity

    if not models:
        results["status"] = "blocked_no_models"
        results["passed"] = False
        return results

    # Capability probe on first chat model
    chat_models = [m for m in models if m.supports_chat and not m.supports_embedding]
    probe_model_id = chat_models[0].model_id if chat_models else models[0].model_id

    success, text, record = probe_model(cfg, probe_model_id, sprint_id=sprint_id)
    results["probe_model"] = probe_model_id
    results["probe_success"] = success
    results["probe_tokens"] = record.total_tokens
    results["probe_status"] = record.status.value

    # Verify no secrets
    dump = json.dumps(record.model_dump(), default=str)
    results["secrets_in_telemetry"] = any(
        pat in dump for pat in ["sk-", "Bearer eyJ"]
    )
    results["passed"] = success and not results["secrets_in_telemetry"]
    results["status"] = "success" if results["passed"] else "probe_failed"

    return results


def run_isolation_checks() -> dict:
    """Run control-plane isolation checks."""
    from tools.ai.control_plane.config import AIConfig
    from tools.ai.control_plane.model_discovery import discover_models
    from tools.ai.control_plane.capability_probe import probe_model
    from tools.ai.schemas.models import CallStatus

    results = {"mode": "isolation"}
    checks = []

    # Unconfigured returns empty
    cfg = AIConfig(endpoint="", api_key_present=False)
    models = discover_models(cfg)
    checks.append({"name": "unconfigured_empty", "passed": models == []})

    # Probe blocked
    success, _, record = probe_model(cfg, "test")
    checks.append({"name": "probe_blocked", "passed": record.status == CallStatus.blocked_missing_env})

    results["checks"] = checks
    results["passed"] = all(c["passed"] for c in checks)
    return results


def run_failure_injection_checks() -> dict:
    """Run failure injection tests (import and execute)."""
    results = {"mode": "failure_injection"}
    try:
        import subprocess
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/ai", "-q", "-k", "failure_injection or FailureInjection"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=120,
        )
        results["exit_code"] = proc.returncode
        results["passed"] = proc.returncode == 0
        results["output_tail"] = proc.stdout[-300:] if proc.stdout else ""
    except Exception as e:
        results["passed"] = False
        results["error"] = str(e)
    return results


def run_fixture_pipeline_checks(format_id: str, sprint_id: str) -> dict:
    """Run fixture pipeline with lexical retrieval."""
    from tools.ai.pipeline.e2e_pilot import PilotConfig, run_pilot

    config = PilotConfig(
        format_id=format_id,
        fixture_mode=True,
        use_lexical_retrieval=True,
        retrieval_query=f"{format_id} format specification requirements parsing",
        sprint_id=sprint_id,
    )
    pilot_result = run_pilot(config)
    result = pilot_result.to_dict()
    result["mode"] = "fixture_pipeline"
    result["sprint_id"] = sprint_id
    result["passed"] = pilot_result.all_stages_passed
    return result


def run_live_pipeline_checks(format_id: str, sprint_id: str) -> dict:
    """Run live pipeline: gateway synthesis with citation verification."""
    from tools.ai.pipeline.e2e_pilot import PilotConfig, run_pilot
    from tools.ai.control_plane.config import load_ai_config

    cfg = load_ai_config()
    if not cfg.is_configured:
        return {
            "mode": "live_pipeline",
            "status": "blocked_missing_env",
            "passed": False,
            "sprint_id": sprint_id,
        }

    config = PilotConfig(
        format_id=format_id,
        fixture_mode=True,
        live_gateway=True,
        use_lexical_retrieval=True,
        retrieval_query=f"{format_id} format specification requirements parsing",
        sprint_id=sprint_id,
        contradiction_policy="required",
    )
    pilot_result = run_pilot(config)
    result = pilot_result.to_dict()
    result["mode"] = "live_pipeline"
    result["sprint_id"] = sprint_id
    result["passed"] = pilot_result.all_stages_passed
    result["status"] = "success" if result["passed"] else "pipeline_failed"

    dump = json.dumps(result, default=str)
    if any(pat in dump for pat in ["sk-", "Bearer eyJ"]):
        result["secrets_in_output"] = True
        result["passed"] = False
    else:
        result["secrets_in_output"] = False

    return result


def run_evidence_validation(contract_path: str) -> dict:
    """Validate evidence contract artifacts exist and are non-empty.

    Uses the canonical contract loader from validate_evidence_bundle.py
    to ensure field-name consistency (required_repo_files).
    """
    from tools.evidence.validate_evidence_bundle import load_contract

    results = {"mode": "evidence_validation", "contract_path": contract_path}

    contract_file = Path(contract_path)
    if not contract_file.exists():
        results["passed"] = False
        results["error"] = f"Contract file not found: {contract_path}"
        return results

    contract = load_contract(str(contract_file))

    required = contract.get("required_repo_files", [])
    missing = []
    empty = []
    for artifact in required:
        ap = REPO_ROOT / artifact
        if not ap.exists():
            missing.append(artifact)
        elif ap.stat().st_size == 0:
            empty.append(artifact)

    results["required_count"] = len(required)
    results["missing"] = missing
    results["empty"] = empty
    results["missing_count"] = len(missing)
    results["passed"] = len(missing) == 0 and len(empty) == 0
    return results


def main():
    parser = argparse.ArgumentParser(description="AI Pipeline Runner")
    parser.add_argument("--fixture", action="store_true", help="Run fixture checks")
    parser.add_argument("--fixture-pipeline", action="store_true", help="Run fixture pipeline with lexical retrieval")
    parser.add_argument("--isolation", action="store_true", help="Run isolation checks only")
    parser.add_argument("--live-probe", action="store_true", help="Run live probes")
    parser.add_argument("--live-pipeline", action="store_true", help="Run live pipeline with citations")
    parser.add_argument("--failure-injection", action="store_true", help="Run failure injection tests")
    parser.add_argument("--all", action="store_true", help="Run all check modes")
    parser.add_argument("--no-live", action="store_true", help="Skip live probes")
    parser.add_argument("--json", action="store_true", help="Output JSON only (no stderr)")
    parser.add_argument("--fail-on-blocked-live", action="store_true", help="Exit 1 if live is blocked")
    parser.add_argument("--format", default="fods", help="Target format ID")
    parser.add_argument("--report-dir", default=None, help="Report output directory")
    parser.add_argument("--sprint-id", default="UNKNOWN", help="Sprint identifier")
    parser.add_argument("--clean-env", action="store_true", help="Clear AI env vars")
    parser.add_argument("--validate-evidence", default=None, help="Validate evidence contract YAML path")
    parser.add_argument("--schema", action="store_true", help="Print output JSON schema and exit")
    args = parser.parse_args()

    if args.schema:
        schema = {
            "type": "object",
            "properties": {
                "timestamp": {"type": "string", "format": "date-time"},
                "sprint_id": {"type": "string"},
                "overall_passed": {"type": "boolean"},
                "isolation": {"type": "object", "properties": {"mode": {}, "passed": {"type": "boolean"}}},
                "fixture": {"type": "object", "properties": {"mode": {}, "passed": {"type": "boolean"}}},
                "fixture_pipeline": {"type": "object", "properties": {"mode": {}, "passed": {"type": "boolean"}}},
                "failure_injection": {"type": "object", "properties": {"mode": {}, "passed": {"type": "boolean"}}},
                "live_probe": {"type": "object", "properties": {"mode": {}, "passed": {"type": "boolean"}}},
                "live_pipeline": {"type": "object", "properties": {"mode": {}, "passed": {"type": "boolean"}}},
                "evidence_validation": {"type": "object", "properties": {"mode": {}, "passed": {"type": "boolean"}}},
            },
            "required": ["timestamp", "sprint_id", "overall_passed"],
        }
        print(json.dumps(schema, indent=2))
        return 0

    if args.clean_env:
        for var in ["GPT_OSS_ENDPOINT", "GPT_OSS_API_KEY", "PROFESSIONALIZE_API_KEY",
                     "PROFESSIONALIZE_BASE_URL", "AGENT_METRICS_ENDPOINT",
                     "AGENT_METRICS_TOKEN", "AGENT_METRICS_API_KEY"]:
            os.environ.pop(var, None)

    # --all enables everything
    if args.all:
        args.fixture = True
        args.fixture_pipeline = True
        args.isolation = True
        args.failure_injection = True
        if not args.no_live:
            args.live_probe = True
            args.live_pipeline = True

    # Default: run fixture + isolation if no mode specified
    if not any([args.fixture, args.fixture_pipeline, args.isolation,
                args.live_probe, args.live_pipeline, args.failure_injection]):
        args.fixture = True
        args.isolation = True

    all_results = {"timestamp": datetime.now(timezone.utc).isoformat(), "sprint_id": args.sprint_id}

    if args.isolation or args.fixture or args.fixture_pipeline:
        all_results["isolation"] = run_isolation_checks()

    if args.fixture:
        all_results["fixture"] = run_fixture_checks(args.format, args.sprint_id)

    if args.fixture_pipeline:
        all_results["fixture_pipeline"] = run_fixture_pipeline_checks(args.format, args.sprint_id)

    if args.failure_injection:
        all_results["failure_injection"] = run_failure_injection_checks()

    live_blocked = False
    if args.live_probe and not args.no_live:
        all_results["live_probe"] = run_live_probe(args.sprint_id)
        if all_results["live_probe"].get("status") == "blocked_no_env":
            live_blocked = True
    elif args.live_probe and args.no_live:
        all_results["live_probe"] = {"status": "skipped_by_no_live_flag", "passed": True}

    if args.live_pipeline and not args.no_live:
        all_results["live_pipeline"] = run_live_pipeline_checks(args.format, args.sprint_id)
        if all_results["live_pipeline"].get("status") == "blocked_missing_env":
            live_blocked = True
    elif args.live_pipeline and args.no_live:
        all_results["live_pipeline"] = {"status": "skipped_by_no_live_flag", "passed": True}

    if args.validate_evidence:
        all_results["evidence_validation"] = run_evidence_validation(args.validate_evidence)

    # Overall pass
    passed = all(
        r.get("passed", False) for k, r in all_results.items()
        if isinstance(r, dict) and "passed" in r
    )
    all_results["overall_passed"] = passed

    # Output
    output = json.dumps(all_results, indent=2, default=str)
    print(output)

    # Write report if requested
    if args.report_dir:
        report_dir = Path(args.report_dir)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / "ai-pipeline-runner-output.json"
        report_path.write_text(output, encoding="utf-8")
        if not args.json:
            print(f"\nReport written to: {report_path}", file=sys.stderr)

    # Exit codes: 0=pass, 1=failure, 2=live blocked but allowed
    if not passed:
        return 1
    if live_blocked and args.fail_on_blocked_live:
        return 1
    if live_blocked and not args.fail_on_blocked_live:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
