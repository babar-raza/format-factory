"""
generate_stream_gaps.py — Fresh gap generation for all 4 streams.

Generates gaps from stream-appropriate sources:
- mainstream: POC matrix (product capabilities)
- acceleration: tool inventory (tools needing improvement)
- skills: skill registry (unregistered/draft skills)
- supervisor: pipeline state (missing validators, self-containment)

Fixes D103-03 (stale gaps) and D103-04 (0 acceleration gaps).
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_MATRIX = REPO_ROOT / "product-capability-matrix" / "poc-targets.yaml"
DEFAULT_SKILL_REGISTRY = REPO_ROOT / ".supervisor" / "skill-registry.yaml"

STREAMS = ("mainstream", "acceleration", "skills", "supervisor")

# Tools that should exist in the acceleration pipeline
EXPECTED_ACCELERATION_TOOLS = [
    "select_poc_gaps.py",
    "choose_skill_or_handoff.py",
    "generate_execution_handoff.py",
    "record_lane_execution.py",
    "generate_sprint_learning.py",
    "package_install_proof.py",
    "detect_product_progress.py",
    "materialize_and_review.py",
    "next_best_action.py",
    "stream_forecaster.py",
    "anti_skip_checker.py",
    "stream_prompt_generator.py",
    "generate_stream_gaps.py",
    "build_declaration_review_package.py",
    "build_context_pack.py",
]

# Pipeline validators expected for supervisor stream
EXPECTED_SUPERVISOR_FEATURES = [
    "evidence-manifest in review package",
    "acceleration report packaging",
    "raw log packaging",
    "sample output packaging",
    "lane ledger packaging",
    "cross-stream prompt contamination detection",
    "evidence self-containment validation",
]


def _gap_id(stream: str, source: str, name: str) -> str:
    return f"{stream}-{source}-{name}".lower().replace(".", "-").replace("_", "-").replace(" ", "-")


def generate_mainstream_gaps(
    matrix: dict[str, Any],
) -> list[dict[str, Any]]:
    """Extract remaining product gaps from POC matrix."""
    gaps = []
    gap_statuses = {
        "GAP_DOGFOOD_EXTERNAL", "NOT_IMPLEMENTED", "NOT_STARTED",
        "NOT_YET", "PARTIAL", "R85_TARGET",
    }

    for track_key, track_label in [
        ("commercial_net_products", "commercial_net"),
        ("foss_reduced_products", "foss_reduced"),
    ]:
        for product in matrix.get(track_key, []):
            fmt = product.get("format", "unknown")
            # Walk all status fields
            for section_key in ["dotnet_status", "python_foss_status", "python_status", "dogfood_status"]:
                section = product.get(section_key, {})
                if not isinstance(section, dict):
                    continue
                for cap, status in section.items():
                    status_str = str(status)
                    if status_str in gap_statuses:
                        gaps.append({
                            "stream": "mainstream",
                            "gap_id": _gap_id("mainstream", fmt, f"{section_key}-{cap}"),
                            "format": fmt,
                            "product_track": track_label,
                            "capability": f"{section_key}.{cap}",
                            "current_status": status_str,
                            "description": f"{fmt} {section_key}.{cap} is {status_str}",
                            "priority": 80 if "dogfood" in section_key else 60,
                        })
    return gaps


def generate_acceleration_gaps(
    tool_dir: Path | None = None,
    test_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Generate gaps from acceleration tool inventory."""
    tool_dir = tool_dir or (REPO_ROOT / "tools" / "supervisor")
    test_dir = test_dir or (REPO_ROOT / "tests" / "supervisor" / "acceleration")
    gaps = []

    for tool_name in EXPECTED_ACCELERATION_TOOLS:
        tool_path = tool_dir / tool_name
        exists = tool_path.exists() if tool_dir.exists() else False

        # Check for matching test
        test_name = f"test_{tool_name.replace('.py', '')}.py"
        test_path = test_dir / test_name
        has_test = test_path.exists() if test_dir.exists() else False

        if not exists:
            gaps.append({
                "stream": "acceleration",
                "gap_id": _gap_id("acceleration", "tool", f"missing-{tool_name}"),
                "tool": tool_name,
                "current_status": "NOT_IMPLEMENTED",
                "description": f"Tool {tool_name} does not exist",
                "priority": 100,
            })
        elif not has_test:
            gaps.append({
                "stream": "acceleration",
                "gap_id": _gap_id("acceleration", "tool", f"untested-{tool_name}"),
                "tool": tool_name,
                "current_status": "PARTIAL",
                "description": f"Tool {tool_name} exists but has no dedicated test file",
                "priority": 70,
            })

    # Check for evidence self-containment gaps
    gaps.append({
        "stream": "acceleration",
        "gap_id": _gap_id("acceleration", "integration", "review-package-evidence-inclusion"),
        "tool": "build_declaration_review_package.py",
        "current_status": "GAP",
        "description": "Review package does not include acceleration evidence artifacts (reports, sample outputs, raw logs)",
        "priority": 90,
    })

    gaps.append({
        "stream": "acceleration",
        "gap_id": _gap_id("acceleration", "integration", "evidence-manifest-colocation"),
        "tool": "evidence-manifest.yaml",
        "current_status": "GAP",
        "description": "Evidence manifest not co-located with declaration for review package builder",
        "priority": 85,
    })

    return gaps


