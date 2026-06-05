"""
check_cross_stream_consumption.py — Check cross-stream consumption status.

Verifies whether:
  - Mainstream has consumed Skills governed transcripts
  - Mainstream has consumed Acceleration AI outputs
  - Skills stream has produced governed transcripts
  - Acceleration stream has produced AI outputs

Also probes filesystem for actual Skills/Acceleration packets (not just replay results).
Filesystem packets override stale SKILLS_MISSING_PACKET verdicts from old replay data.

Usage:
    python tools/supervisor/check_cross_stream_consumption.py \\
        --replay-results reports/supervisor-product-first/replay-results.json \\
        --output-dir reports/supervisor-product-traffic-controller
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# Known filesystem locations for Skills and Acceleration packets
_SKILLS_PACKET_PATHS = [
    "reports/skills-product-first/mainstream-consumption-packet.json",
    "reports/skills-product-first/handoff-to-mainstream.json",
]
_ACCELERATION_PACKET_DIRS = [
    "reports/acceleration-product-first/mainstream-consumption-packets",
]


def _load_json(path: Path) -> Any:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def probe_skills_packet(repo_root: Path | None = None) -> dict:
    """Probe filesystem for Skills consumption packet.

    Returns dict with found=True/False, paths found, and parsed packet summary.
    """
    root = repo_root or Path(".")
    found_paths = []
    packet_content = None
    for rel in _SKILLS_PACKET_PATHS:
        p = root / rel
        if p.exists():
            found_paths.append(str(p))
            if packet_content is None:
                try:
                    packet_content = _load_json(p)
                except Exception:
                    pass

    coverage_scope = None
    if packet_content and isinstance(packet_content, dict):
        # Extract coverage scope from known fields
        gap = packet_content.get("selected_product_gap", {})
        coverage_scope = gap.get("capability", gap.get("format_id", "unknown"))

    return {
        "found": len(found_paths) > 0,
        "paths": found_paths,
        "coverage_scope": coverage_scope,
        "packet_valid": packet_content is not None,
    }


def probe_acceleration_packets(repo_root: Path | None = None) -> dict:
    """Probe filesystem for Acceleration consumption packets.

    Returns dict with found=True/False, packet count, and paths.
    """
    root = repo_root or Path(".")
    found_paths = []
    valid_count = 0
    for rel_dir in _ACCELERATION_PACKET_DIRS:
        d = root / rel_dir
        if d.exists() and d.is_dir():
            for f in d.glob("*.json"):
                try:
                    _load_json(f)
                    found_paths.append(str(f))
                    valid_count += 1
                except Exception:
                    pass

    return {
        "found": valid_count > 0,
        "paths": found_paths,
        "valid_packet_count": valid_count,
    }


def _find_replay(replay_results: list[dict], stream: str) -> dict:
    for entry in replay_results:
        if entry.get("stream") == stream:
            return entry
    return {}


def check_skills_consumption(
    mainstream_replay: dict, skills_replay: dict,
    skills_packet_probe: dict | None = None,
) -> dict:
    """Check if Skills governed transcripts are produced and consumed by Mainstream.

    skills_packet_probe: result of probe_skills_packet(). If the packet exists
    on disk, SKILLS_MISSING_PACKET is suppressed and coverage scope is reported.
    """
    skills_overhead = skills_replay.get("product_velocity_score", {}).get("machinery_overhead_score", 0)
    skills_breadth = skills_replay.get("product_velocity_score", {}).get("product_breadth_score", 0)
    mainstream_skills_consumption = mainstream_replay.get("skills_consumption", "not_consumed")

    # Skills stream produced governed transcripts (from replay)?
    skills_produced_replay = skills_breadth > 0

    # Skills packet present on filesystem (overrides stale replay data)?
    packet_on_disk = skills_packet_probe is not None and skills_packet_probe.get("found", False)
    skills_produced = skills_produced_replay or packet_on_disk

    # Mainstream consumed them?
    mainstream_consumed = mainstream_skills_consumption == "consumed"

    flags = []
    if not skills_produced:
        flags.append("SKILLS_NO_PRODUCT_OUTPUT")
    # Only emit SKILLS_MISSING_PACKET if packet is NOT on disk
    if skills_overhead >= 2 and not mainstream_consumed and not packet_on_disk:
        flags.append("SKILLS_MISSING_PACKET")
    if not mainstream_consumed:
        flags.append("MAINSTREAM_NOT_CONSUMING_SKILLS")

    # Classify coverage scope when packet is present
    coverage_scope = None
    packet_paths = []
    if skills_packet_probe:
        coverage_scope = skills_packet_probe.get("coverage_scope")
        packet_paths = skills_packet_probe.get("paths", [])

    verdict_base = "SKILLS_CONSUMPTION_GAP" if flags else "SKILLS_CONSUMPTION_OK"
    if packet_on_disk and not mainstream_consumed:
        # Packet exists but Mainstream hasn't declared consumption yet
        verdict_base = "SKILLS_CONSUMABLE_NOT_YET_CONSUMED"

    return {
        "status": "consumed" if mainstream_consumed else "not_consumed",
        "skills_overhead_score": skills_overhead,
        "skills_breadth_score": skills_breadth,
        "mainstream_consumption_declared": mainstream_skills_consumption,
        "packet_on_disk": packet_on_disk,
        "packet_paths": packet_paths,
        "coverage_scope": coverage_scope,
        "flags": flags,
        "verdict": verdict_base,
        "action_required": not mainstream_consumed,
        "recommended_action": (
            "Skills packet present on disk. Mainstream must declare governed_execution_consumed=true"
            if packet_on_disk and not mainstream_consumed
            else "Skills must produce governed transcripts AND Mainstream must declare governed_execution_consumed=true"
            if not mainstream_consumed else "No action required"
        ),
    }


def check_acceleration_consumption(
    mainstream_replay: dict, acceleration_replay: dict,
    acc_packet_probe: dict | None = None,
) -> dict:
    """Check if Acceleration AI outputs are produced and consumed by Mainstream.

    acc_packet_probe: result of probe_acceleration_packets(). If packets exist
    on disk, classifies as ACCELERATION_CONSUMABLE_PARTIAL when not yet consumed.
    """
    acc_breadth = acceleration_replay.get("product_velocity_score", {}).get("product_breadth_score", 0)
    mainstream_acc_consumption = mainstream_replay.get("acceleration_consumption", "not_consumed")
    ai_output_status = acceleration_replay.get("ai_output_status", "no_ai")

    # Acceleration produced AI outputs (from replay)?
    ai_produced_replay = ai_output_status in ("ai_draft", "ai_reviewed")

    # Acceleration packets present on filesystem?
    packets_on_disk = acc_packet_probe is not None and acc_packet_probe.get("found", False)
    valid_count = acc_packet_probe.get("valid_packet_count", 0) if acc_packet_probe else 0

    # Mainstream consumed them?
    mainstream_consumed = mainstream_acc_consumption == "consumed"

    flags = []
    if not ai_produced_replay and not packets_on_disk:
        flags.append("ACCELERATION_NO_AI_OUTPUT")
    if not mainstream_consumed:
        flags.append("MAINSTREAM_NOT_CONSUMING_ACCELERATION")

    # Verdict classification
    if mainstream_consumed:
        verdict = "ACCELERATION_CONSUMPTION_OK"
    elif packets_on_disk and valid_count >= 3:
        verdict = "ACCELERATION_CONSUMABLE_PARTIAL"
    elif packets_on_disk:
        verdict = "ACCELERATION_CONSUMABLE_PARTIAL"
    else:
        verdict = "ACCELERATION_CONSUMPTION_GAP"

    packet_paths = acc_packet_probe.get("paths", []) if acc_packet_probe else []

    return {
        "status": "consumed" if mainstream_consumed else "not_consumed",
        "acceleration_breadth_score": acc_breadth,
        "acceleration_ai_output_status": ai_output_status,
        "mainstream_consumption_declared": mainstream_acc_consumption,
        "packets_on_disk": packets_on_disk,
        "valid_packet_count": valid_count,
        "packet_paths": packet_paths,
        "flags": flags,
        "verdict": verdict,
        "action_required": not mainstream_consumed,
        "recommended_action": (
            f"Acceleration has {valid_count} packets on disk. Mainstream must declare reusable_accelerator_consumed=true"
            if packets_on_disk and not mainstream_consumed
            else "Acceleration must produce ai_draft outputs AND Mainstream must declare reusable_accelerator_consumed=true"
            if not mainstream_consumed else "No action required"
        ),
        "ai_authority_note": "All Acceleration outputs are ai_draft — non-authoritative. Requires deterministic validation.",
    }


def run(replay_path: Path, output_dir: Path, repo_root: Path | None = None) -> int:
    replay_results = _load_json(replay_path)
    if not isinstance(replay_results, list):
        print(f"ERROR: replay results must be a list, got {type(replay_results)}", file=sys.stderr)
        return 1

    mainstream_replay = _find_replay(replay_results, "mainstream")
    skills_replay = _find_replay(replay_results, "skills")
    acceleration_replay = _find_replay(replay_results, "acceleration")

    # Probe filesystem for current packets (overrides stale replay verdicts)
    root = repo_root or Path(".")
    skills_probe = probe_skills_packet(root)
    acc_probe = probe_acceleration_packets(root)

    skills_status = check_skills_consumption(mainstream_replay, skills_replay, skills_probe)
    acceleration_status = check_acceleration_consumption(mainstream_replay, acceleration_replay, acc_probe)

    timestamp = datetime.now(timezone.utc).isoformat()
    overall = {
        "timestamp": timestamp,
        "mainstream_sprint": mainstream_replay.get("sprint_id", "unknown"),
        "skills_sprint": skills_replay.get("sprint_id", "unknown"),
        "acceleration_sprint": acceleration_replay.get("sprint_id", "unknown"),
        "skills": skills_status,
        "acceleration": acceleration_status,
        "overall_verdict": (
            "CROSS_STREAM_CONSUMPTION_GAPS_DETECTED"
            if (skills_status["action_required"] or acceleration_status["action_required"])
            else "CROSS_STREAM_CONSUMPTION_OK"
        ),
        "all_flags": skills_status["flags"] + acceleration_status["flags"],
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "cross-stream-consumption-status.json").write_text(
        json.dumps(overall, indent=2), encoding="utf-8"
    )

    print(f"Skills consumption: {skills_status['verdict']}")
    print(f"  packet_on_disk: {skills_status.get('packet_on_disk')}")
    print(f"Acceleration consumption: {acceleration_status['verdict']}")
    print(f"  packets_on_disk: {acceleration_status.get('packets_on_disk')}, count={acceleration_status.get('valid_packet_count')}")
    print(f"Overall: {overall['overall_verdict']}")
    print(f"Flags: {overall['all_flags']}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Check cross-stream consumption status."
    )
    parser.add_argument("--replay-results", type=Path,
                        default=Path("reports/supervisor-product-first/replay-results.json"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("reports/supervisor-product-traffic-controller"))
    parser.add_argument("--repo-root", type=Path, default=None,
                        help="Repo root for filesystem packet probing (default: CWD)")
    args = parser.parse_args()
    sys.exit(run(args.replay_results, args.output_dir, args.repo_root))


if __name__ == "__main__":
    main()
