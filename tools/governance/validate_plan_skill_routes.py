#!/usr/bin/env python3
"""
validate_plan_skill_routes.py — EP-009: Plan Skill Route Validation (FF-SGOV-001 TC-SGOV-W2-004)

Validates that plan taskcards reference registered skill_ids from .supervisor/skill-registry.yaml.
Reads plan markdown or YAML files; extracts skill_ids from taskcard blocks; validates each against
the active skill registry.

Exit codes:
  0 — PASS (all found skill_ids are registered, or no skill_ids declared)
  1 — INVALID_ROUTES (at least one skill_id is UNREGISTERED or EMPTY)
  2 — CONFIG_ERROR (registry unreadable, plan file not found)

Usage:
  python tools/governance/validate_plan_skill_routes.py <plan_path>
  python tools/governance/validate_plan_skill_routes.py plans/.claude/imperative-floating-book.md
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_REGISTRY_PATH = _REPO / ".supervisor" / "skill-registry.yaml"


def load_active_skill_ids(registry_path: Path) -> set[str]:
    """Return set of skill_id strings where status=active from skill-registry.yaml."""
    try:
        import yaml  # type: ignore
    except ImportError:
        raise ImportError("PyYAML is required: pip install pyyaml")

    data = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
    skills_list = data.get("skills", [])
    active = set()
    for skill in skills_list:
        if isinstance(skill, dict) and skill.get("status") == "active":
            sid = skill.get("skill_id") or skill.get("id")
            if sid:
                active.add(str(sid))
    return active


def extract_skill_ids_from_plan(plan_path: Path) -> dict[str, list[str]]:
    """Extract skill_ids per taskcard from a markdown or YAML plan file.

    Returns a dict of {context_label: [skill_id, ...]} where context_label is the
    surrounding TC-ID or a line-number marker.

    Recognizes these patterns in the file:
      skill_ids: [foo, bar]
      skill_ids:
        - foo
        - bar
    """
    text = plan_path.read_text(encoding="utf-8", errors="replace")
    results: dict[str, list[str]] = {}

    # Inline list: skill_ids: [foo, bar, baz]
    inline_pattern = re.compile(r"skill_ids\s*:\s*\[([^\]]+)\]", re.IGNORECASE)
    # YAML block list: skill_ids:\n  - foo\n  - bar
    block_start = re.compile(r"skill_ids\s*:\s*$", re.IGNORECASE | re.MULTILINE)

    # Find enclosing TC-ID for context (look backwards for nearest TC-* pattern)
    tc_pattern = re.compile(r"TC-[A-Z0-9_-]+", re.IGNORECASE)

    lines = text.splitlines()

    def nearest_tc(line_idx: int) -> str:
        """Find nearest TC-ID at or before line_idx."""
        for i in range(line_idx, max(-1, line_idx - 30), -1):
            m = tc_pattern.search(lines[i])
            if m:
                return m.group(0)
        return f"line_{line_idx + 1}"

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Inline list pattern
        m = inline_pattern.search(stripped)
        if m:
            raw = m.group(1)
            ids = [s.strip().strip("'\"") for s in raw.split(",") if s.strip()]
            label = nearest_tc(i)
            results.setdefault(label, []).extend(ids)
            continue

        # Block list pattern
        if block_start.search(stripped):
            block_ids = []
            j = i + 1
            while j < len(lines):
                next_stripped = lines[j].strip()
                if next_stripped.startswith("- "):
                    sid = next_stripped[2:].strip().strip("'\"")
                    if sid:
                        block_ids.append(sid)
                    j += 1
                elif next_stripped == "" or next_stripped.startswith("#"):
                    j += 1
                    continue
                else:
                    break
            if block_ids:
                label = nearest_tc(i)
                results.setdefault(label, []).extend(block_ids)

    return results


def validate(plan_path: Path, registry_path: Path) -> dict:
    """Validate plan skill routes against registry. Returns result dict."""
    if not plan_path.exists():
        return {
            "verdict": "CONFIG_ERROR",
            "error": f"Plan file not found: {plan_path}",
            "findings": [],
        }

    if not registry_path.exists():
        return {
            "verdict": "CONFIG_ERROR",
            "error": f"Skill registry not found: {registry_path}",
            "findings": [],
        }

    try:
        active_ids = load_active_skill_ids(registry_path)
    except Exception as exc:
        return {
            "verdict": "CONFIG_ERROR",
            "error": f"Registry load error: {exc}",
            "findings": [],
        }

    skill_map = extract_skill_ids_from_plan(plan_path)
    findings = []
    has_error = False

    if not skill_map:
        findings.append({
            "context": "plan",
            "verdict": "NO_SKILL_IDS_DECLARED",
            "note": "No skill_ids found in plan. Consider adding skill routing to taskcards.",
        })
        # No declarations is a WARN, not an error
    else:
        for context, ids in sorted(skill_map.items()):
            if not ids:
                findings.append({
                    "context": context,
                    "skill_ids": [],
                    "verdict": "EMPTY",
                    "note": "skill_ids list is empty",
                })
                has_error = True
            else:
                for sid in ids:
                    if sid in active_ids:
                        findings.append({
                            "context": context,
                            "skill_id": sid,
                            "verdict": "PASS",
                        })
                    else:
                        findings.append({
                            "context": context,
                            "skill_id": sid,
                            "verdict": "UNREGISTERED",
                            "note": f"'{sid}' not found in active skills ({len(active_ids)} active)",
                        })
                        has_error = True

    verdict = "INVALID_ROUTES" if has_error else "PASS"
    return {
        "verdict": verdict,
        "plan_path": str(plan_path),
        "active_skill_count": len(active_ids),
        "skill_declarations_found": len(skill_map),
        "findings": findings,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate plan taskcard skill routes against the skill registry (EP-009)"
    )
    parser.add_argument("plan", type=Path, help="Path to plan markdown or YAML file")
    parser.add_argument(
        "--registry", type=Path, default=_REGISTRY_PATH,
        help=f"Path to skill-registry.yaml (default: {_REGISTRY_PATH})"
    )
    args = parser.parse_args(argv)

    plan_path = args.plan if args.plan.is_absolute() else Path.cwd() / args.plan
    result = validate(plan_path, args.registry)

    print(json.dumps(result, indent=2))

    verdict = result["verdict"]
    if verdict == "PASS":
        print("\nVALIDATION: PASS")
        return 0
    elif verdict == "CONFIG_ERROR":
        print(f"\nVALIDATION: CONFIG_ERROR — {result.get('error', '')}")
        return 2
    else:
        errors = [f for f in result["findings"] if f.get("verdict") in ("EMPTY", "UNREGISTERED")]
        print(f"\nVALIDATION: INVALID_ROUTES ({len(errors)} issue(s))")
        return 1


if __name__ == "__main__":
    sys.exit(main())
