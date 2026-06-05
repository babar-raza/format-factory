"""Classify a product gap for governed skill execution, handoff, or escalation.

v2 improvements (R99):
- Reads skill registry YAML for dynamic skill matching
- Adds NEED_PLAN_HARDENING and READ_ONLY_VERIFY decisions
- Matches against registered skill capability paths

v3 improvements (R100):
- Work-type classification (8 types) via classify_work_type()
- work_type field added to decision output
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_SKILL_REGISTRY = REPO_ROOT / ".supervisor" / "skill-registry.yaml"

EXTERNAL_GATE_TERMS = (
    "approval",
    "babar raza",
    "credential",
    "gate 8",
    "gate 11",
    "gate_11",
    "g11-g",
    "g11g",
    "publish",
    "push",
)

SKILL_RULES = (
    (
        "dogfood-export",
        ("dogfood", "export"),
        "governed-dogfood-export",
    ),
    (
        "dependency-resolution",
        ("dependency", "offline resolution"),
        "governed-dependency-resolution-review",
    ),
    (
        "capability-implementation",
        ("writer not implemented", "write_ppm"),
        "governed-product-capability-implementation",
    ),
    (
        "installed-workflow",
        ("installed_workflow", "installed workflow", "self-contained install"),
        "governed-installed-workflow-verification",
    ),
    (
        "package-proof",
        ("package", "wheel", "pip install", "sdist"),
        "governed-package-proof",
    ),
)

# Work-type classification (R100): maps a gap to its expected work type
WORK_TYPE_RULES = (
    ("product_source_change", ("save", "write", "edit", "add", "remove", "set", "create")),
    ("test_only_change", ("test", "roundtrip", "regression", "hardening")),
    ("docs_examples", ("example", "documentation", "readme", "usage")),
    ("package_proof", ("package", "wheel", "install", "pip", "sdist")),
    ("dogfood_export", ("dogfood", "export", "convert")),
    ("supervisor_tooling", ("supervisor", "tooling", "automation", "acceleration")),
    ("external_gate", ("gate 11", "gate 8", "approval", "publish", "credential")),
    ("dry_run_proof", ("dry-run", "dry_run", "simulation", "proof")),
)

READ_ONLY_PATTERNS = (
    "installed_workflow",
    "installed workflow",
    "verify",
    "check",
    "inspect",
)

PLAN_HARDENING_PATTERNS = (
    "new file",
    "create new",
    "restructure",
    "migrate",
    "refactor",
)

UNSAFE_SCOPE_PATTERNS = (
    "all formats",
    "every format",
    "global refactor",
    "cross-product",
    "bulk rename",
    "delete all",
)


def classify_work_type(gap: dict[str, Any]) -> str:
    """Classify a gap into one of 8 work types based on keyword matching."""
    text = _gap_text(gap)
    for work_type, keywords in WORK_TYPE_RULES:
        if any(kw in text for kw in keywords):
            return work_type
    return "unknown"


def classify_source_track(gap: dict[str, Any]) -> str:
    """Classify gap as commercial_dotnet, foss_python, or unknown."""
    track = gap.get("product_track", "")
    if "commercial" in track or "net" in track.lower():
        return "commercial_dotnet"
    if "foss" in track or "python" in track.lower() or "reduced" in track:
        return "foss_python"
    return "unknown"


def _gap_text(gap: dict[str, Any]) -> str:
    values = (
        gap.get("capability_path", ""),
        gap.get("description", ""),
        gap.get("current_status", ""),
    )
    return " ".join(str(value).lower() for value in values)


def _match_skill_registry(
    gap_text: str,
    skill_registry: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Try to match a gap to a registered skill from the skill registry."""
    if not skill_registry:
        return None
    skills = skill_registry.get("skills", [])
    for skill in skills:
        if skill.get("status") != "active":
            continue
        skill_id = skill.get("skill_id", "")
        purpose = (skill.get("purpose", "") or "").lower()
        purpose_words = set(purpose.split())
        gap_words = set(gap_text.split())
        overlap = purpose_words & gap_words
        if len(overlap) >= 3:
            return {
                "skill_id": skill_id,
                "command": skill.get("command"),
                "product_track": skill.get("product_track"),
            }
    return None


def choose_skill_or_handoff(
    gap: dict[str, Any],
    skill_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a deterministic governed execution decision for one normalized gap."""
    text = _gap_text(gap)
    work_type = classify_work_type(gap)
    source_track = classify_source_track(gap)

    if any(p in text for p in UNSAFE_SCOPE_PATTERNS):
        return {
            "decision": "UNSAFE_SCOPE",
            "governed_skill": None,
            "handoff_required": True,
            "external_gate": False,
            "work_type": work_type,
            "source_track": source_track,
            "reason": "Gap scope is too broad for governed execution.",
        }

    if any(term in text for term in EXTERNAL_GATE_TERMS):
        return {
            "decision": "EXTERNAL_GATE_ESCALATION",
            "governed_skill": None,
            "handoff_required": True,
            "external_gate": True,
            "work_type": work_type,
            "source_track": source_track,
            "reason": "The gap requires human authority or an external action.",
        }

    for category, terms, skill in SKILL_RULES:
        if any(term in text for term in terms):
            if any(p in text for p in PLAN_HARDENING_PATTERNS):
                return {
                    "decision": "NEED_PLAN_HARDENING",
                    "governed_skill": skill,
                    "handoff_required": True,
                    "external_gate": False,
                    "work_type": work_type,
                    "source_track": source_track,
                    "reason": f"High-risk {category} work needs plan hardening before execution.",
                }
            return {
                "decision": "GOVERNED_SKILL_REQUIRED",
                "governed_skill": skill,
                "handoff_required": False,
                "external_gate": False,
                "work_type": work_type,
                "source_track": source_track,
                "reason": f"Repeatable {category} work must run through a governed skill.",
            }

    registry_match = _match_skill_registry(text, skill_registry)
    if registry_match:
        return {
            "decision": "GOVERNED_SKILL_REQUIRED",
            "governed_skill": registry_match["skill_id"],
            "handoff_required": False,
            "external_gate": False,
            "work_type": work_type,
            "source_track": source_track,
            "reason": f"Matched registered skill '{registry_match['skill_id']}' from skill registry.",
        }

    if any(p in text for p in READ_ONLY_PATTERNS):
        return {
            "decision": "READ_ONLY_VERIFY",
            "governed_skill": None,
            "handoff_required": False,
            "external_gate": False,
            "work_type": work_type,
            "source_track": source_track,
            "reason": "Gap can be verified through read-only checks without source edits.",
        }

    return {
        "decision": "GOVERNED_HANDOFF_REQUIRED",
        "governed_skill": None,
        "handoff_required": True,
        "external_gate": False,
        "work_type": work_type,
        "source_track": source_track,
        "reason": "No governed skill rule covers this product gap.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Choose governed skill execution or handoff for a normalized product gap."
    )
    parser.add_argument("--gap-json", type=Path, required=True)
    parser.add_argument("--skill-registry", type=Path, default=None)
    args = parser.parse_args()
    gap = json.loads(args.gap_json.read_text(encoding="utf-8"))
    registry = None
    registry_path = args.skill_registry or DEFAULT_SKILL_REGISTRY
    if registry_path.exists():
        registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    result = choose_skill_or_handoff(gap, skill_registry=registry)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
