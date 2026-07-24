"""Pre-execution gate for /add-dogfood-export (TC-PA-009).

Runs the two checks whose absence produced the defect class this gate exists to
stop (plan findings PF-001, PF-002):

  1. COMPATIBILITY -- is source->target a meaningful information-model pair?
     (~45 of 222 converters at HEAD are meaningless projections)
  2. IMPORT HYGIENE -- do the paths this skill will write mutate sys.path?
     (219 files / 406 occurrences at HEAD)

USAGE (from the skill, BEFORE writing any converter code; run from repo root)

    python -m tools.governance.skill_gates.dogfood_export_gate \
        --source-format dif --target-format csv \
        --target-paths src/python/dif/dif_to_csv.py

Invoked with `-m` deliberately: this gate bans sys.path mutation, so it must not
bootstrap itself with one. `-m` from the repo root puts the root on sys.path via
the interpreter's normal rules and needs no hack. (PA-F3 records that V149, the
zero-stub enforcer, does `import sys as _sys; _sys.path.insert(...)` -- an
enforcer that commits the offence it polices is not credible.)

Exit codes:
  0 = ALLOW        -- pair is registered compatible AND target paths are clean
  1 = BLOCKED      -- a check failed; do not write the converter
  2 = CONFIG_ERROR -- gate could not evaluate (missing/malformed matrix)

The --target-paths check is meaningful in two situations: re-running the gate
after generation (catches what was just written), and re-running over an
existing converter being modified. On a first run for a not-yet-created file the
hygiene check has nothing to read and reports 0 findings -- that is a real limit,
which is why the skill contract requires a POST-generation re-run.

ENFORCEMENT HONESTY: this script produces a deterministic verdict when it runs.
Nothing forces the skill's agent to run it. Blocking power comes from V249/V251
(sprint pipeline) and from the installed pre-commit hook. See
docs/governance/skill-gate-validator-seam.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from tools.governance.skill_gates import converter_compat, import_hygiene


def run(source_format: str, target_format: str, target_paths: list[str],
        matrix_path: str | None = None) -> dict:
    compat = converter_compat.check_pair(source_format, target_format, matrix_path)

    findings = import_hygiene.check_paths([p for p in target_paths
                                           if Path(p).exists()])
    hygiene_ok = not findings

    if compat.verdict == converter_compat.VERDICT_CONFIG_ERROR:
        verdict = "CONFIG_ERROR"
    elif compat.blocked or not hygiene_ok:
        verdict = "BLOCKED"
    else:
        verdict = "ALLOW"

    reasons: list[str] = []
    if compat.blocked:
        reasons.append(f"compatibility: {compat.reason}")
    if not hygiene_ok:
        reasons.append(
            f"import_hygiene: {len(findings)} sys.path mutation(s) in target paths — "
            "a Format Factory library must be importable as an installed package; "
            "sys.path mutation in shipped source mutates the importing "
            "application's interpreter state. Findings: "
            + "; ".join(f.format() for f in findings[:5]))

    return {
        "gate": "add-dogfood-export",
        "verdict": verdict,
        "pair": compat.pair,
        "compatibility": {
            "verdict": compat.verdict,
            "classification": compat.classification,
            "reason": compat.reason,
        },
        "import_hygiene": {
            "verdict": "CLEAN" if hygiene_ok else "VIOLATIONS",
            "checked_paths": [p for p in target_paths if Path(p).exists()],
            "findings": [f.format() for f in findings],
        },
        "reasons": reasons,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Pre-execution gate for /add-dogfood-export (TC-PA-009)")
    ap.add_argument("--source-format", required=True)
    ap.add_argument("--target-format", required=True)
    ap.add_argument("--target-paths", nargs="*", default=[],
                    help="paths the skill will write (re-run after generation)")
    ap.add_argument("--matrix", default=None,
                    help="override compatibility matrix path (tests only)")
    args = ap.parse_args(argv)

    result = run(args.source_format, args.target_format, args.target_paths,
                 args.matrix)
    print(json.dumps(result, indent=2))
    return {"ALLOW": 0, "BLOCKED": 1, "CONFIG_ERROR": 2}[result["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
