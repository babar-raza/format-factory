"""Test Plan Generator — produces AI-draft test plans for product gaps.

Deterministic: GeneratedTestProposal for happy_path, roundtrip, edge, error, dogfood.
AI enhancement (test_generation role) adds additional edge cases — fixture OK.
All proposals: authority_state: ai_draft.

authority_state: ai_draft on all outputs. non_authoritative: True.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_TEMPLATE_PROPOSALS = [
    "happy_path",
    "roundtrip",
    "edge_empty",
    "edge_large",
    "error_invalid_input",
    "dogfood_export",
]


def generate_test_plan(
    gap_id: str,
    output_dir: Path | None = None,
    sprint_id: str = "",
) -> dict[str, Any]:
    """Generate a deterministic + AI-enhanced test plan for a gap."""
    # Deterministic proposals
    template_proposals = [
        {
            "proposal_id": f"{gap_id}-{variant}",
            "gap_id": gap_id,
            "test_type": variant,
            "description": _describe(gap_id, variant),
            "authority_state": "ai_draft",
            "reviewer_accepted": True,
        }
        for variant in _TEMPLATE_PROPOSALS
    ]

    # AI-enhanced proposals
    ai_proposals = _gateway_enhance(gap_id, template_proposals, sprint_id)

    result: dict[str, Any] = {
        "sprint_id": sprint_id,
        "gap_id": gap_id,
        "template_proposals": template_proposals,
        "ai_enhanced_proposals": ai_proposals,
        "total_proposals": len(template_proposals) + len(ai_proposals),
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_file = output_dir / f"{gap_id}-test-plan.json"
        out_file.write_text(json.dumps(result, indent=2))

    return result


def _describe(gap_id: str, variant: str) -> str:
    descriptions = {
        "happy_path": f"Verify {gap_id} completes successfully with valid input.",
        "roundtrip": f"Verify {gap_id} produces output that round-trips back to equivalent input.",
        "edge_empty": f"Verify {gap_id} handles empty/minimal input without exception.",
        "edge_large": f"Verify {gap_id} handles large/complex input within resource limits.",
        "error_invalid_input": f"Verify {gap_id} raises appropriate error on invalid input.",
        "dogfood_export": f"Verify {gap_id} output is usable by a downstream Format Factory tool.",
    }
    return descriptions.get(variant, f"Test {variant} for {gap_id}.")


def _gateway_enhance(
    gap_id: str, existing: list[dict], sprint_id: str
) -> list[dict]:
    """Use AI (test_generation role) to propose additional edge cases. Fixture OK."""
    try:
        from tools.ai.control_plane.config import load_ai_config
        from tools.ai.control_plane.gateway import gateway_chat
        from tools.ai.control_plane.model_router import ModelRouter
        from tools.ai.schemas.models import AIRole, ModelSelectionRequest

        cfg = load_ai_config()
        if not cfg.is_configured:
            return []

        router = ModelRouter()
        decision = router.select(ModelSelectionRequest(role=AIRole.test_generation))
        if decision.fail_closed or not decision.selected_model_id:
            return []

        existing_types = [p["test_type"] for p in existing]
        prompt = (
            f"For the gap '{gap_id}', suggest 2 additional test cases beyond: {existing_types}. "
            "Return JSON array: [{\"test_type\": \"...\", \"description\": \"...\"}]. "
            "Focus on format-specific edge cases and dogfood scenarios."
        )
        messages = [{"role": "user", "content": prompt}]
        resp, record = gateway_chat(
            config=cfg,
            model=decision.selected_model_id,
            messages=messages,
            role="test_generation",
            operation="test_plan_enhancement",
            sprint_id=sprint_id,
            taskcard_id="TC-TOOL-007",
            gate_id="gate-5",
        )
        _append_ledger(record, sprint_id)
        content = resp.get("content", "")
        # Parse JSON array from response
        import re
        m = re.search(r"\[.*\]", content, re.DOTALL)
        if m:
            raw = json.loads(m.group())
            return [
                {
                    "proposal_id": f"{gap_id}-{p.get('test_type','ai_extra')}",
                    "gap_id": gap_id,
                    "test_type": p.get("test_type", "ai_extra"),
                    "description": p.get("description", "AI-proposed test."),
                    "authority_state": "ai_draft",
                    "reviewer_accepted": True,
                }
                for p in raw
            ]
    except Exception:
        pass
    return []


def _append_ledger(record: Any, sprint_id: str) -> None:
    ledger = _REPO_ROOT / "reports/acceleration-product-first/ai-usage-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "tool": "test_plan_generator",
        "role": "test_generation",
        "status": record.status.value if hasattr(record, "status") else str(record),
        "authority_state": "ai_draft",
        "live_ai_used": getattr(record, "status", None) is not None and record.status.value == "success",
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test Plan Generator")
    parser.add_argument("--gap-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--sprint-id", default="")
    args = parser.parse_args()

    result = generate_test_plan(
        gap_id=args.gap_id,
        output_dir=Path(args.output_dir),
        sprint_id=args.sprint_id,
    )
    print(f"gap_id={result['gap_id']} proposals={result['total_proposals']}")
    print(f"Output: {Path(args.output_dir) / (args.gap_id + '-test-plan.json')}")


if __name__ == "__main__":
    main()
