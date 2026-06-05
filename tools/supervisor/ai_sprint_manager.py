"""AI Sprint Manager — non-authoritative adaptive sprint management.

Three passes: pre (plan), mid (reroute), final (review + next-sprint recommendation).
Role: agentic_low_risk — NO fixture fallback. If gateway unavailable: status=skipped.

advisory_only: True on all outputs. authority_state: ai_draft.
Never modifies authority files. Never replaces evidence or gates.

authority_state: ai_draft on all outputs. non_authoritative: True.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

_PASS_OUTPUTS = {
    "pre": "pre-sprint-plan.json",
    "mid": "mid-sprint-reroute.json",
    "final": "final-review.json",
}


def run_pass(
    pass_name: str,
    sprint_id: str,
    output_dir: Path,
    brain_dir: Path | None = None,
    lane_ledger: Path | None = None,
) -> dict[str, Any]:
    """Execute one sprint management pass."""
    output_dir.mkdir(parents=True, exist_ok=True)

    result = _gateway_sprint_pass(pass_name, sprint_id, brain_dir, lane_ledger)
    out_file = output_dir / _PASS_OUTPUTS[pass_name]
    out_file.write_text(json.dumps(result, indent=2))

    if pass_name == "final":
        # Also write next-sprint recommendation as markdown
        rec_md = _build_recommendation_md(result, sprint_id)
        (output_dir / "next-sprint-recommendation.md").write_text(rec_md)

    return result


def _gateway_sprint_pass(
    pass_name: str,
    sprint_id: str,
    brain_dir: Path | None,
    lane_ledger: Path | None,
) -> dict[str, Any]:
    """Attempt agentic_low_risk call. If unavailable: status=skipped (never fixture)."""
    # Always include pass-specific required fields with defaults
    _pass_defaults = {
        "pre": {"lane_design": {"note": "skipped_no_model"}, "dependency_map": {}},
        "mid": {"stuck_lanes": [], "reroute_suggestions": [], "breadth_warning": False},
        "final": {"sprint_grade": {"product_progress": "ai_draft", "governance_progress": "ai_draft", "poc_movement": "ai_draft"}, "top_learnings": [], "next_sprint_focus": []},
    }
    base = {
        "pass_name": pass_name,
        "sprint_id": sprint_id,
        "advisory_only": True,
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **_pass_defaults.get(pass_name, {}),
    }

    try:
        from tools.ai.control_plane.config import load_ai_config
        from tools.ai.control_plane.gateway import gateway_chat
        from tools.ai.control_plane.model_router import ModelRouter as _ModelRouter
        from tools.ai.schemas.models import AIRole, ModelSelectionRequest

        cfg = load_ai_config()
        if not cfg.is_configured:
            return {**base, "status": "skipped", "reason": "gateway_not_configured"}

        router = _ModelRouter()
        decision = router.select(ModelSelectionRequest(role=AIRole.agentic_low_risk))
        if decision.fail_closed or not decision.selected_model_id:
            _append_ledger(sprint_id, pass_name, "skipped_no_model")
            return {**base, "status": "skipped", "reason": "no_model_for_agentic_low_risk"}

        # Build context
        context = _build_context(pass_name, brain_dir, lane_ledger)
        prompt = _build_prompt(pass_name, sprint_id, context)
        messages = [{"role": "user", "content": prompt}]

        resp, record = gateway_chat(
            config=cfg, model=decision.selected_model_id, messages=messages,
            role="agentic_low_risk", operation=f"sprint_manager_{pass_name}",
            sprint_id=sprint_id, taskcard_id="TC-TOOL-002", gate_id=f"gate-{_pass_gate(pass_name)}",
        )
        _append_ledger(sprint_id, pass_name, record.status.value if hasattr(record, "status") else "unknown")

        content = resp.get("content", "")
        return {**base, "status": "completed", "ai_output": content, **_parse_pass(pass_name, content)}

    except Exception as e:
        _append_ledger(sprint_id, pass_name, f"error_{type(e).__name__}")
        return {**base, "status": "skipped", "reason": f"exception_{type(e).__name__}"}


def _build_context(pass_name: str, brain_dir: Path | None, lane_ledger: Path | None) -> str:
    ctx_parts = []
    if brain_dir and brain_dir.exists() and pass_name == "pre":
        for fname in ["product-gap-rankings.json", "poc-distance-score.json"]:
            p = brain_dir / fname
            if p.exists():
                ctx_parts.append(f"{fname}: {p.read_text()[:500]}")
    if lane_ledger and lane_ledger.exists() and pass_name in ("mid", "final"):
        ctx_parts.append(f"lane_ledger: {lane_ledger.read_text()[:500]}")
    return "\n".join(ctx_parts) if ctx_parts else "No additional context available."


def _build_prompt(pass_name: str, sprint_id: str, context: str) -> str:
    base = f"Sprint: {sprint_id}\nContext:\n{context}\n\n"
    if pass_name == "pre":
        return base + (
            "Design a sprint lane plan. Return JSON with keys: lane_design (object), dependency_map (object). "
            "advisory_only: true. Be specific about which lanes run in parallel vs sequential."
        )
    elif pass_name == "mid":
        return base + (
            "Review mid-sprint progress. Return JSON with keys: stuck_lanes (list), "
            "reroute_suggestions (list), breadth_warning (bool). advisory_only: true."
        )
    else:
        return base + (
            "Provide final sprint review. Return JSON with keys: sprint_grade (object with "
            "product_progress str, governance_progress str, poc_movement str), "
            "top_learnings (list), next_sprint_focus (list). advisory_only: true."
        )


def _parse_pass(pass_name: str, content: str) -> dict:
    """Try to extract structured fields from AI response."""
    import re
    m = re.search(r"\{.*\}", content, re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group())
            if pass_name == "pre":
                return {
                    "lane_design": parsed.get("lane_design", {"note": "AI draft"}),
                    "dependency_map": parsed.get("dependency_map", {}),
                }
            elif pass_name == "mid":
                return {
                    "stuck_lanes": parsed.get("stuck_lanes", []),
                    "reroute_suggestions": parsed.get("reroute_suggestions", []),
                    "breadth_warning": parsed.get("breadth_warning", False),
                }
            else:
                return {
                    "sprint_grade": parsed.get("sprint_grade", {
                        "product_progress": "ai_draft",
                        "governance_progress": "ai_draft",
                        "poc_movement": "ai_draft",
                    }),
                    "top_learnings": parsed.get("top_learnings", []),
                    "next_sprint_focus": parsed.get("next_sprint_focus", []),
                }
        except Exception:
            pass
    # Defaults if parse fails
    if pass_name == "pre":
        return {"lane_design": {"note": "parse_failed"}, "dependency_map": {}}
    elif pass_name == "mid":
        return {"stuck_lanes": [], "reroute_suggestions": [], "breadth_warning": False}
    return {"sprint_grade": {"product_progress": "ai_draft", "governance_progress": "ai_draft", "poc_movement": "ai_draft"}}


def _build_recommendation_md(result: dict, sprint_id: str) -> str:
    grade = result.get("sprint_grade", {})
    focus = result.get("next_sprint_focus", [])
    return f"""# Next Sprint Recommendation

