"""AI Product Brain — reads poc-targets.yaml deterministically, annotates with AI reasoning.

Observes the whole product system. Produces capability graph, distance scores,
gap rankings, over-investment analysis. All outputs ai_draft / non-authoritative.

poc-targets.yaml is NEVER modified. Format registry is NEVER modified.
AI role: summarization (fixture OK if gateway unavailable).

authority_state: ai_draft on all outputs. non_authoritative: True.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_POC_TARGETS = _REPO_ROOT / "product-capability-matrix/poc-targets.yaml"


def run_brain(
    sprint_id: str,
    output_dir: Path,
) -> dict[str, Any]:
    """Main entry point for AI Product Brain."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read poc-targets.yaml (read-only)
    poc_data = yaml.safe_load(_POC_TARGETS.read_text(encoding="utf-8"))
    poc_checksum = hashlib.sha256(_POC_TARGETS.read_bytes()).hexdigest()

    # Build capability graph deterministically
    cap_graph = _build_capability_graph(poc_data)
    _write(output_dir / "product-capability-graph.json", cap_graph, sprint_id)

    # Distance scores
    distance = _build_distance_scores(poc_data)
    _write(output_dir / "poc-distance-score.json", distance, sprint_id)

    # Gap rankings (AI-annotated)
    rankings = _build_gap_rankings(poc_data, sprint_id)
    _write(output_dir / "product-gap-rankings.json", rankings, sprint_id)

    # Over-investment analysis
    over_invest = _build_over_investment(poc_data, sprint_id)
    _write(output_dir / "over-investment-analysis.json", over_invest, sprint_id)

    # Append ledger entry
    _append_ledger(sprint_id, "brain_complete", poc_checksum)

    return {
        "sprint_id": sprint_id,
        "poc_targets_checksum": poc_checksum,
        "products_analyzed": len(cap_graph.get("products", [])),
        "authority_state": "ai_draft",
        "non_authoritative": True,
    }


