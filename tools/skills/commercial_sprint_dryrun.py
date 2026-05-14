"""
commercial_sprint_dryrun.py -- Phase R4/R5 Deliverable (Lane C)

Dry-run commercial sprint orchestrator.

PURPOSE:
  Orchestrate a full commercial sprint dry-run WITHOUT mutating any source code,
  executing implementation, approving gates, or publishing anything.

  A dry-run produces:
    1. Format context (from resolver)
    2. Lane selection (from lane selector)
    3. Accepted requirement IDs (from generated-requirements)
    4. Generated execution prompt (from swarm_prompt_generator)
    5. Quality gate validation result (from prompt_quality_gate)
    6. Sprint metadata summary
    7. Evidence contract metadata (planned — no actual bundle built in dry-run)

ALLOWED:
  - Reading all format data
  - State resolution (format_context_resolver)
  - Lane selection (lane_selector)
  - Prompt generation (swarm_prompt_generator)
  - Quality gate validation (prompt_quality_gate)
  - Evidence contract metadata generation
  - Writing dry-run output to reports/

NOT ALLOWED:
  - Source code mutation
  - Implementation execution
  - Gate approval
  - Publishing or pushing
  - Building actual evidence bundle (that is human-authorized)
  - Writing to src/net/ or src/python/

GOVERNANCE:
  - commercial_product_ready: false (always)
  - gate_self_approval_allowed: false (always)
  - DEC-034 IV required before implementation promotion
  - Evidence bundle must be human-authorized before build

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))


def run_dryrun(
    fmt: str,
    sprint_id: str,
    sprint_mission: str,
    output_report: bool = False,
) -> dict:
    """
    Execute a complete commercial sprint dry-run for a format.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')
    sprint_id : str
        Sprint identifier for the generated prompt
    sprint_mission : str
        Mission statement for the generated prompt
    output_report : bool
        If True, write a report to reports/planning/<dryrun-report>.md

    Returns
    -------
    dict with:
      format_id: str
      sprint_id: str
      dryrun_status: str  -- DRY_RUN_PASS | DRY_RUN_FAIL | DRY_RUN_BLOCKED
      requirements_state: str
      accepted_count: int
      selected_lanes: list
      blocked_lanes: list
      prompt_quality_gate_status: str
      quality_score: int
      prompt_char_count: int
      governance: dict
      evidence_contract_metadata: dict  -- planned only, not built
      timestamp: str
      notes: list[str]
    """
    from format_context_resolver import resolve_format_context
    from lane_selector import select_lanes
    from swarm_prompt_generator import generate_prompt
    from prompt_quality_gate import validate_prompt

    timestamp = datetime.utcnow().isoformat() + "Z"
    notes = []

    # Step 1: Resolve format context
    fmt_ctx = resolve_format_context(fmt)
    req_state = fmt_ctx["requirements_state"]["status"]
    governance = fmt_ctx["governance"]

    # Step 2: Lane selection
    lane_result = select_lanes(fmt_ctx)

    # Step 3: Prompt generation
    gen_result = generate_prompt(fmt, sprint_id, sprint_mission)

    # Step 4: Quality gate validation
    if gen_result["prompt"] is not None:
        gate_result = validate_prompt(gen_result["prompt"])
        gate_status = gate_result["status"]
        quality_score = gate_result["score"]
    else:
        gate_result = None
        gate_status = "NOT_GENERATED"
        quality_score = 0
        notes.append(f"Prompt generation blocked: {gen_result['generator_status']}")

    # Step 5: Evidence contract metadata (planned — not built in dry-run)
    evidence_contract_metadata = {
        "planned_contract_path": f"tools/evidence/contracts/{sprint_id.lower()}.yaml",
        "planned_bundle_path": f".local/evidence-bundles/{sprint_id.lower()}.zip",
        "planned_metadata_dir": f".local/metadata/{sprint_id.lower()}/",
        "note": "Dry-run only — no actual bundle built. Human authorization required.",
    }

    # Determine overall dry-run status
    if req_state != "REQUIREMENTS_AUTHORITATIVE":
        dryrun_status = "DRY_RUN_BLOCKED"
        notes.append(f"Requirements state is {req_state!r} — REQUIREMENTS_AUTHORITATIVE required")
    elif gate_status == "FAIL":
        dryrun_status = "DRY_RUN_FAIL"
        notes.append(f"Prompt quality gate FAILED — {gate_result['blocker_count']} blockers")
    elif gate_status in ("PASS", "PASS_WITH_WARNINGS"):
        dryrun_status = "DRY_RUN_PASS"
        if gate_status == "PASS_WITH_WARNINGS":
            notes.append("Quality gate has warnings — review before human submission")
    else:
        dryrun_status = "DRY_RUN_FAIL"
        notes.append("Unknown gate status")

    result = {
        "format_id": fmt,
        "sprint_id": sprint_id,
        "dryrun_status": dryrun_status,
        "requirements_state": req_state,
        "accepted_count": gen_result["accepted_count"],
        "selected_lanes": lane_result["selected_lanes"],
        "blocked_lanes": lane_result["blocked_lanes"],
        "prompt_quality_gate_status": gate_status,
        "quality_score": quality_score,
        "prompt_char_count": len(gen_result["prompt"]) if gen_result["prompt"] else 0,
        "governance": {
            "commercial_product_ready": False,
            "gate_self_approval_allowed": False,
            "autonomous_implementation_allowed": False,
            "dry_run_only": True,
            "implementation_requires_human_authorization": True,
            "dec034_iv_required_before_promotion": True,
        },
        "evidence_contract_metadata": evidence_contract_metadata,
        "timestamp": timestamp,
        "notes": notes,
    }

    if output_report:
        _write_dryrun_report(result, gen_result.get("prompt", ""), gate_result)

    return result


def _write_dryrun_report(result: dict, prompt_text: str, gate_result: dict | None):
    """Write a human-readable dry-run report to reports/planning/."""
    fmt = result["format_id"]
    sprint_id = result["sprint_id"]
    report_path = (
        REPO_ROOT / "reports" / "planning"
        / f"dryrun-commercial-orchestrator-{fmt}-{result['timestamp'][:10]}.md"
    )

    gate_details = ""
    if gate_result:
        lines = []
        for c in gate_result["checks"]:
            icon = "PASS" if c["status"] == "PASS" else c["status"]
            lines.append(f"| #{c['id']} | {c['name']} | {icon} | {c['detail']} |")
        gate_details = "\n".join(lines)

    content = f"""---
