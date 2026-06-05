"""
generate_stream_routing_packet.py — Wire product_velocity_scorer into Supervisor routing.

Accepts replay results + POC gap data and produces:
  - product_velocity_score.json
  - product_velocity_summary.md
  - stream_decision.json
  - false_pass_false_stop_assessment.json

Usage:
    python tools/supervisor/generate_stream_routing_packet.py \\
        --stream mainstream \\
        --replay-results reports/supervisor-product-first/replay-results.json \\
        --gaps .local/supervisor/selected-product-gaps.json \\
        --output-dir reports/supervisor-product-traffic-controller
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any


def _load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _find_replay(replay_results: list[dict], stream: str) -> dict:
    for entry in replay_results:
        if entry.get("stream") == stream:
            return entry
    return {}


def _build_evidence_from_replay(replay: dict, gaps: list[dict], stream: str) -> dict:
    """Convert replay result + gap list into evidence dict for velocity scorer."""
    vel = replay.get("product_velocity_score", {})
    mainstream_gaps = [g for g in gaps if g.get("stream") == "mainstream"]
    formats_touched = list({g["format"] for g in mainstream_gaps})

    return {
        "families_touched": vel.get("product_breadth_score", 0),
        "source_diffs": vel.get("product_breadth_score", 0),
        "mainstream_blocker_removed": vel.get("mainstream_blocker_removed", False),
        "false_pass_prevented": replay.get("false_pass_risk") == "low",
        "false_stop_prevented": replay.get("false_stop_risk") == "low",
        "acceleration_output_consumed": replay.get("acceleration_consumption") == "consumed",
        "governed_execution_consumed": replay.get("skills_consumption") == "consumed",
        "governed_transcripts": 1 if replay.get("skills_consumption") == "consumed" else 0,
        "ai_acceleration_consumed": False,
        "human_handoff_reduced": False,
        "test_delta": 0,
        "claimed_product_breadth": vel.get("product_breadth_score", 0) > 0,
        "repair_items": 0,
        "product_items": max(1, len(mainstream_gaps)),
        "formats_available": formats_touched,
        "declared_items": [],
    }


def score_stream(stream: str, replay: dict, gaps: list[dict]) -> dict:
    """Run the full 12-dimension score for a stream."""
    sys.path.insert(0, str(Path(__file__).parent))
    from product_velocity_scorer import (
        score_stream_velocity,
        classify_mainstream_package,
        compute_product_output_floor,
        detect_semantic_drift_risk,
    )

    evidence = _build_evidence_from_replay(replay, gaps, stream)
    velocity = score_stream_velocity(stream, evidence, {}, {})
    classification = classify_mainstream_package(evidence) if stream == "mainstream" else None
    floor_met = compute_product_output_floor(evidence)
    drift = detect_semantic_drift_risk(stream, evidence)

    return {
        "stream": stream,
        "sprint_id": replay.get("sprint_id", "unknown"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "velocity_score": velocity,
        "mainstream_classification": classification,
        "product_output_floor_met": floor_met,
        "semantic_drift_risk": drift,
        "prior_decision": replay.get("final_supervisor_decision", "unknown"),
        "evidence_summary": {
            "families_touched": evidence["families_touched"],
            "source_diffs": evidence["source_diffs"],
            "governed_transcripts": evidence["governed_transcripts"],
            "mainstream_blocker_removed": evidence["mainstream_blocker_removed"],
        },
    }


def compute_stream_decision(scored: dict, gaps: list[dict], stream: str) -> dict:
    """Produce stream_decision.json from scored velocity."""
    vel = scored["velocity_score"]
    breadth = vel.get("product_breadth_score", 0)
    overhead = vel.get("machinery_overhead_score", 0)
    floor_met = scored["product_output_floor_met"]
    classification = scored.get("mainstream_classification")
    drift = scored.get("semantic_drift_risk", "low")

    # Determine stream route/decision
    stream_gaps = [g for g in gaps if g.get("stream") == stream]
    external_gate_gaps = [g for g in stream_gaps if g.get("external_gate")]
    actionable_gaps = [g for g in stream_gaps if not g.get("external_gate")]

    formats_targeted = list({g["format"] for g in actionable_gaps})

    if not floor_met and stream == "mainstream":
        decision = "REROUTE_TO_PRODUCT_GAPS"
        routing_note = f"Product output floor not met (breadth={breadth}). Route to: {formats_targeted}"
    elif overhead >= 3 and not any([vel.get("false_pass_prevented"), vel.get("false_stop_prevented"),
                                     vel.get("mainstream_blocker_removed")]):
        decision = "CONTINUE_WITH_LIMITATIONS"
        routing_note = f"High machinery overhead (score={overhead}) without compensating product output."
    elif classification in ("CLEAN_PASS",) and floor_met:
        decision = "CONTINUE"
        routing_note = "Clean product output. Continue."
    elif classification and classification.startswith("PARTIAL"):
        decision = "CONTINUE_WITH_LIMITATIONS"
        routing_note = f"Partial classification: {classification}. Target breadth gaps."
    else:
        decision = "CONTINUE"
        routing_note = "Velocity positive. Continue."

    return {
        "stream": stream,
        "timestamp": scored["timestamp"],
        "decision": decision,
        "routing_note": routing_note,
        "mainstream_classification": classification,
        "product_breadth_score": breadth,
        "machinery_overhead_score": overhead,
        "product_output_floor_met": floor_met,
        "semantic_drift_risk": drift,
        "actionable_gaps_count": len(actionable_gaps),
        "external_gate_gaps_count": len(external_gate_gaps),
        "formats_targeted": formats_targeted,
        "target_families_needed": max(0, 3 - breadth),
    }


def assess_false_pass_stop(scored: dict, replay: dict, stream: str) -> dict:
    """Produce false_pass_false_stop_assessment.json."""
    vel = scored["velocity_score"]
    prior_decision = replay.get("deterministic_verdict", "unknown")
    fp_risk = replay.get("false_pass_risk", "unknown")
    fs_risk = replay.get("false_stop_risk", "unknown")

    # False pass: claimed PASS but product evidence is weak
    breadth = vel.get("product_breadth_score", 0)
    overhead = vel.get("machinery_overhead_score", 0)
    classification = scored.get("mainstream_classification", "")

    false_pass_detected = (
        prior_decision == "ACCEPTED"
        and breadth < 2
        and stream == "mainstream"
        and classification not in ("CLEAN_PASS",)
    )

    # False stop: decision is STOP but product evidence is present
    false_stop_detected = (
        prior_decision in ("REJECTED", "NO_PRODUCT_OUTPUT_FLOOR")
        and breadth > 0
        and vel.get("false_stop_prevented", False)
    )

    actions = []
    if false_pass_detected:
        actions.append(f"Downgrade Mainstream to PARTIAL — breadth={breadth}, classification={classification}")
    if overhead >= 2 and not vel.get("mainstream_blocker_removed"):
        actions.append("Flag high machinery overhead — no compensating blocker removal")
    if not actions:
        actions.append("No false pass or stop detected in this sprint")

    return {
        "stream": stream,
        "timestamp": scored["timestamp"],
        "false_pass_detected": false_pass_detected,
        "false_pass_risk": fp_risk,
        "false_pass_evidence": f"breadth={breadth}, classification={classification}" if false_pass_detected else "none",
        "false_stop_detected": false_stop_detected,
        "false_stop_risk": fs_risk,
        "false_stop_evidence": "none",
        "actions_required": actions,
        "mainstream_safe_to_continue": not false_pass_detected,
        "deterministic_override_applied": false_pass_detected,
    }


def write_velocity_summary(scored: dict, decision: dict, output_dir: Path, stream: str) -> None:
    vel = scored["velocity_score"]
    summary_path = output_dir / "product_velocity_summary.md"

    lines = [
        f"# Product Velocity Summary — {stream.capitalize()}",
        "",
        f"**Sprint:** {scored.get('sprint_id', 'unknown')}",
        f"**Timestamp:** {scored['timestamp']}",
        f"**Stream Decision:** {decision['decision']}",
        "",
        "## 12-Dimension Velocity Score",
        "",
        "| Dimension | Value |",
        "|-----------|-------|",
    ]
    for k, v in vel.items():
        lines.append(f"| {k} | {v} |")

    lines += [
        "",
        "## Stream Assessment",
        "",
        f"- **Mainstream Classification:** {scored.get('mainstream_classification', 'n/a')}",
        f"- **Product Output Floor Met:** {scored.get('product_output_floor_met')}",
        f"- **Semantic Drift Risk:** {scored.get('semantic_drift_risk')}",
        f"- **Routing Note:** {decision['routing_note']}",
        "",
        "## Gap Targets",
        "",
        f"- Actionable gaps: {decision['actionable_gaps_count']}",
        f"- External gate gaps: {decision['external_gate_gaps_count']}",
        f"- Formats targeted: {', '.join(decision['formats_targeted']) if decision['formats_targeted'] else 'none'}",
        f"- Families still needed for CLEAN_PASS: {decision['target_families_needed']}",
    ]

    summary_path.write_text("\n".join(lines), encoding="utf-8")


def run(stream: str, replay_path: Path, gaps_path: Path, output_dir: Path) -> int:
    replay_results = _load_json(replay_path)
    if isinstance(replay_results, list):
        replay = _find_replay(replay_results, stream)
    else:
        replay = replay_results

    gaps_data = _load_json(gaps_path)
    gaps = gaps_data.get("selected_gaps", [])

    scored = score_stream(stream, replay, gaps)
    decision = compute_stream_decision(scored, gaps, stream)
    assessment = assess_false_pass_stop(scored, replay, stream)

    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "product_velocity_score.json").write_text(
        json.dumps(scored, indent=2), encoding="utf-8"
    )
    (output_dir / "stream_decision.json").write_text(
        json.dumps(decision, indent=2), encoding="utf-8"
    )
    (output_dir / "false_pass_false_stop_assessment.json").write_text(
        json.dumps(assessment, indent=2), encoding="utf-8"
    )
    write_velocity_summary(scored, decision, output_dir, stream)

    print(f"Stream: {stream}")
    print(f"Decision: {decision['decision']}")
    print(f"Classification: {scored.get('mainstream_classification', 'n/a')}")
    print(f"Breadth: {scored['velocity_score']['product_breadth_score']}")
    print(f"Overhead: {scored['velocity_score']['machinery_overhead_score']}")
    print(f"Outputs written to: {output_dir}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate stream routing packet from replay results + product gaps."
    )
    parser.add_argument("--stream", default="mainstream",
                        choices=["mainstream", "acceleration", "skills", "supervisor"],
                        help="Stream to score")
    parser.add_argument("--replay-results", type=Path,
                        default=Path("reports/supervisor-product-first/replay-results.json"))
    parser.add_argument("--gaps", type=Path,
                        default=Path(".local/supervisor/selected-product-gaps.json"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("reports/supervisor-product-traffic-controller"))
    args = parser.parse_args()
    sys.exit(run(args.stream, args.replay_results, args.gaps, args.output_dir))


if __name__ == "__main__":
    main()