def _build_capability_graph(poc: dict) -> dict:
    """Build deterministic capability graph from poc-targets.yaml."""
    products = []
    for product_key, product_data in poc.items():
        if not isinstance(product_data, dict):
            continue
        # Count gaps and passes
        gaps = [k for k, v in product_data.items() if isinstance(v, str) and "GAP" in v]
        passes = [k for k, v in product_data.items() if isinstance(v, str) and v == "PASS"]
        products.append({
            "product": product_key,
            "gap_count": len(gaps),
            "pass_count": len(passes),
            "top_gaps": gaps[:5],
        })
    return {
        "products": products,
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _build_distance_scores(poc: dict) -> dict:
    """Distance-to-completion score per product (0=complete, higher=more gaps)."""
    scores = []
    for product_key, product_data in poc.items():
        if not isinstance(product_data, dict):
            continue
        gaps = sum(1 for v in product_data.values() if isinstance(v, str) and "GAP" in v)
        passes = sum(1 for v in product_data.values() if isinstance(v, str) and v == "PASS")
        total = gaps + passes
        distance = round(gaps / total, 4) if total > 0 else 0.0
        scores.append({"product": product_key, "distance_score": distance, "gaps": gaps, "passes": passes})
    scores.sort(key=lambda x: x["distance_score"], reverse=True)
    return {
        "scores": scores,
        "note": "Higher distance_score = more gaps remaining. ai_draft only.",
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _build_gap_rankings(poc: dict, sprint_id: str) -> dict:
    """Rank gaps by priority. Deterministic base + AI annotation."""
    all_gaps = []
    for product_key, product_data in poc.items():
        if not isinstance(product_data, dict):
            continue
        for cap_key, cap_val in product_data.items():
            if isinstance(cap_val, str) and "GAP" in cap_val:
                all_gaps.append({
                    "product": product_key,
                    "capability": cap_key,
                    "gap_status": cap_val,
                    "priority_score": _priority(cap_key, cap_val),
                })
    all_gaps.sort(key=lambda x: x["priority_score"], reverse=True)
    top_gaps = all_gaps[:20]

    # AI annotation
    ai_note = _gateway_rank_comment(top_gaps[:5], sprint_id)

    return {
        "top_gaps": top_gaps,
        "ai_ranking_note": ai_note,
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _priority(cap_key: str, cap_val: str) -> int:
    """Priority heuristic: dogfood > external > other."""
    score = 0
    if "DOGFOOD" in cap_val:
        score += 10
    if "EXTERNAL" in cap_val:
        score += 5
    if "dotnet" in cap_key or "net" in cap_key.lower():
        score += 3
    if "installed" in cap_key.lower():
        score += 2
    return score


def _build_over_investment(poc: dict, sprint_id: str) -> dict:
    """Identify products with many PASS but still large gaps — potential machinery drift."""
    analysis = []
    for product_key, product_data in poc.items():
        if not isinstance(product_data, dict):
            continue
        passes = sum(1 for v in product_data.values() if isinstance(v, str) and v == "PASS")
        gaps = sum(1 for v in product_data.values() if isinstance(v, str) and "GAP" in v)
        if passes > 5 and gaps > 3:
            analysis.append({
                "product": product_key,
                "passes": passes,
                "gaps": gaps,
                "flag": "HIGH_PASS_WITH_REMAINING_GAPS",
            })

    ai_note = _gateway_invest_comment(analysis, sprint_id)

    return {
        "analysis": analysis,
        "ai_note": ai_note,
        "authority_state": "ai_draft",
        "non_authoritative": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _gateway_rank_comment(top_gaps: list, sprint_id: str) -> str:
    """AI comment on top gaps. Fixture OK."""
    try:
        from tools.ai.control_plane.config import load_ai_config
        from tools.ai.control_plane.gateway import gateway_chat
        from tools.ai.control_plane.model_router import ModelRouter
        from tools.ai.schemas.models import AIRole, ModelSelectionRequest

        cfg = load_ai_config()
        if not cfg.is_configured:
            return f"[fixture] Top gaps: {[g['capability'] for g in top_gaps]}."

        router = ModelRouter()
        decision = router.select(ModelSelectionRequest(role=AIRole.summarization))
        if decision.fail_closed or not decision.selected_model_id:
            return "[fixture] No model."

        gap_list = [f"{g['product']}.{g['capability']}" for g in top_gaps]
        prompt = (
            f"For a file format library, rank these gaps by product value: {gap_list}. "
            "In 2 sentences explain which to prioritize and why."
        )
        messages = [{"role": "user", "content": prompt}]
        resp, record = gateway_chat(
            config=cfg, model=decision.selected_model_id, messages=messages,
            role="summarization", operation="gap_ranking", sprint_id=sprint_id,
            taskcard_id="TC-TOOL-001", gate_id="gate-3",
        )
        _append_ledger(sprint_id, "gap_ranking", "")
        return resp.get("content", "") or "[gateway_empty]"
    except Exception as e:
        return f"[fixture_error] {type(e).__name__}: {e}"


def _gateway_invest_comment(analysis: list, sprint_id: str) -> str:
    """AI comment on over-investment signals. Fixture OK."""
    try:
        from tools.ai.control_plane.config import load_ai_config
        from tools.ai.control_plane.gateway import gateway_chat
        from tools.ai.control_plane.model_router import ModelRouter
        from tools.ai.schemas.models import AIRole, ModelSelectionRequest

        cfg = load_ai_config()
        if not cfg.is_configured:
            return f"[fixture] Over-investment flagged: {len(analysis)} products."

        router = ModelRouter()
        decision = router.select(ModelSelectionRequest(role=AIRole.summarization))
        if decision.fail_closed or not decision.selected_model_id:
            return "[fixture] No model."

        flags = [a["product"] for a in analysis]
        prompt = (
            f"Products with many passes but remaining gaps: {flags}. "
            "In 1 sentence explain what this suggests for sprint focus."
        )
        messages = [{"role": "user", "content": prompt}]
        resp, record = gateway_chat(
            config=cfg, model=decision.selected_model_id, messages=messages,
            role="summarization", operation="over_investment_analysis", sprint_id=sprint_id,
            taskcard_id="TC-TOOL-001", gate_id="gate-3",
        )
        _append_ledger(sprint_id, "over_investment", "")
        return resp.get("content", "") or "[gateway_empty]"
    except Exception as e:
        return f"[fixture_error] {type(e).__name__}: {e}"


def _write(path: Path, data: dict, sprint_id: str) -> None:
    if "sprint_id" not in data:
        data["sprint_id"] = sprint_id
    path.write_text(json.dumps(data, indent=2))


def _append_ledger(sprint_id: str, operation: str, checksum: str) -> None:
    ledger = _REPO_ROOT / "reports/acceleration-product-first/ai-usage-ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "tool": "ai_product_brain",
        "operation": operation,
        "authority_state": "ai_draft",
        "live_ai_used": True,
    }
    with open(ledger, "a") as f:
        f.write(json.dumps(entry) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="AI Product Brain")
    parser.add_argument("--sprint-id", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    result = run_brain(sprint_id=args.sprint_id, output_dir=Path(args.output_dir))
    print(f"products_analyzed={result['products_analyzed']}")
    print(f"poc_targets_checksum={result['poc_targets_checksum']}")
    print(f"authority_state={result['authority_state']}")


if __name__ == "__main__":
    main()
