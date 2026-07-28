"""path_scope_lint.py — Skills-First Control: registry path-declaration lint.

Fail-closed self-test: every ACTIVE skill whose command file documents an
"Allowed Paths" section referencing `src/python/` or `src/net/` must have a
non-empty, template-token-free, actually-matchable `implementation_paths` or
`allowed_paths` entry in `.supervisor/skill-registry.yaml`.

Without this, `tools/supervisor/coordination/hooks/skill_gate.py`'s
`evaluate_path()` can never return `SKILL_EXISTS_BUT_NO_MANIFEST` for that
skill's real files: `_skill_scope_covers()` reuses `closeout.path_allowed()`,
which supports only exact match, prefix match, and trailing wildcards -- no
mid-path wildcard. A declared path containing a template placeholder like
`<format>` can therefore never match any real repository path. The skill
looks registered but is functionally invisible to the tool-layer gate, which
always returns `NO_SKILL_RESOLVED_FOR_PATH` (never block-eligible) for every
file that skill is supposed to govern.

Usage:
  python -m tools.governance.skills_first.path_scope_lint [--json]

Exit codes: 0 = PASS, 1 = FAIL (violations found), 2 = CONFIG_ERROR.
"""
from __future__ import annotations

import argparse
import json
import re
import sys

from .closeout import path_allowed
from .registries import REPO_ROOT, RegistryError, load_skills

# A path containing a template placeholder like <format>/<format_name> can
# never match a real path via path_allowed()'s prefix/glob semantics.
_TEMPLATE_TOKEN_RE = re.compile(r"<[^>]+>")

_ALLOWED_PATHS_HEADING_RE = re.compile(r"^#{1,3}\s*Allowed Paths\s*$", re.MULTILINE)
_NEXT_HEADING_RE = re.compile(r"^#{1,3}\s", re.MULTILINE)
_SRC_REF_RE = re.compile(r"src/(python|net)/")
# A bullet line that only grants READ access to src/ (recon, SHA computation,
# diff analysis) is not a write-scope declaration -- excluding it prevents
# false positives like `qname-backfill` ("src/python/<format>/ (read-only
# scan)") or `dependabot-config` ("Read -- ... src/net/**/*.csproj ...").
_READONLY_LINE_RE = re.compile(r"read[\s-]*only|^-\s*Read\b", re.IGNORECASE)

# Representative real repository paths used to sanity-check that a declared
# scope actually resolves against something concrete, not just "looks like"
# a path. Chosen to span both product tracks, the one confirmed-orphaned
# shared-infrastructure subtree (see RC-E in the skills-first hardening
# plan), and the one legitimately narrow, non-generic scope (FODT's spec/
# bootstrap subtree) known to exist -- a fixed probe set will always be an
# incomplete sample for arbitrarily narrow-but-correct declared scopes; add
# a probe here rather than loosening the match requirement if a future skill
# is validly scoped to a subtree none of these probes reach.
_PROBE_PATHS = (
    "src/python/fods/fods_writer.py",
    "src/python/_shared/exceptions.py",
    "src/net/fods/FodsWriter.cs",
    "src/python/fodt/spec/text/paragraph.py",
)


def _command_declares_src_scope(command_file: str) -> bool:
    """True if the skill's command .md documents an "Allowed Paths" section
    with at least one WRITE-scoped bullet line referencing src/python/ or
    src/net/ (i.e. this is a src/-mutating skill). A line whose only src/
    reference is explicitly read-only (recon, SHA computation, diff
    analysis -- "read-only", "read only", or a line starting "- Read --")
    does not count; several skills document read access to src/ for
    context without ever writing there."""
    path = REPO_ROOT / command_file
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace")
    m = _ALLOWED_PATHS_HEADING_RE.search(text)
    if not m:
        return False
    body = text[m.end():]
    nxt = _NEXT_HEADING_RE.search(body)
    if nxt:
        body = body[:nxt.start()]
    for line in body.splitlines():
        if _SRC_REF_RE.search(line) and not _READONLY_LINE_RE.search(line):
            return True
    return False


def _declared_paths(skill) -> list[str]:
    return list(skill.implementation_paths or []) + list(skill.allowed_paths or [])


def _resolves_against_a_probe(declared: list[str]) -> bool:
    return any(path_allowed(probe, declared) for probe in _PROBE_PATHS)


def lint() -> dict:
    violations: list[dict] = []
    for s in load_skills():
        if not s.is_active or not s.command_file:
            continue
        if not _command_declares_src_scope(s.command_file):
            continue

        declared = _declared_paths(s)
        if not declared:
            violations.append({
                "skill_id": s.skill_id,
                "category": "empty_declared_paths",
                "detail": "command file documents a src/ Allowed Paths"
                          " section but implementation_paths/allowed_paths"
                          " is empty in the registry",
            })
            continue

        templated = [p for p in declared if _TEMPLATE_TOKEN_RE.search(p)]
        if templated:
            violations.append({
                "skill_id": s.skill_id,
                "category": "unmatchable_template_token",
                "detail": f"declared path(s) contain a template placeholder"
                          f" that path_allowed() can never match a real"
                          f" path against: {templated}",
            })
            continue

        if not _resolves_against_a_probe(declared):
            violations.append({
                "skill_id": s.skill_id,
                "category": "no_probe_match",
                "detail": f"declared paths {declared!r} do not match any"
                          f" representative real src/ path {_PROBE_PATHS!r}",
            })

    return {
        "schema": "skills-first-control/path-scope-lint@1",
        "verdict": "FAIL" if violations else "PASS",
        "violation_count": len(violations),
        "violations": sorted(violations, key=lambda v: v["skill_id"]),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Skills-First Control path-scope lint")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    try:
        report = lint()
    except RegistryError as exc:
        print(json.dumps({"verdict": "CONFIG_ERROR", "error": str(exc)}), file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"[path-scope-lint] verdict={report['verdict']}"
              f" violations={report['violation_count']}")
        for v in report["violations"]:
            print(f"  {v['skill_id']}: [{v['category']}] {v['detail']}")

    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
