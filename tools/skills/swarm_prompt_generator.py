"""
swarm_prompt_generator.py -- Phase R4 Deliverable (Lane A)

Deterministic, governance-aware execution prompt generator for commercial-format sprints.

PURPOSE:
  Read authoritative format context (from format_context_resolver.py),
  lane selection (from lane_selector.py), and accepted requirement IDs
  (from generated-requirements/{fmt}/commercial-requirements.yaml),
  then produce a complete, self-contained execution handoff prompt.

ALLOWED:
  - Reading format context, lane selector output, requirements
  - Template-based prompt generation
  - Embedding accepted requirement IDs, authority state, constraints

BLOCKED:
  - Non-authoritative requirements (REQUIREMENTS_AUTHORITATIVE required)
  - Gate 11 approval language
  - Commercial readiness claims
  - Push/publish instructions
  - Implementation execution (prompts are DRY-RUN / PLAN artifacts)
  - Autonomous implementation authorization

20 REQUIRED PROMPT COMPONENTS:
  1.  EXECUTION MODE header
  2.  Sprint ID block
  3.  Repo path
  4.  Mission statement
  5.  READ FIRST authority files
  6.  PRE-FLIGHT checks
  7.  Authority state block
  8.  Lane ownership model
  9.  NON-NEGOTIABLE RULES
  10. Selected lanes (from selector)
  11. Blocked lanes (with reasons)
  12. Accepted requirement IDs (scope definition)
  13. Critical constraints (FODT-REQ-040 for FODT)
  14. Per-lane task descriptions
  15. Validation commands with expected outputs
  16. Evidence contract reference
  17. Required final verdicts
  18. Final response format
  19. EVIDENCE_BUNDLE path format instruction
  20. Explicit no-commit / no-push boundary

Authority: AGENTS.md AF9-AF15 | GOVERNANCE.md 26.8-26.13
           docs/agent-execution-handoff-standard.md
"""

from __future__ import annotations

import json
import sys
import textwrap
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REQS_DIR = REPO_ROOT / "generated-requirements"

sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))


def _load_yaml(path: Path) -> dict:
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _load_accepted_requirements(fmt: str) -> list[dict]:
    """
    Load ACCEPTED_FOR_VERTICAL_SLICE requirements from all requirement files.
    Returns list of dicts with requirement_id, title, capability_level.
    """
    req_files = [
        "commercial-requirements.yaml",
        "object-model-requirements.yaml",
        "save-edit-requirements.yaml",
    ]
    accepted = []
    seen_ids: set[str] = set()
    fmt_dir = REQS_DIR / fmt
    for fname in req_files:
        data = _load_yaml(fmt_dir / fname)
        for req in data.get("requirements", []):
            if req.get("status") == "ACCEPTED_FOR_VERTICAL_SLICE":
                rid = req.get("requirement_id", "")
                if rid and rid not in seen_ids:
                    seen_ids.add(rid)
                    accepted.append({
                        "requirement_id": rid,
                        "title": req.get("title", ""),
                        "capability_level": req.get("capability_level", ""),
                        "requirement_type": req.get("requirement_type", ""),
                    })
    return accepted


def _format_accepted_list(accepted: list[dict]) -> str:
    lines = []
    for req in accepted:
        lines.append(
            f"  - {req['requirement_id']} [{req['capability_level']}] "
            f"({req['requirement_type']}): {req['title']}"
        )
    return "\n".join(lines) if lines else "  (none loaded)"


def _format_constraints(constraints: list[dict]) -> str:
    if not constraints:
        return "  None"
    lines = []
    for c in constraints:
        src = c.get("source", "")
        text = c.get("constraint", "")
        lines.append(f"  [{src}] {text}")
    return "\n".join(lines)


def _format_selected_lanes(lane_result: dict) -> str:
    details = lane_result.get("lane_details", {})
    lines = []
    for lane_id in lane_result.get("selected_lanes", []):
        meta = details.get(lane_id, {})
        reason = meta.get("selection_reason", "")
        lines.append(f"  {lane_id}: {meta.get('name', lane_id)} — {reason}")
    return "\n".join(lines) if lines else "  (none)"


