#!/usr/bin/env python3
"""AI Pipeline Runner — standardized entry point for AI system verification.

Usage:
    python tools/ai/run_ai_checks.py --fixture
    python tools/ai/run_ai_checks.py --live-probe
    python tools/ai/run_ai_checks.py --no-live
    python tools/ai/run_ai_checks.py --fixture --format fods --report-dir reports/r31
    python tools/ai/run_ai_checks.py --sprint-id R31

Modes:
    --fixture      Run deterministic fixture pipeline (default, always safe)
    --live-probe   Run live gateway probes if env is configured
    --no-live      Explicitly skip all live probes

Options:
    --format       Target format ID for format-specific checks (default: fods)
    --report-dir   Directory for reports (default: reports/current)
    --sprint-id    Sprint identifier for telemetry
    --clean-env    Clear AI env vars before running (isolation test)
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


def main():
    parser = argparse.ArgumentParser(description="AI Pipeline Runner")
    parser.add_argument("--fixture", action="store_true", help="Run fixture pipeline")
    parser.add_argument("--live-probe", action="store_true", help="Run live probes")
    parser.add_argument("--no-live", action="store_true", help="Skip live probes")
    parser.add_argument("--format", default="fods", help="Target format ID")
    parser.add_argument("--report-dir", default=None, help="Report output directory")
    parser.add_argument("--sprint-id", default="UNKNOWN", help="Sprint identifier")
    parser.add_argument("--clean-env", action="store_true", help="Clear AI env vars")
    args = parser.parse_args()

    if args.clean_env:
        for var in ["GPT_OSS_ENDPOINT", "GPT_OSS_API_KEY", "PROFESSIONALIZE_API_KEY",
                     "PROFESSIONALIZE_BASE_URL", "AGENT_METRICS_ENDPOINT",
                     "AGENT_METRICS_TOKEN", "AGENT_METRICS_API_KEY"]:
            os.environ.pop(var, None)

    # Default: run fixture if no mode specified
    if not args.fixture and not args.live_probe:
        args.fixture = True

    all_results = {"timestamp": datetime.now(timezone.utc).isoformat(), "sprint_id": args.sprint_id}

    # Always run isolation checks
    all_results["isolation"] = run_isolation_checks()

    if args.fixture:
        all_results["fixture"] = run_fixture_checks(args.format, args.sprint_id)

    if args.live_probe and not args.no_live:
        all_results["live_probe"] = run_live_probe(args.sprint_id)
    elif args.live_probe and args.no_live:
        all_results["live_probe"] = {"status": "skipped_by_no_live_flag", "passed": True}

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
        print(f"\nReport written to: {report_path}", file=sys.stderr)

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