def generate_skills_gaps(
    skill_registry: dict[str, Any] | None = None,
    tool_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """Generate gaps from skill registry (draft/unregistered tools)."""
    gaps = []
    tool_dir = tool_dir or (REPO_ROOT / "tools" / "supervisor")

    if not skill_registry:
        gaps.append({
            "stream": "skills",
            "gap_id": _gap_id("skills", "registry", "missing-registry"),
            "current_status": "NOT_FOUND",
            "description": "Skill registry not found or empty",
            "priority": 100,
        })
        return gaps

    skills = skill_registry.get("skills", [])
    registered_commands = {s.get("command", "").lstrip("/") for s in skills}

    # Check for new tools not yet registered as skills
    acceleration_tools = [
        "next_best_action", "stream_forecaster", "anti_skip_checker",
        "stream_prompt_generator", "generate_stream_gaps",
    ]
    for tool in acceleration_tools:
        cmd = tool.replace("_", "-")
        if cmd not in registered_commands:
            gaps.append({
                "stream": "skills",
                "gap_id": _gap_id("skills", "registry", f"unregistered-{tool}"),
                "tool": f"{tool}.py",
                "current_status": "NOT_REGISTERED",
                "description": f"Tool {tool}.py is not registered as a governed skill",
                "priority": 60,
            })

    # Check for draft skills
    for skill in skills:
        if skill.get("status") == "draft":
            gaps.append({
                "stream": "skills",
                "gap_id": _gap_id("skills", "registry", f"draft-{skill.get('skill_id', 'unknown')}"),
                "skill_id": skill.get("skill_id"),
                "current_status": "DRAFT",
                "description": f"Skill {skill.get('skill_id')} is in draft status",
                "priority": 50,
            })

    return gaps


def generate_supervisor_gaps() -> list[dict[str, Any]]:
    """Generate gaps from supervisor pipeline state."""
    gaps = []

    for feature in EXPECTED_SUPERVISOR_FEATURES:
        gaps.append({
            "stream": "supervisor",
            "gap_id": _gap_id("supervisor", "pipeline", feature),
            "current_status": "GAP",
            "description": f"Supervisor pipeline missing: {feature}",
            "priority": 70,
        })

    return gaps


def generate_all_stream_gaps(
    matrix: dict[str, Any] | None = None,
    skill_registry: dict[str, Any] | None = None,
    tool_dir: Path | None = None,
    test_dir: Path | None = None,
    sprint_id: str = "unknown",
) -> dict[str, Any]:
    """Generate fresh gaps for all 4 streams."""
    mainstream = generate_mainstream_gaps(matrix or {})
    acceleration = generate_acceleration_gaps(tool_dir, test_dir)
    skills = generate_skills_gaps(skill_registry, tool_dir)
    supervisor = generate_supervisor_gaps()

    all_gaps = mainstream + acceleration + skills + supervisor

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sprint_id": sprint_id,
        "is_stale": False,
        "total_gaps": len(all_gaps),
        "streams": {
            "mainstream": len(mainstream),
            "acceleration": len(acceleration),
            "skills": len(skills),
            "supervisor": len(supervisor),
        },
        "gaps": all_gaps,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Generate fresh gaps for all 4 streams")
    parser.add_argument("--matrix", type=Path, default=DEFAULT_MATRIX)
    parser.add_argument("--skill-registry", type=Path, default=DEFAULT_SKILL_REGISTRY)
    parser.add_argument("--sprint-id", default="unknown")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    matrix = yaml.safe_load(args.matrix.read_text(encoding="utf-8")) if args.matrix.exists() else {}
    registry = yaml.safe_load(args.skill_registry.read_text(encoding="utf-8")) if args.skill_registry.exists() else None

    payload = generate_all_stream_gaps(
        matrix=matrix,
        skill_registry=registry,
        sprint_id=args.sprint_id,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"OUTPUT: {args.output}")
    else:
        print(json.dumps(payload, indent=2))

    print(f"TOTAL_GAPS: {payload['total_gaps']}")
    print(f"STREAMS: {payload['streams']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
