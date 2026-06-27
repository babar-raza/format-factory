"""
detect_drift.py — Capability Sync Tool 6/7

Read-only drift detector. Compares committed .governance/capabilities/registry.yaml
and the CAPABILITY-INDEX/CAPABILITY-DISCOVERY sections in CLAUDE.md and AGENTS.md
against a freshly computed in-memory snapshot.

Exit 0 if no drift. Exit 1 if any drift detected.
Never writes any repo files.
"""
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_REPO = Path(__file__).resolve().parent.parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_REGISTRY_PATH = _REPO / ".governance" / "capabilities" / "registry.yaml"
_CLAUDE_MD = _REPO / "CLAUDE.md"
_AGENTS_MD = _REPO / "AGENTS.md"

_CLAUDE_BEGIN_PREFIX = "<!-- BEGIN:CAPABILITY-INDEX"
_CLAUDE_END_MARKER = "<!-- END:CAPABILITY-INDEX -->"
_AGENTS_BEGIN_PREFIX = "<!-- BEGIN:CAPABILITY-DISCOVERY"
_AGENTS_END_MARKER = "<!-- END:CAPABILITY-DISCOVERY -->"


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text(encoding="utf-8", errors="replace")) or {}


def _strip_ts(text: str) -> str:
    """Strip timestamp attributes from BEGIN markers so they don't affect hash."""
    return re.sub(r'generated=[^\s>]+', 'generated=STRIPPED', text)


def _canonicalize_registry(data) -> str:
    """Canonical string for registry comparison (strips generated_at timestamps).
    Accepts either a list (from build_registry) or a dict (from saved registry file).
    """
    if isinstance(data, list):
        caps = data
    else:
        caps = data.get("capabilities", [])
    _SKIP = {"generated_at", "source_skill_registry_version"}
    stripped_caps = sorted(
        [{k: v for k, v in cap.items() if k not in _SKIP} for cap in caps],
        key=lambda c: c.get("capability_id", "")
    )
    return yaml.dump({"capabilities": stripped_caps},
                     default_flow_style=False, allow_unicode=True, sort_keys=True)


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_section(content: str, begin_prefix: str, end_marker: str) -> str | None:
    """Extract content between BEGIN and END markers (exclusive). Returns None if absent."""
    lines = content.splitlines(keepends=True)
    begin_idx = None
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n").rstrip("\r")
        if begin_prefix in stripped:
            begin_idx = i
        elif end_marker in stripped and begin_idx is not None:
            return "".join(lines[begin_idx: i + 1])
    return None


def check_registry_drift() -> dict:
    """Re-compute registry in-memory; compare against committed file."""
    from tools.capability_sync.inventory_capabilities import (
        build_registry, load_commands, load_routing, load_skills, merge_with_prior,
    )
    if not _REGISTRY_PATH.exists():
        return {"drifted": True, "component": "registry", "reason": "registry file missing"}

    committed = _load(_REGISTRY_PATH)
    skills = load_skills()
    commands, md_stems = load_commands()
    routing = load_routing()
    fresh_list = build_registry(skills, commands, md_stems, routing,
                                timestamp="STRIPPED", registry_id="drift-check")
    # Apply merge_with_prior against committed (same as inventory main does)
    fresh_list = merge_with_prior(fresh_list, _REGISTRY_PATH)
    fresh_list.sort(key=lambda c: c["capability_id"])
    fresh = fresh_list

    committed_hash = _hash(_canonicalize_registry(committed))
    fresh_hash = _hash(_canonicalize_registry(fresh))

    if committed_hash == fresh_hash:
        return {"drifted": False, "component": "registry"}
    return {
        "drifted": True,
        "component": "registry",
        "reason": "committed registry differs from freshly computed inventory",
        "committed_hash": committed_hash,
        "fresh_hash": fresh_hash,
    }


def check_claude_drift() -> dict:
    """Re-generate CLAUDE.md section; compare against committed section."""
    from tools.capability_sync.generate_discovery_indexes import generate_claude_index

    if not _REGISTRY_PATH.exists():
        return {"drifted": True, "component": "claude_md", "reason": "registry file missing"}
    if not _CLAUDE_MD.exists():
        return {"drifted": True, "component": "claude_md", "reason": "CLAUDE.md missing"}

    registry = _load(_REGISTRY_PATH)
    expected_block = generate_claude_index(registry, "STRIPPED")
    actual_content = _CLAUDE_MD.read_text(encoding="utf-8")
    actual_section = _extract_section(actual_content, _CLAUDE_BEGIN_PREFIX, _CLAUDE_END_MARKER)

    if actual_section is None:
        return {"drifted": True, "component": "claude_md", "reason": "BEGIN:CAPABILITY-INDEX marker absent"}

    if _hash(_strip_ts(expected_block).rstrip()) == _hash(_strip_ts(actual_section).rstrip()):
        return {"drifted": False, "component": "claude_md"}
    return {
        "drifted": True,
        "component": "claude_md",
        "reason": "CAPABILITY-INDEX section in CLAUDE.md differs from freshly generated content",
    }


def check_agents_drift() -> dict:
    """Re-generate AGENTS.md section; compare against committed section."""
    from tools.capability_sync.generate_discovery_indexes import generate_agents_index

    if not _REGISTRY_PATH.exists():
        return {"drifted": True, "component": "agents_md", "reason": "registry file missing"}
    if not _AGENTS_MD.exists():
        return {"drifted": True, "component": "agents_md", "reason": "AGENTS.md missing"}

    registry = _load(_REGISTRY_PATH)
    expected_block = generate_agents_index(registry, "STRIPPED")
    actual_content = _AGENTS_MD.read_text(encoding="utf-8")
    actual_section = _extract_section(actual_content, _AGENTS_BEGIN_PREFIX, _AGENTS_END_MARKER)

    if actual_section is None:
        return {"drifted": True, "component": "agents_md", "reason": "BEGIN:CAPABILITY-DISCOVERY marker absent"}

    if _hash(_strip_ts(expected_block).rstrip()) == _hash(_strip_ts(actual_section).rstrip()):
        return {"drifted": False, "component": "agents_md"}
    return {
        "drifted": True,
        "component": "agents_md",
        "reason": "CAPABILITY-DISCOVERY section in AGENTS.md differs from freshly generated content",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect capability registry drift")
    parser.add_argument("--output", help="Write JSON drift report to this path")
    args = parser.parse_args()

    results = [check_registry_drift(), check_claude_drift(), check_agents_drift()]
    any_drift = any(r["drifted"] for r in results)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "overall": "DRIFT" if any_drift else "NO_DRIFT",
        "checks": results,
    }

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if any_drift:
        drifted = [r["component"] for r in results if r["drifted"]]
        print(f"DRIFT detected in: {', '.join(drifted)}")
        for r in results:
            if r["drifted"]:
                print(f"  [{r['component']}] {r.get('reason', '')}")
        return 1

    print("NO_DRIFT")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
