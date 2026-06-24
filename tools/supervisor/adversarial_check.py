"""
adversarial_check.py — TC-AMD-LLM-001: LLM adversarial contradiction scan.

Created as a separate file because autonomous_cycle.py is at LOC cap (2374/2374).
Non-blocking: all failures return {"status": "skipped", ...} — never raises.

Uses _get_sv_gateway() from grade_declared_work (same pattern as autonomous_cycle.py:1049).
Requires LLM env vars (GPT_OSS_ENDPOINT + GPT_OSS_API_KEY or PROFESSIONALIZE_*).
Gracefully degrades when LLM is not configured.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def run_adversarial_check(
    review: dict, repo_root: "Path", sprint_id: str, iteration: int = 0
) -> dict:
    """Run LLM adversarial scan on sprint grades. Non-blocking — never raises.

    Returns a dict with:
      status: "completed" | "skipped"
      reason: present when status="skipped"
      findings: list of {severity, item_id, issue} when status="completed"
      overall_risk: "LOW" | "MEDIUM" | "HIGH" when status="completed"
    """
    try:
        sys.path.insert(0, str(repo_root / "tools" / "supervisor"))
        from grade_declared_work import _get_sv_gateway  # noqa: PLC0415
        gw, cfg = _get_sv_gateway()
    except Exception:
        return {"status": "skipped", "reason": "gateway_unavailable"}

    if not gw or not getattr(cfg, "is_configured", False):
        return {"status": "skipped", "reason": "llm_not_configured"}

    grades_summary = "\n".join(
        f"- {g.get('item_id', '?')}: {g.get('supervisor_grade', '?')} "
        f"(evidence: {g.get('evidence_quality_score', 0):.2f})"
        for g in review.get("item_grades", [])
    )
    if not grades_summary:
        return {"status": "skipped", "reason": "no_grades_to_check"}

    messages = [
        {
            "role": "system",
            "content": (
                "You are an adversarial audit agent. Identify overclaims, inconsistencies, "
                "or contradictions in sprint grades. Be specific. "
                'Output JSON only: {"findings": [{"severity": "HIGH|MEDIUM|LOW", '
                '"item_id": "str", "issue": "str"}], "overall_risk": "LOW|MEDIUM|HIGH"}'
            ),
        },
        {
            "role": "user",
            "content": f"Sprint: {sprint_id}\nIteration: {iteration}\nGrades:\n{grades_summary}",
        },
    ]
    try:
        response, _ = gw(messages=messages)
        content = response.get("content", "")
        if not content:
            return {"status": "skipped", "reason": "empty_response"}
        result = json.loads(content)
    except Exception as exc:
        return {"status": "skipped", "reason": f"llm_error: {exc}"}

    result.update({"status": "completed", "sprint_id": sprint_id, "iteration": iteration})
    return result


def write_adversarial_result(result: dict, repo_root: "Path", sprint_id: str) -> None:
    """Write result to .local/supervisor/adversarial-check-{sprint_id}.json atomically."""
    out_dir = repo_root / ".local" / "supervisor"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"adversarial-check-{sprint_id}.json"
    tmp = out_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(result, indent=2), encoding="utf-8")
    os.replace(str(tmp), str(out_path))


def run_and_write(
    review: dict, repo_root: "Path", sprint_id: str, iteration: int = 0
) -> int:
    """Combined run+write. Returns count of HIGH findings (0 if skipped/error). Non-blocking."""
    try:
        result = run_adversarial_check(review, repo_root, sprint_id, iteration)
        if result.get("status") == "completed":
            write_adversarial_result(result, repo_root, sprint_id)
            return len([f for f in result.get("findings", []) if f.get("severity") == "HIGH"])
    except Exception:
        pass
    return 0