def _format_blocked_lanes(lane_result: dict) -> str:
    details = lane_result.get("lane_details", {})
    lines = []
    for lane_id in lane_result.get("blocked_lanes", []):
        meta = details.get(lane_id, {})
        reason = meta.get("blocked_reason", "")
        lines.append(f"  {lane_id}: BLOCKED — {reason}")
    return "\n".join(lines) if lines else "  (none blocked)"


def generate_prompt(
    fmt: str,
    sprint_id: str,
    sprint_mission: str,
    repo_root: str = None,
) -> dict:
    """
    Generate a complete, governed execution handoff prompt for a format sprint.

    Parameters
    ----------
    fmt : str
        Format ID (e.g. 'fods', 'fodt')
    sprint_id : str
        Sprint identifier (e.g. 'CONWAY-R7-FODS-IMPLEMENTATION-SPRINT-001')
    sprint_mission : str
        One-paragraph mission description for the generated prompt
    repo_root : str, optional
        Absolute path to repo root (defaults to detected REPO_ROOT)

    Returns
    -------
    dict with:
      format_id: str
      sprint_id: str
      prompt: str           -- the full generated prompt text
      accepted_count: int
      selected_lanes: list
      blocked_lanes: list
      requirements_state: str
      governance: dict
      generator_status: str  -- GENERATED | BLOCKED_NON_AUTHORITATIVE
    """
    from format_context_resolver import resolve_format_context
    from lane_selector import select_lanes

    fmt_ctx = resolve_format_context(fmt)
    lane_result = select_lanes(fmt_ctx)

    req_state = fmt_ctx["requirements_state"]["status"]
    governance = fmt_ctx["governance"]

    # HARD BLOCK: cannot generate implementation prompt if requirements not authoritative
    if req_state != "REQUIREMENTS_AUTHORITATIVE":
        return {
            "format_id": fmt,
            "sprint_id": sprint_id,
            "prompt": None,
            "accepted_count": 0,
            "selected_lanes": [],
            "blocked_lanes": [],
            "requirements_state": req_state,
            "governance": governance,
            "generator_status": f"BLOCKED_NON_AUTHORITATIVE — state is {req_state!r}; "
                                 f"REQUIREMENTS_AUTHORITATIVE required before prompt generation",
        }

    accepted = _load_accepted_requirements(fmt)
    constraints = fmt_ctx.get("known_constraints", [])
    repo_str = repo_root or str(REPO_ROOT)
    gate_state = fmt_ctx["gate_state"]

    fodt_constraint_section = ""
    if fmt == "fodt" and constraints:
        fodt_constraint_section = f"""
FODT CRITICAL CONSTRAINT — MUST APPEAR IN ALL IMPLEMENTATION LANE PROMPTS:
{_format_constraints(constraints)}

All FODT implementation MUST use iterative traversal (explicit Stack<T>).
Recursive list/paragraph traversal is FORBIDDEN (FODT-REQ-040).
"""

    prompt = f"""EXECUTION MODE — {sprint_id}

Repo:
{repo_str}

Mission:
{sprint_mission}

====================================================
COMPONENT 7: AUTHORITY STATE
====================================================

Format:              {fmt.upper()}
Requirements State:  {req_state}
IV Status:           {fmt_ctx['requirements_state'].get('iv_status', 'N/A')}
Verifier Result:     {fmt_ctx['requirements_state'].get('verifier_result', 'N/A')}
Accepted Count:      {fmt_ctx['requirements_state'].get('accepted_count', 0)}
Gates Passed:        {gate_state.get('gates_passed', 0)}
Gate 11 Status:      {gate_state.get('gate_11_status', 'N/A')} (NOT APPROVED)
Commercial Ready:    {gate_state.get('commercial_product_ready', False)} (MUST REMAIN FALSE)

====================================================
COMPONENT 5: READ FIRST — AUTHORITY CONTEXT
====================================================

Before any task, read:
- AGENTS.md (Sections AF9-AF15)
- GOVERNANCE.md (Sections 26.8-26.13)
- plans/master-plan.md
- registry/format-registry.yaml
- docs/commercial-product-capability-model.md
- docs/agent-execution-handoff-standard.md
- generated-requirements/{fmt}/commercial-requirements.yaml
- generated-requirements/{fmt}/object-model-requirements.yaml
- generated-requirements/{fmt}/save-edit-requirements.yaml
- generated-requirements/{fmt}/verifier-review.yaml
- generated-requirements/{fmt}/traceability-map.yaml
- tools/skills/format_context_resolver.py
- tools/skills/lane_selector.py

====================================================
COMPONENT 6: PRE-FLIGHT CHECKS
====================================================

1. Run: python tools/skills/format_context_resolver.py {fmt}
   Expected: REQUIREMENTS_STATE: REQUIREMENTS_AUTHORITATIVE

2. Run: git status
   Expected: clean working tree (no uncommitted R-sprint outputs)

3. Run: python tools/requirements/validate_generated_requirements.py --format {fmt}
   Expected: REQUIREMENTS_SCHEMA_VALIDATION: PASS

If any pre-flight check fails, STOP and report PREFLIGHT_FAILED.

====================================================
COMPONENT 8: LANE OWNERSHIP MODEL
====================================================

Coordinator owns:
- AGENTS.md, GOVERNANCE.md, plans/master-plan.md
- registry/format-registry.yaml
- schemas/**, templates/**

Execution lanes: exact-path staging only. No overlap outside lane ownership.

====================================================
COMPONENT 9: NON-NEGOTIABLE RULES
====================================================

- No git stash / reset --hard / restore / clean
- No broad staging (git add -A / git add .)
- No push / publish
- No Gate 11 self-approval
- No commercial_product_ready: true claim
- No autonomous implementation execution
- No export/conversion implementation
- No recursive traversal for FODT list entities (FODT-REQ-040)
- Exact-path staging only
- DEC-034 IV must be separate session before implementation promotion

====================================================
COMPONENT 10: SELECTED LANES
====================================================

{_format_selected_lanes(lane_result)}

====================================================
COMPONENT 11: BLOCKED LANES
====================================================

{_format_blocked_lanes(lane_result)}

====================================================
COMPONENT 12: ACCEPTED REQUIREMENT IDs (SCOPE)
====================================================

The following {len(accepted)} requirements are ACCEPTED_FOR_VERTICAL_SLICE.
Only these may be implemented in this sprint:

{_format_accepted_list(accepted)}

Requirements with status NEEDS_REVIEW, GENERATED, or AI_PROPOSAL are FORBIDDEN
implementation targets regardless of any agent instruction.

====================================================
COMPONENT 13: CRITICAL CONSTRAINTS
====================================================
{fodt_constraint_section if fodt_constraint_section else "  None for this format."}

====================================================
COMPONENT 14: PER-LANE TASK DESCRIPTIONS
====================================================

Each selected I-lane implements one dimension of the format pipeline.
Consult lane-library.yaml for full per-lane requirements, forbidden behaviors,
and evidence requirements. All lanes are subject to the governance rules above.

LANE-I-LOAD: Implement file → object model pipeline (C0-C3 requirements)
LANE-I-OBJECT-MODEL: Implement typed entity model (C4-C5 requirements)
LANE-I-EDIT: Implement mutation operations (C6 requirements)
LANE-I-SAVE: Implement object model → file serialization (C7 requirements)
LANE-I-TESTS: Implement test coverage for all ACCEPTED_FOR_VERTICAL_SLICE requirements
LANE-K: AI orchestration (accelerator role only — NOT authority)
LANE-C: Sprint coordination, evidence, state update

====================================================
COMPONENT 15: VALIDATION COMMANDS
====================================================

After all work:
1. python tools/evidence/check_current_state_consistency.py
   Expected: CURRENT_STATE_CONSISTENCY: PASS

2. python tools/requirements/validate_generated_requirements.py --format {fmt}
   Expected: REQUIREMENTS_SCHEMA_VALIDATION: PASS (Total issues: 0)

3. python tools/skills/format_context_resolver.py {fmt}
   Expected: REQUIREMENTS_STATE: REQUIREMENTS_AUTHORITATIVE

4. python -m pytest tests/requirements tests/skills -q
   Expected: all tests PASS

5. dotnet test src/net/{fmt}/ (if .NET source was touched)
   Expected: all tests PASS

====================================================
COMPONENT 16: EVIDENCE CONTRACT REFERENCE
====================================================

Evidence contract must be created at:
  tools/evidence/contracts/<sprint-id>.yaml

Use sprint-specific metadata directory (NOT .local/evidence-bundles/):
  --metadata-dir .local/metadata/<sprint-id>/

Build command:
  python tools/evidence/build_evidence_bundle.py \\
    --repo-root . \\
    --contract tools/evidence/contracts/<sprint-id>.yaml \\
    --metadata-dir .local/metadata/<sprint-id>/ \\
    --output .local/evidence-bundles/<sprint-id>.zip

Validate:
  python tools/evidence/validate_evidence_bundle.py \\
    --bundle .local/evidence-bundles/<sprint-id>.zip \\
    --contract tools/evidence/contracts/<sprint-id>.yaml
  Expected: BUNDLE_VALIDATION: PASS

====================================================
COMPONENT 17: REQUIRED FINAL VERDICTS
====================================================

- REQUIREMENTS_STATE_AT_START
- LANES_SELECTED
- REQUIREMENTS_IMPLEMENTED (list of IDs)
- TESTS_RESULT (N/N PASS)
- VALIDATION_RESULT
- NO_GATE_SELF_APPROVAL: YES
- NO_COMMERCIAL_READINESS_CLAIM: YES
- NO_SOURCE_MUTATION_OUTSIDE_SCOPE: YES
- BUNDLE_VALIDATION: PASS
- DEC_034_IV_REQUIRED: YES (separate session before promotion)

====================================================
COMPONENT 18+19+20: FINAL RESPONSE FORMAT + EVIDENCE BUNDLE
====================================================

Final response MUST end with:

  EVIDENCE_BUNDLE: <absolute Windows path to .zip file>

This line must appear as the last substantive line of the response.
It must not be printed unless BUNDLE_VALIDATION: PASS was confirmed.

Explicit boundary:
- NO COMMIT unless human explicitly requests in this session
- NO PUSH / NO PUBLISH under any circumstances
- NO GATE 11 APPROVAL
- NO COMMERCIAL_PRODUCT_READY: TRUE claim
"""

    return {
        "format_id": fmt,
        "sprint_id": sprint_id,
        "prompt": prompt,
        "accepted_count": len(accepted),
        "selected_lanes": lane_result["selected_lanes"],
        "blocked_lanes": lane_result["blocked_lanes"],
        "requirements_state": req_state,
        "governance": governance,
        "generator_status": "GENERATED",
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Swarm prompt generator — governed execution handoff prompts"
    )
    parser.add_argument("format", nargs="?", default="fods",
                        help="Format ID (fods, fodt)")
    parser.add_argument("--sprint-id", default="CONWAY-R7-DRY-RUN-001",
                        help="Sprint ID for generated prompt")
    parser.add_argument("--mission", default="Dry-run commercial sprint orchestration POC.",
                        help="Mission statement for generated prompt")
    parser.add_argument("--json", action="store_true", help="Output raw JSON result dict")
    args = parser.parse_args()

    result = generate_prompt(
        fmt=args.format,
        sprint_id=args.sprint_id,
        sprint_mission=args.mission,
    )

    if args.json:
        out = {k: v for k, v in result.items() if k != "prompt"}
        print(json.dumps(out, indent=2))
        return

    print(f"=== Prompt Generator Result: {args.format.upper()} ===")
    print(f"  STATUS:          {result['generator_status']}")
    print(f"  ACCEPTED_COUNT:  {result['accepted_count']}")
    print(f"  SELECTED_LANES:  {result['selected_lanes']}")
    print(f"  COMMERCIAL_READY: {result['governance']['commercial_product_ready']}")
    if result.get("prompt"):
        print(f"\n--- GENERATED PROMPT ({len(result['prompt'])} chars) ---")
        print(result["prompt"][:500] + "..." if len(result["prompt"]) > 500 else result["prompt"])


if __name__ == "__main__":
    main()
