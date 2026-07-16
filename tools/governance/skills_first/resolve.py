"""Skills-First Control — deterministic skill resolution.

Implements the policy's skill_resolution_order (docs/governance/skill-only-policy.yaml
section 4) as executable logic: classify an operation + target paths against the
capability-routing registry, then select the primary registered+active skill.

Returns a resolution record with an explicit decision and rationale. When no
route/skill covers the operation it returns MISSING_SKILL_CAPABILITY (the signal
to invoke the skill-gap review) rather than guessing a loosely-related skill.

This is intentionally conservative: it never fabricates a skill and never
returns an inactive/unregistered skill.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

from .registries import RegistryError, load_routes, load_skills

# Keyword hints per route family; used only to rank routes for an operation
# string. Path hints match skills' declared allowed_paths / implementation_paths.
_STOPWORDS = {"the", "a", "an", "to", "of", "and", "for", "in", "on", "with",
              "change", "changing", "modify", "modifying", "update", "add"}

# Tokens so generic that a match on them ALONE is not a confident route match.
# When the winning route matched the operation only via these, the resolution is
# flagged low_confidence so the agent applies the extend-vs-create rubric instead
# of accepting a loosely-related skill (policy section 13 / prompt section 16).
_GENERIC_TOKENS = {"governance", "audit", "check", "validate", "sync", "update",
                   "control", "system", "repo", "repository", "run", "review"}


def _tokens(text: str) -> set[str]:
    return {t for t in re.split(r"[^a-z0-9]+", text.lower()) if t and t not in _STOPWORDS}


def resolve(operation: str, target_paths: list[str] | None = None) -> dict[str, Any]:
    routes = [r for r in load_routes() if r.is_active]
    skills = {s.skill_id: s for s in load_skills()}
    active_ids = {sid for sid, s in skills.items() if s.is_active}

    op_tokens = _tokens(operation)
    path_tokens: set[str] = set()
    for p in (target_paths or []):
        path_tokens |= _tokens(p)

    scored: list[tuple[int, Any]] = []
    for r in routes:
        blob = _tokens(r.route_id + " " + r.description)
        score = len(op_tokens & blob) * 2 + len(path_tokens & blob)
        # boost if a preferred skill's paths intersect the targets
        for sid in r.preferred_skill_ids:
            s = skills.get(sid)
            if s:
                sp = _tokens(" ".join(s.allowed_paths + s.implementation_paths
                                     + [s.product_track]))
                score += len(path_tokens & sp)
        if score > 0:
            scored.append((score, r))
    scored.sort(key=lambda x: (-x[0], x[1].route_id))

    for score, r in scored:
        usable = [sid for sid in r.preferred_skill_ids if sid in active_ids]
        if usable:
            composed = usable[1:] if len(usable) > 1 else []
            decision = "COMPOSE_EXISTING_SKILLS" if composed else "REUSE_EXACT_MATCH"
            matched = op_tokens & _tokens(r.route_id + " " + r.description)
            low_conf = bool(matched) and matched <= _GENERIC_TOKENS
            return {
                "verdict": "RESOLVED",
                "operation": operation,
                "route_id": r.route_id,
                "route_score": score,
                "selected_skill_id": usable[0],
                "composed_skill_ids": composed,
                "resolution_decision": decision,
                "low_confidence": low_conf,
                "matched_tokens": sorted(matched),
                "review_required": low_conf,
                "rationale": (
                    f"route '{r.route_id}' (score {score}) -> active skill "
                    f"'{usable[0]}'"
                    + (f" composed with {composed}" if composed else "")
                    + (" — LOW CONFIDENCE: matched only generic tokens "
                       f"{sorted(matched)}; apply extend-vs-create rubric before "
                       "accepting this skill" if low_conf else "")),
                "candidate_routes": [x[1].route_id for x in scored[:5]],
            }

    return {
        "verdict": "MISSING_SKILL_CAPABILITY",
        "operation": operation,
        "route_id": None,
        "selected_skill_id": None,
        "resolution_decision": "CREATE_MISSING_MICRO_SKILL",
        "rationale": "no active route maps to this operation; invoke skill-gap "
                     "review (do NOT implement directly, do NOT pick a loosely "
                     "related skill)",
        "candidate_routes": [x[1].route_id for x in scored[:5]],
    }


def _main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Skills-First skill resolution")
    ap.add_argument("--operation", required=True)
    ap.add_argument("--paths", nargs="*", default=[])
    args = ap.parse_args(argv)
    try:
        res = resolve(args.operation, args.paths)
    except RegistryError as exc:
        print(json.dumps({"verdict": "CONFIG_ERROR", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(res, indent=2))
    return 0 if res["verdict"] == "RESOLVED" else 1


if __name__ == "__main__":
    raise SystemExit(_main())
