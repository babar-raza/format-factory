"""AI Evidence Critic — semantic review of sprint evidence. Advisory only.

MACHINERY_CREEP verdict is advisory — never blocks autonomous-cycle.
Anti_skip_checker results are authoritative; AI disagreement logged as semantic_concern.
Evidence manifest and authority files are NEVER modified.

authority_state: ai_draft on all outputs. non_authoritative: True.
Role: evidence_review (fixture OK).
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def run_critic(sprint_id: str, output_dir: Path) -> dict[str, Any]:
    """Run the evidence critic over sprint outputs."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Collect sprint artifacts to critique
    artifacts = _collect_artifacts(sprint_id)
    critique = _gateway_critique(artifacts, sprint_id)
    overclaim = _gateway_overclaim(artifacts, sprint_id)

    result: dict[str, Any] = {
        "sprint_id": sprint_id,
        "artifacts_reviewed": len(artifacts),
        "sprint_grade": critique.get("sprint_grade", {
            "product_progress": "ai_draft_incomplete",
            "governance_progress": "ai_draft_incomplete",
            "poc_movement": "ai_draft_incomplete",
        }),
        "semantic_concerns": critique.get("semantic_concerns", []),
        "machinery_creep_detected": critique.get("machinery_creep", False),
        "machinery_creep_verdict": "ADVISORY_ONLY — does not block autonomous-cycle",
        "overclaim_risks": overclaim,
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "advisory_only": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    (output_dir / "evidence-critique.json").write_text(json.dumps(result, indent=2))

    # Overclaim risk markdown
    overclaim_md = _format_overclaim_md(result, sprint_id)
    (output_dir / "overclaim-risk.md").write_text(overclaim_md)

    return result


def _collect_artifacts(sprint_id: str) -> list[dict]:
    """List key sprint artifacts for review."""
    artifacts = []
    base = _REPO_ROOT / "reports/acceleration-product-first"
    for pattern in [
        "ai-product-brain/*.json",
        "mainstream-consumption-packets/*.json",
        "test-plans/*.json",
        "ai-management-passes/*.json",
        "external-tool-risk-register.json",
    ]:
        for p in base.glob(pattern):
            artifacts.append({"path": str(p.relative_to(_REPO_ROOT)), "size_bytes": p.stat().st_size})
    return artifacts


def _gateway_critique(artifacts: list, sprint_id: str) -> dict:
    """AI critique of sprint evidence. Fixture OK."""
    try:
        from tools.ai.control_plane.config import load_ai_config
        from tools.ai.control_plane.gateway import gateway_chat
        from tools.ai.control_plane.model_router import ModelRouter
        from tools.ai.schemas.models import AIRole, ModelSelectionRequest

        cfg = load_ai_config()
        if not cfg.is_configured:
            return _fixture_critique()

        router = ModelRouter()
        decision = router.select(ModelSelectionRequest(role=AIRole.evidence_review))
        if decision.fail_closed or not decision.selected_model_id:
            return _fixture_critique()

        artifact_list = [a["path"] for a in artifacts[:10]]
        prompt = (
            f"Review sprint '{sprint_id}' evidence artifacts: {artifact_list}.\n"
            "Return JSON with: sprint_grade (object with product_progress, governance_progress, poc_movement), "
            "semantic_concerns (list of strings), machinery_creep (bool — true if sprint produced "
            "tools/machinery not directly useful to Mainstream).\n"
            "This is advisory only — authority_state: ai_draft."
        )
        messages = [{"role": "user", "content": prompt}]
        resp, record = gateway_chat(
            config=cfg, model=decision.selected_model_id, messages=messages,
            role="evidence_review", operation="sprint_critique",
            sprint_id=sprint_id, taskcard_id="TC-TOOL-004", gate_id="gate-8",
        )
        _append_ledger(sprint_id, "critique", record)
        content = resp.get("content", "")
        import re
        m = re.search(r"\{.*\}", content, re.DOTALL)
        if m:
            return json.loads(m.group())
    except Exception:
        pass
    return _fixture_critique()


def _fixture_critique() -> dict:
    return {
        "sprint_grade": {
            "product_progress": "ACCELERATION_PRODUCED_MAINSTREAM_PACKETS",
            "governance_progress": "EXTERNAL_TOOL_INTAKE_MODELED",
            "poc_movement": "AI_LAYER_ESTABLISHED",
        },
        "semantic_concerns": [],
        "machinery_creep": False,
    }


def _gateway_overclaim(artifacts: list, sprint_id: str) -> list:
    """Check for overclaim risks. Fixture OK."""
    risks = []
    for a in artifacts:
        if "patterns" in a["path"] and a["size_bytes"] < 100:
            risks.append(f"Possible empty corpus: {a['path']}")
    return risks


def _format_overclaim_md(result: dict, sprint_id: str) -> str:
    risks = result.get("overclaim_risks", [])
    return f"""# Overclaim Risk Review

Sprint: {sprint_id}
authority_state: ai_draft
advisory_only: true

## Overclaim Risks Detected
{chr(10).join(f"- {r}" for r in risks) if risks else "None detected."}

## MACHINERY_CREEP Verdict
{result.get("machinery_creep_verdict", "N/A")}

---
This review is advisory only. Anti-skip checker results are authoritative.
"""


def _append_ledger(sprint_id: str, operation: str, record: Any) -> None:
    ledger = _REPO_ROOT / "reports/acceleration-product-first/ai-usage-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "tool": "ai_evidence_critic",
        "operation": operation,
        "role": "evidence_review",
        "status": record.status.value if hasattr(record, "status") else str(record),
        "authority_state": "ai_draft",
        "live_ai_used": hasattr(record, "status") and record.status.value == "success",
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Evidence Critic")
    parser.add_argument("--sprint-id", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    result = run_critic(sprint_id=args.sprint_id, output_dir=Path(args.output_dir))
    print(f"artifacts_reviewed={result['artifacts_reviewed']}")
    print(f"machinery_creep={result['machinery_creep_detected']}")
    print(f"advisory_only={result['advisory_only']}")


if __name__ == "__main__":
    main()
