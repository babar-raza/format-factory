"""AI Implementation Designer — generates design docs for product gaps.

Produces per-gap: design.md, test-strategy.md, dogfood-strategy.md, risk-review.md.
Role: structured_extraction (fixture OK).
File paths from TRACK_FILE_RULES — not AI-invented.

authority_state: ai_draft in YAML frontmatter of all outputs. non_authoritative: True.
src/ is NEVER created or modified.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Authoritative track file rules — same as mainstream_acceleration_packet.py
_TRACK_FILE_RULES: dict[str, dict[str, Any]] = {
    "fods": {
        "allowed": ["src/net/fods/FodsDocument.cs", "tests/net/fods/", "examples/net/fods/"],
        "forbidden": ["src/python/fods/", "registry/", "product-capability-matrix/"],
        "track": "commercial_net",
        "primary_source": "src/net/fods/FodsDocument.cs",
    },
    "fodt": {
        "allowed": ["src/net/fodt/FodtDocument.cs", "tests/net/fodt/", "examples/net/fodt/"],
        "forbidden": ["src/python/fodt/", "registry/", "product-capability-matrix/"],
        "track": "commercial_net",
        "primary_source": "src/net/fodt/FodtDocument.cs",
    },
    "netpbm": {
        "allowed": ["src/net/netpbm/", "tests/net/netpbm/", "examples/net/netpbm/"],
        "forbidden": ["src/python/netpbm/", "registry/", "product-capability-matrix/"],
        "track": "commercial_net",
        "primary_source": "src/net/netpbm/Model/NetpbmImage.cs",
    },
    "sylk": {
        "allowed": ["src/python/sylk/", "tests/python/sylk/", "examples/python/sylk/"],
        "forbidden": ["src/net/sylk/", "registry/", "product-capability-matrix/"],
        "track": "foss_reduced",
        "primary_source": "src/python/sylk/sylk_parser.py",
    },
    "dif": {
        "allowed": ["src/python/dif/", "tests/python/dif/"],
        "forbidden": ["registry/", "product-capability-matrix/"],
        "track": "foss_reduced",
        "primary_source": "src/python/dif/",
    },
    "zst": {
        "allowed": ["src/python/zst/", "tests/python/zst/"],
        "forbidden": ["registry/", "product-capability-matrix/"],
        "track": "foss_reduced",
        "primary_source": "src/python/zst/",
    },
}


def design_gap(
    format_id: str,
    gap_id: str,
    output_dir: Path,
    sprint_id: str = "",
) -> dict[str, str]:
    """Generate design docs for a gap. Returns mapping of doc type -> path."""
    output_dir.mkdir(parents=True, exist_ok=True)
    rules = _TRACK_FILE_RULES.get(format_id, {
        "allowed": [], "forbidden": [], "track": "unknown", "primary_source": "unknown",
    })

    design = _gateway_design(format_id, gap_id, rules, sprint_id)
    test_strategy = _gateway_test_strategy(format_id, gap_id, rules, sprint_id)
    dogfood_strategy = _gateway_dogfood(format_id, gap_id, rules, sprint_id)
    risk_review = _gateway_risk(format_id, gap_id, rules, sprint_id)

    safe_gap = gap_id.replace("/", "-").replace(".", "-")
    frontmatter = f"---\nauthority_state: ai_draft\nnon_authoritative: true\nformat: {format_id}\ngap_id: {gap_id}\ntimestamp: {datetime.now(timezone.utc).isoformat()}\n---\n\n"

    paths = {}
    for name, content in [
        ("design", design),
        ("test-strategy", test_strategy),
        ("dogfood-strategy", dogfood_strategy),
        ("risk-review", risk_review),
    ]:
        out_path = output_dir / f"{format_id}-{safe_gap}-{name}.md"
        out_path.write_text(frontmatter + content)
        try:
            paths[name] = str(out_path.relative_to(_REPO_ROOT))
        except ValueError:
            paths[name] = str(out_path)

    # Write summary JSON
    summary = {
        "sprint_id": sprint_id,
        "format": format_id,
        "gap_id": gap_id,
        "track": rules.get("track"),
        "allowed_files": rules.get("allowed"),
        "design_files": paths,
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    (output_dir / f"{format_id}-{safe_gap}-summary.json").write_text(json.dumps(summary, indent=2))
    # Also write canonical design.md for packet assembly
    (output_dir / f"{format_id}-design.md").write_text(frontmatter + design)

    return paths


def _gateway_design(format_id: str, gap_id: str, rules: dict, sprint_id: str) -> str:
    prompt = (
        f"Design an implementation for gap '{gap_id}' in the '{format_id}' format library.\n"
        f"Allowed files to modify: {rules.get('allowed', [])}.\n"
        f"Forbidden files: {rules.get('forbidden', [])}.\n"
        "Provide: 1) API signature, 2) implementation steps, 3) key XML/binary parsing notes.\n"
        "This is advisory only — authority_state: ai_draft."
    )
    return _call_gateway(prompt, sprint_id, "design", format_id, gap_id, "TC-TOOL-003", "gate-5")


def _gateway_test_strategy(format_id: str, gap_id: str, rules: dict, sprint_id: str) -> str:
    prompt = (
        f"Describe a test strategy for gap '{gap_id}' in '{format_id}'.\n"
        f"Test files go in: {[r for r in rules.get('allowed', []) if 'tests' in r]}.\n"
        "Cover: happy path, roundtrip, edge cases, dogfood export.\n"
        "This is advisory only — authority_state: ai_draft."
    )
    return _call_gateway(prompt, sprint_id, "test_strategy", format_id, gap_id, "TC-TOOL-003", "gate-5")


def _gateway_dogfood(format_id: str, gap_id: str, rules: dict, sprint_id: str) -> str:
    prompt = (
        f"Describe a dogfood export strategy for gap '{gap_id}' in '{format_id}'.\n"
        "How should the output of this capability be exported/converted to prove it works end-to-end?\n"
        "This is advisory only — authority_state: ai_draft."
    )
    return _call_gateway(prompt, sprint_id, "dogfood_strategy", format_id, gap_id, "TC-TOOL-003", "gate-5")


def _gateway_risk(format_id: str, gap_id: str, rules: dict, sprint_id: str) -> str:
    prompt = (
        f"Identify implementation risks for gap '{gap_id}' in '{format_id}'.\n"
        "Consider: XML namespace issues, encoding, large files, format version compatibility.\n"
        "This is advisory only — authority_state: ai_draft."
    )
    return _call_gateway(prompt, sprint_id, "risk_review", format_id, gap_id, "TC-TOOL-003", "gate-5")


def _call_gateway(
    prompt: str, sprint_id: str, operation: str,
    format_id: str, gap_id: str, taskcard_id: str, gate_id: str,
) -> str:
    try:
        from tools.ai.control_plane.config import load_ai_config
        from tools.ai.control_plane.gateway import gateway_chat
        from tools.ai.control_plane.model_router import ModelRouter
        from tools.ai.schemas.models import AIRole, ModelSelectionRequest

        cfg = load_ai_config()
        if not cfg.is_configured:
            return f"[fixture] No gateway for {operation} on {format_id}/{gap_id}."

        router = ModelRouter()
        decision = router.select(ModelSelectionRequest(role=AIRole.structured_extraction))
        if decision.fail_closed or not decision.selected_model_id:
            return "[fixture] No model for structured_extraction."

        messages = [{"role": "user", "content": prompt}]
        resp, record = gateway_chat(
            config=cfg, model=decision.selected_model_id, messages=messages,
            role="structured_extraction", operation=operation,
            sprint_id=sprint_id, taskcard_id=taskcard_id, gate_id=gate_id,
        )
        _append_ledger(sprint_id, operation, record)
        return resp.get("content", "") or f"[gateway_empty] No content for {operation}."
    except Exception as e:
        return f"[fixture_error] {type(e).__name__}: {e}"


def _append_ledger(sprint_id: str, operation: str, record: Any) -> None:
    ledger = _REPO_ROOT / "reports/acceleration-product-first/ai-usage-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "tool": "ai_implementation_designer",
        "operation": operation,
        "role": "structured_extraction",
        "status": record.status.value if hasattr(record, "status") else str(record),
        "authority_state": "ai_draft",
        "live_ai_used": hasattr(record, "status") and record.status.value == "success",
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Implementation Designer")
    parser.add_argument("--format", required=True)
    parser.add_argument("--gap-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--sprint-id", default="")
    args = parser.parse_args()

    paths = design_gap(
        format_id=args.format,
        gap_id=args.gap_id,
        output_dir=Path(args.output_dir),
        sprint_id=args.sprint_id,
    )
    print(f"format={args.format} gap_id={args.gap_id} docs={list(paths.keys())}")


if __name__ == "__main__":
    main()
