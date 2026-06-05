"""Mainstream Acceleration Packet — assembles AI-draft packets for Mainstream consumption.

Combines: gap selection, AI rationale, implementation design, test strategy,
source patterns, test plan, execution handoff paths (TRACK_FILE_RULES authoritative),
external_tool_context, governance rules, downgrade rules.

All outputs: authority_state: ai_draft, non_authoritative: True, requires_validation: True.
No src/ files created. No poc-targets.yaml modification.

authority_state: ai_draft on all outputs. non_authoritative: True.

Schema version: 1.1.0
Added fields: packet_version, stream, test_plan_exists, skills_handoff_compatibility,
supervisor_routing_compatibility, required_mainstream_validation, runtime_status,
stale_or_error_flags, directly_consumable.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PACKET_SCHEMA_VERSION = "1.1.0"

# Authoritative track file rules (from generate_execution_handoff.py)
_TRACK_FILE_RULES: dict[str, dict[str, list[str]]] = {
    "fods": {
        "allowed": [
            "src/net/fods/FodsDocument.cs",
            "tests/net/fods/",
            "examples/net/fods/",
        ],
        "forbidden": [
            "src/python/fods/",
            "registry/",
            "product-capability-matrix/",
        ],
        "product_track": "commercial_net",
    },
    "fodt": {
        "allowed": [
            "src/net/fodt/FodtDocument.cs",
            "tests/net/fodt/",
            "examples/net/fodt/",
        ],
        "forbidden": [
            "src/python/fodt/",
            "registry/",
            "product-capability-matrix/",
        ],
        "product_track": "commercial_net",
    },
    "netpbm": {
        "allowed": [
            "src/net/netpbm/",
            "tests/net/netpbm/",
            "examples/net/netpbm/",
        ],
        "forbidden": [
            "src/python/netpbm/",
            "registry/",
            "product-capability-matrix/",
        ],
        "product_track": "commercial_net",
    },
    "sylk": {
        "allowed": [
            "src/python/sylk/",
            "tests/python/sylk/",
            "examples/python/sylk/",
        ],
        "forbidden": [
            "src/net/sylk/",
            "registry/",
            "product-capability-matrix/",
        ],
        "product_track": "foss_reduced",
    },
    "dif": {
        "allowed": ["src/python/dif/", "tests/python/dif/"],
        "forbidden": ["registry/", "product-capability-matrix/"],
        "product_track": "foss_reduced",
    },
    "zst": {
        "allowed": ["src/python/zst/", "tests/python/zst/"],
        "forbidden": ["registry/", "product-capability-matrix/"],
        "product_track": "foss_reduced",
    },
}

_GOVERNANCE_RULES = [
    "No product capability matrix update from AI draft alone — requires test evidence.",
    "No authority file modification from AI output without human gate.",
    "Implementation design is advisory — Mainstream worker decides final implementation.",
    "Test plan is advisory — Mainstream worker selects and adapts tests.",
    "Source patterns are read-only observations — no src/ modification by Acceleration.",
    "All AI outputs must carry authority_state: ai_draft until human evaluation.",
    "External tool context is optional and non-blocking for packet consumption.",
]

_DOWNGRADE_RULES = [
    "If test plan references API not confirmed in source, downgrade to ai_draft.",
    "If implementation design references capability not in poc-targets.yaml, downgrade to ai_draft.",
    "If source patterns are empty (corpus_empty=true), note limited evidence.",
    "If AI calls used fixture mode, label outputs live_ai_used: false.",
    "If ai_rationale contains fixture_error, set runtime_status=degraded and directly_consumable=False.",
    "If test_plan_path is null, set test_plan_exists=False and add stale_or_error_flags entry.",
]

_REQUIRED_MAINSTREAM_VALIDATION = [
    "Run all tests referenced in test_plan before using packet as implementation basis.",
    "Verify allowed_files are correct for this format's product track.",
    "Confirm capability_path exists in poc-targets.yaml before starting implementation.",
    "Review implementation_design_path content as advisory input only.",
    "Do not update poc-targets.yaml from packet alone — requires test evidence.",
]


def build_packet(
    format_id: str,
    capability_path: str,
    output_dir: Path,
    sprint_id: str = "",
) -> dict[str, Any]:
    """Build one Mainstream acceleration packet."""
    rules = _TRACK_FILE_RULES.get(format_id, {
        "allowed": [], "forbidden": ["registry/", "product-capability-matrix/"],
        "product_track": "unknown",
    })

    # Load companion artifacts if present
    source_patterns_path = _find_artifact(
        f"reports/acceleration-product-first/source-patterns/{format_id}-patterns.json"
    )
    design_path = _find_artifact(
        f"reports/acceleration-product-first/ai-implementation-designs/{format_id}-design.md"
    )
    test_plan_path = _find_test_plan(format_id, capability_path)

    # AI rationale via gateway (summarization role, fixture OK)
    ai_rationale = _gateway_rationale(format_id, capability_path, sprint_id)

    # Determine runtime health
    has_fixture_error = "fixture_error" in str(ai_rationale)
    stale_flags: list[str] = []
    if has_fixture_error:
        stale_flags.append(f"ai_rationale_degraded: {ai_rationale[:120]}")
    if test_plan_path is None:
        stale_flags.append("test_plan_path_not_found: test plan could not be located")
    runtime_status = "degraded" if has_fixture_error else "ok"
    directly_consumable = not has_fixture_error

    packet: dict[str, Any] = {
        "packet_version": _PACKET_SCHEMA_VERSION,
        "stream": "acceleration",
        "sprint_id": sprint_id,
        "format": format_id,
        "capability_path": capability_path,
        "product_track": rules["product_track"],
        "selected_gap": capability_path,
        "source_patterns_path": source_patterns_path,
        "implementation_design_path": design_path,
        "test_plan_path": test_plan_path,
        "test_plan_exists": test_plan_path is not None,
        "ai_rationale": ai_rationale,
        "allowed_files": rules["allowed"],
        "forbidden_files": rules["forbidden"],
        "governance_rules": _GOVERNANCE_RULES,
        "downgrade_rules": _DOWNGRADE_RULES,
        "required_mainstream_validation": _REQUIRED_MAINSTREAM_VALIDATION,
        "runtime_status": runtime_status,
        "directly_consumable": directly_consumable,
        "stale_or_error_flags": stale_flags,
        "skills_handoff_compatibility": {
            "compatible": True,
            "skills_can_use_packet": True,
            "skills_normalization_required": True,
            "authority_state": "ai_draft",
            "note": "Skills stream may use packet data as advisory input; normalization required before registry entry.",
        },
        "supervisor_routing_compatibility": {
            "compatible": True,
            "supervisor_verdict": "ACCELERATION_CONSUMABLE_WITH_LIMITATIONS" if stale_flags else "ACCELERATION_CONSUMABLE",
            "authority_state": "ai_draft",
            "note": "Supervisor can route this packet to Mainstream as advisory input. Mainstream must validate all claims.",
        },
        "capability_matrix_update_hint": {
            "note": "Do not update poc-targets.yaml from AI draft alone. Run tests first.",
            "authority_state": "ai_draft",
        },
        "external_tool_context": {
            "ruflo_context_available": False,
            "ruflo_mode": "absent",
            "superpowers_skill_pattern_available": False,
            "superpowers_relevant_skills": [],
            "ghidra_mcp_applicable": False,
            "ghidra_mcp_activation_required": False,
            "external_tool_recommendations": [],
            "external_tool_activation_required_for_packet": False,
            "authority_state": "ai_draft",
            "non_authoritative": True,
        },
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "requires_validation": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    safe_name = capability_path.replace(".", "-").replace("/", "-")
    out_file = output_dir / f"{format_id}-{safe_name}.json"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(packet, indent=2))
    return packet


def _find_artifact(rel_path: str) -> str | None:
    p = _REPO_ROOT / rel_path
    return str(p.relative_to(_REPO_ROOT)) if p.exists() else None


def _find_test_plan(format_id: str, capability_path: str) -> str | None:
    """Find test plan file using multiple naming patterns."""
    base_dir = _REPO_ROOT / "reports/acceleration-product-first/test-plans"
    candidates = [
        # Exact capability-path pattern
        base_dir / f"{capability_path.replace('.', '-')}-test-plan.json",
        # Format-prefixed short names (common convention)
        base_dir / f"{format_id}-dogfood-csv-test-plan.json",
        base_dir / f"{format_id}-dogfood-markdown-test-plan.json",
        base_dir / f"{format_id}-export-test-plan.json",
        base_dir / f"{format_id}-csv-export-test-plan.json",
        base_dir / f"{format_id}-write-test-plan.json",
    ]
    # Also try any file starting with format_id in the test-plans dir
    if base_dir.exists():
        for f in sorted(base_dir.glob(f"{format_id}-*.json")):
            candidates.append(f)

    for c in candidates:
        if c.exists():
            try:
                return str(c.relative_to(_REPO_ROOT))
            except ValueError:
                return str(c)
    return None


def _gateway_rationale(format_id: str, capability_path: str, sprint_id: str) -> str:
    """Get AI rationale for why this gap matters. Fixture OK.

    Ensures tools.ai imports work regardless of Python environment by
    inserting repo root into sys.path if needed.
    """
    repo_root_str = str(_REPO_ROOT)
    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    try:
        from tools.ai.control_plane.config import load_ai_config
        from tools.ai.control_plane.gateway import gateway_chat
        from tools.ai.control_plane.model_router import ModelRouter
        from tools.ai.schemas.models import AIRole, ModelSelectionRequest

        cfg = load_ai_config()
        if not cfg.is_configured:
            return f"[fixture] Gap {capability_path} for {format_id}: priority gap per poc-targets.yaml."

        router = ModelRouter()
        decision = router.select(ModelSelectionRequest(role=AIRole.summarization))
        if decision.fail_closed or not decision.selected_model_id:
            return f"[fixture] No model for rationale. Gap: {capability_path}."

        prompt = (
            f"In 2-3 sentences, explain why closing the gap '{capability_path}' for the "
            f"'{format_id}' format would improve the Format Factory product. "
            "Focus on concrete product value for a file format library user."
        )
        messages = [{"role": "user", "content": prompt}]
        resp, record = gateway_chat(
            config=cfg,
            model=decision.selected_model_id,
            messages=messages,
            role="summarization",
            operation="packet_rationale",
            sprint_id=sprint_id,
            taskcard_id="TC-TOOL-008",
            gate_id="gate-7",
        )
        _append_ledger(record, sprint_id)
        return resp.get("content", "") or "[gateway_empty]"
    except Exception as e:
        return f"[fixture_error] {type(e).__name__}: {e}"


def _append_ledger(record: Any, sprint_id: str) -> None:
    ledger = _REPO_ROOT / "reports/acceleration-product-first/ai-usage-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "tool": "mainstream_acceleration_packet",
        "role": "summarization",
        "status": record.status.value if hasattr(record, "status") else str(record),
        "authority_state": "ai_draft",
        "live_ai_used": getattr(record, "status", None) is not None and record.status.value == "success",
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mainstream Acceleration Packet Builder")
    parser.add_argument("--format", required=True)
    parser.add_argument("--capability-path", required=True)
    parser.add_argument("--sprint-id", default="")
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    packet = build_packet(
        format_id=args.format,
        capability_path=args.capability_path,
        output_dir=Path(args.output_dir),
        sprint_id=args.sprint_id,
    )
    print(f"format={packet['format']} track={packet['product_track']} gap={packet['selected_gap']}")
    out = Path(args.output_dir) / f"{args.format}-{args.capability_path.replace('.', '-')}.json"
    print(f"Output: {out}")


if __name__ == "__main__":
    main()