Sprint: {sprint_id}
Generated: {datetime.now(timezone.utc).isoformat()}
authority_state: ai_draft
advisory_only: true

## Sprint Grade
- Product Progress: {grade.get("product_progress", "N/A")}
- Governance Progress: {grade.get("governance_progress", "N/A")}
- POC Movement: {grade.get("poc_movement", "N/A")}

## Top Focus Areas for Next Sprint
{chr(10).join(f"- {f}" for f in (focus if focus else ["See gap rankings for details."]))}

## Top Learnings
{chr(10).join(f"- {l}" for l in result.get("top_learnings", ["See learning loop for details."]))}

---
This recommendation is advisory only. Supervisor grading and test evidence are authoritative.
"""


def _pass_gate(pass_name: str) -> str:
    return {"pre": "4", "mid": "6", "final": "8"}.get(pass_name, "?")


def _append_ledger(sprint_id: str, operation: str, status: str) -> None:
    ledger = _REPO_ROOT / "reports/acceleration-product-first/ai-usage-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "tool": "ai_sprint_manager",
        "operation": operation,
        "status": status,
        "role": "agentic_low_risk",
        "authority_state": "ai_draft",
        "live_ai_used": status == "success",
        "no_fixture_fallback": True,
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Sprint Manager")
    parser.add_argument("--pass", dest="pass_name", required=True, choices=["pre", "mid", "final"])
    parser.add_argument("--sprint-id", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--brain-dir", default=None)
    parser.add_argument("--lane-ledger", default=None)
    args = parser.parse_args()

    result = run_pass(
        pass_name=args.pass_name,
        sprint_id=args.sprint_id,
        output_dir=Path(args.output_dir),
        brain_dir=Path(args.brain_dir) if args.brain_dir else None,
        lane_ledger=Path(args.lane_ledger) if args.lane_ledger else None,
    )
    print(f"pass={result['pass_name']} status={result.get('status','?')} advisory_only={result['advisory_only']}")


if __name__ == "__main__":
    main()