document_type: dryrun_commercial_orchestrator_report
format: {fmt}
sprint_id: {sprint_id}
date: {result['timestamp'][:10]}
visibility: internal
---

# Dry-Run Commercial Sprint Orchestrator Report

**Format:** {fmt.upper()}
**Sprint ID:** {sprint_id}
**Timestamp:** {result['timestamp']}
**DRY_RUN_STATUS:** {result['dryrun_status']}

---

## Section 1: Authority State

| Field | Value |
|-------|-------|
| Requirements State | {result['requirements_state']} |
| Accepted Count | {result['accepted_count']} |
| commercial_product_ready | False |
| gate_self_approval_allowed | False |

## Section 2: Lane Selection

**Selected:** {', '.join(result['selected_lanes'])}

**Blocked:** {', '.join(result['blocked_lanes'])}

## Section 3: Quality Gate Results

**Status:** {result['prompt_quality_gate_status']}
**Score:** {result['quality_score']}/10

| # | Criterion | Status | Detail |
|---|-----------|--------|--------|
{gate_details}

## Section 4: Prompt Stats

- Prompt length: {result['prompt_char_count']} characters

## Section 5: Evidence Contract (Planned)

- Contract path: `{result['evidence_contract_metadata']['planned_contract_path']}`
- Bundle path: `{result['evidence_contract_metadata']['planned_bundle_path']}`
- Metadata dir: `{result['evidence_contract_metadata']['planned_metadata_dir']}`
- **Note:** {result['evidence_contract_metadata']['note']}

## Section 6: Notes

{chr(10).join(f'- {n}' for n in result['notes']) if result['notes'] else 'None.'}

---

**DRY_RUN_ONLY: TRUE — No source mutation. No gate approval. No implementation execution.**
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(content, encoding="utf-8")
    print(f"  Report written: {report_path}")


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Dry-run commercial sprint orchestrator"
    )
    parser.add_argument("format", nargs="?", default="all",
                        help="Format ID (fods, fodt) or 'all'")
    parser.add_argument("--sprint-id", default="CONWAY-R7-DRY-RUN-001")
    parser.add_argument("--mission", default="Dry-run commercial sprint orchestration POC.")
    parser.add_argument("--report", action="store_true", help="Write report to reports/planning/")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    formats = ["fods", "fodt"] if args.format == "all" else [args.format]

    for fmt in formats:
        result = run_dryrun(
            fmt=fmt,
            sprint_id=args.sprint_id,
            sprint_mission=args.mission,
            output_report=args.report,
        )

        if args.json:
            print(json.dumps(result, indent=2))
            continue

        print(f"\n=== Dry-Run: {fmt.upper()} ===")
        print(f"  DRY_RUN_STATUS:     {result['dryrun_status']}")
        print(f"  REQUIREMENTS_STATE: {result['requirements_state']}")
        print(f"  ACCEPTED_COUNT:     {result['accepted_count']}")
        print(f"  QUALITY_GATE:       {result['prompt_quality_gate_status']} ({result['quality_score']}/10)")
        print(f"  PROMPT_SIZE:        {result['prompt_char_count']} chars")
        print(f"  COMMERCIAL_READY:   {result['governance']['commercial_product_ready']}")
        if result["notes"]:
            print(f"  NOTES: {'; '.join(result['notes'])}")


if __name__ == "__main__":
    main()
