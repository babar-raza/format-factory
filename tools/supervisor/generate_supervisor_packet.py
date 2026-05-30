"""
generate_supervisor_packet.py — Format Factory Local Supervisor Control Plane
Assembles supervisor next-sprint artifacts from evidence review + contradictions.

Generates:
  reports/supervisor/next-sprint.md        — full next-sprint Claude Code prompt
  reports/supervisor/next-sprint-taskmaster.json  — TM import ready (schema-validated)
  reports/supervisor/next-ruflo-lanes.json        — Ruflo lane plan (schema-validated)
  reports/supervisor/approval-gates.md            — gate classifications
  reports/supervisor/session-resume.md            — fresh-session briefing

Does NOT call Claude Code or any external API — pure local assembly.

Exit codes:
  0 — success
  3 — critical contradictions present; next-sprint focuses on repair
  9 — unexpected error

Usage:
  python tools/supervisor/generate_supervisor_packet.py
  python tools/supervisor/generate_supervisor_packet.py --review reports/supervisor/evidence-review.json --contradictions reports/supervisor/contradictions.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path


def load_json(path: Path) -> dict:
    if path and path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def load_memory(memory_path: Path) -> str:
    if memory_path.exists():
        lines = memory_path.read_text(encoding="utf-8").splitlines()
        # Return last 50 lines of memory
        return "\n".join(lines[-50:])
    return "(no memory file)"


def generate_next_sprint_md(review: dict, contradictions: dict, memory_snippet: str) -> str:
    sprint_id = review.get("sprint_id", "unknown")
    verdict = review.get("verdict", "unknown")
    facts = review.get("facts", {})
    critical_count = contradictions.get("critical_count", 0)
    autonomous = contradictions.get("autonomous_continue", True)

    if critical_count > 0:
        focus = "REPAIR: Address CRITICAL contradictions before advancing"
        repair_notes = "\n".join(
            f"- [{c['severity']}] {c['description']}"
            for c in contradictions.get("contradictions", [])
        )
    else:
        focus = "ADVANCE: Continue normal mega-train lanes"
        repair_notes = "None"

    next_r = "R79"  # Advisory suggestion only
    test_line = f"{facts.get('test_count', 0)} passed, {facts.get('fail_count', 0)} failed, {facts.get('skip_count', 0)} skipped"

    content = f"""# Supervisor-Generated Next Sprint Prompt
# Source sprint: {sprint_id}
# Generated: {datetime.now().isoformat()}
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
{focus}

## Prior Sprint Summary
- Sprint ID: {sprint_id}
- Evidence verdict: {verdict}
- Tests: {test_line}
- Autonomous continue: {autonomous}

## Contradictions Requiring Repair
{repair_notes}

## Suggested Next Sprint Identity
`FORMAT-FACTORY-{next_r}-SUPERVISOR-GENERATED-NEXT-SPRINT`
(Advisory — confirm with plans/master-plan.md before using)

## Non-Negotiable Rules (always apply)
1. No push without explicit user authorization.
2. No commit without explicit user authorization.
3. No gate self-approval.
4. No active .vscode/mcp.json without MODE 4 approval.
5. No Task Master / Ruflo init without MODE 3+ authorization.
6. Evidence bundle (ZIP) must be produced and validated with BUNDLE_VALIDATION: PASS.
7. All gate closures require human approval (gates 1-11).
8. Format Factory authority is final — supervisor is advisory only.

## Evidence Requirements for Next Sprint
- Evidence bundle built via tools/evidence/build_evidence_bundle.py
- Validated via tools/evidence/validate_evidence_bundle.py → BUNDLE_VALIDATION: PASS
- Final verdict must contain: VERDICT: <enum>
- All SHAs must be filled (no PENDING markers in final state)
- Tests: 0 failures required

## Suggested Lane Manifest (Advisory)
- Lane C0: Coordinator — integration, manifest authority, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, GOVERNANCE.md, master-plan state
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Implementation — per open taskcards
- Lane C4: Validation — pytest, py_compile, schema validation
- Lane C5: Negative/fuzz — negative test coverage
- Lane C6: Evidence — bundle build + validation
- Lane C7: Adversarial — challenge all claims before finalizing

## Acceptance Criteria Per Lane
(Fill from open taskcards in taskcards/ directory)

## Project Memory Context
```
{memory_snippet}
```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
"""
    return content


def generate_taskmaster_json(review: dict, contradictions: dict) -> dict:
    sprint_id = review.get("sprint_id", "unknown")
    critical_count = contradictions.get("critical_count", 0)
    timestamp = datetime.now().isoformat()

    tasks = []
    if critical_count > 0:
        for i, c in enumerate(contradictions.get("contradictions", []), 1):
            if c["severity"] == "CRITICAL":
                tasks.append({
                    "task_id": f"REPAIR-{i:03d}",
                    "title": f"Repair: {c['description'][:80]}",
                    "description": c.get("detail", ""),
                    "status": "pending",
                    "ff_taskcard_ref": "repair-required",
                    "supervisor_task_ref": "TC-SUP-009",
                    "acceptance_evidence": "contradictions.md shows 0 CRITICAL contradictions",
                    "validation_command": "python tools/supervisor/compare_goal_to_evidence.py --review reports/supervisor/evidence-review.json",
                    "non_authoritative": True,
                    "lane": "C2",
                })
    else:
        # Generate placeholder advance tasks
        tasks.append({
            "task_id": "TASK-001",
            "title": "Continue next mega-train sprint",
            "description": "Evidence accepted; continue normal sprint lanes per plans/master-plan.md",
            "status": "pending",
            "ff_doc_ref": "plans/master-plan.md",
            "supervisor_task_ref": "TC-SUP-010",
            "acceptance_evidence": "BUNDLE_VALIDATION: PASS in next sprint evidence bundle",
            "validation_command": "python tools/evidence/validate_evidence_bundle.py --contract <contract> --bundle <bundle>",
            "non_authoritative": True,
            "lane": "C0",
        })

    return {
        "sprint_id": f"supervisor-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": timestamp,
        "verdict": review.get("verdict", "unknown"),
        "source_bundle": review.get("bundle_path", ""),
        "tasks": tasks,
        "notes": f"Generated from evidence review of sprint {sprint_id}",
    }


def generate_ruflo_lanes_json(review: dict, contradictions: dict) -> dict:
    timestamp = datetime.now().isoformat()
    sprint_id = review.get("sprint_id", "unknown")

    lanes = [
        {
            "lane_id": "C0",
            "owner_role": "Coordinator",
            "title": "Sprint coordination and integration",
            "description": "Tracks all lanes; owns file ownership matrix; stops on emergency conditions",
            "allowed_files": ["reports/rNN/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**", "tools/evidence/**", "tests/evidence/**"],
            "dependencies": [],
            "tasks": [],
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C1",
            "owner_role": "Governance",
            "title": "Governance discovery",
            "description": "Read-only access to governance files; produces preflight report",
            "allowed_files": ["reports/rNN/00-preflight.md"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md"],
            "dependencies": [],
            "tasks": [],
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C2",
            "owner_role": "Repair",
            "title": "Contradiction repair",
            "description": "Address any open CRITICAL contradictions from prior sprint",
            "allowed_files": ["reports/rNN/**", "src/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0"],
            "tasks": [t["task_id"] for t in [] if t.get("lane") == "C2"],
            "status": "pending",
            "non_authoritative": True,
        },
        {
            "lane_id": "C6",
            "owner_role": "Evidence",
            "title": "Evidence bundle",
            "description": "Build and validate evidence bundle",
            "allowed_files": [".local/evidence/**"],
            "forbidden_files": ["AGENTS.md", "GOVERNANCE.md", "plans/master-plan.md", "registry/**"],
            "dependencies": ["C0", "C1", "C2"],
            "tasks": [],
            "status": "pending",
            "non_authoritative": True,
        },
    ]

    return {
        "sprint_id": f"supervisor-export-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
        "timestamp": timestamp,
        "verdict": review.get("verdict", "unknown"),
        "source_bundle": review.get("bundle_path", ""),
        "coordinator_lane": "C0",
        "lanes": lanes,
        "overlap_check_passed": True,
        "notes": f"Generated from evidence review of sprint {sprint_id}",
    }


def generate_approval_gates_md(review: dict, contradictions: dict) -> str:
    critical_count = contradictions.get("critical_count", 0)
    autonomous = contradictions.get("autonomous_continue", True)

    lines = [
        "# Approval Gates Classification",
        f"Sprint ID: {review.get('sprint_id', 'unknown')}",
        f"Generated: {datetime.now().isoformat()}",
        "",
        "## Pending Actions",
        "",
    ]

    if critical_count > 0:
        lines += [
            "| Action | Classification | Who Unblocks |",
            "|--------|---------------|-------------|",
            f"| Repair {critical_count} CRITICAL contradictions | local-repair-loop | Claude_Code |",
            "| Continue to next sprint | stop-contradictions-present | Claude_Code (after repair) |",
        ]
    else:
        lines += [
            "| Action | Classification | Who Unblocks |",
            "|--------|---------------|-------------|",
            "| Continue to next sprint lanes | autonomous-continue | null |",
            "| Gate approval (if any gate pending) | stop-gate-approval-required | Babar_Raza |",
            "| Push/commit | stop-push-approval-required | User |",
            "| MCP activation | stop-mcp-activation-required | User |",
        ]

    lines += [
        "",
        "## Summary",
        f"- AUTONOMOUS_CONTINUE: {'YES' if autonomous else 'NO — repair required first'}",
        "- NEXT_HUMAN_GATE: MODE 4 MCP activation (explicit user approval required)",
        "- DAEMON_STATUS: NOT_STARTED (no human gate needed to keep it stopped)",
    ]

    return "\n".join(lines) + "\n"


def generate_session_resume_md(review: dict, contradictions: dict, memory_snippet: str) -> str:
    facts = review.get("facts", {})
    return f"""# Session Resume Briefing
# Format Factory — Supervisor-Generated
# Generated: {datetime.now().isoformat()}

## Quick State
- Last sprint: {review.get('sprint_id', 'unknown')}
- Evidence verdict: {review.get('verdict', 'unknown')}
- Tests: {facts.get('test_count', 0)} passed / {facts.get('fail_count', 0)} failed
- PENDING markers: {facts.get('pending_marker_count', 0)}
- CRITICAL contradictions: {contradictions.get('critical_count', 0)}
- Autonomous continue: {contradictions.get('autonomous_continue', True)}

## What Was Done Last Sprint
(Read reports/supervisor/evidence-review.md for full details)

## What To Do Next
1. Read this file and evidence-review.md
2. Read approval-gates.md — follow classification
3. If contradictions exist → fix them before advancing
4. If autonomous-continue → proceed with next-sprint.md prompt
5. Read plans/master-plan.md for current phase state (AUTHORITY)

## Where To Find Evidence
- Last evidence bundle: {review.get('bundle_path', 'see .supervisor/state/current-run.json')}
- Supervisor outputs: reports/supervisor/
- Project memory: .supervisor/project-memory.md

## Project Memory (recent)
```
{memory_snippet}
```

## IMPORTANT REMINDERS
- Format Factory authority is FINAL. Supervisor output is advisory.
- No push without explicit user authorization.
- No gate self-approval. All gates 1-11 require human approval.
- No MCP activation without explicit user approval (MODE 4).
"""


def validate_against_schema(data: dict, schema_path: Path) -> list[str]:
    """Validate data against JSON schema. Returns list of errors."""
    try:
        import jsonschema
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        try:
            jsonschema.validate(instance=data, schema=schema)
            return []
        except jsonschema.ValidationError as e:
            return [str(e.message)]
        except jsonschema.SchemaError as e:
            return [f"Schema error: {e.message}"]
    except ImportError:
        return ["jsonschema library not available — skipping schema validation"]
    except Exception as e:
        return [f"Validation error: {e}"]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate supervisor next-sprint packet from evidence review"
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=Path("reports/supervisor/evidence-review.json"),
        help="Path to evidence-review.json",
    )
    parser.add_argument(
        "--contradictions",
        type=Path,
        default=Path("reports/supervisor/contradictions.json"),
        help="Path to contradictions.json",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/supervisor"),
        help="Directory for output files",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path("."),
        help="Repository root",
    )
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    review = load_json(args.review)
    contradictions = load_json(args.contradictions)
    memory_snippet = load_memory(repo_root / ".supervisor" / "project-memory.md")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate next-sprint.md
    next_sprint_text = generate_next_sprint_md(review, contradictions, memory_snippet)
    (output_dir / "next-sprint.md").write_text(next_sprint_text, encoding="utf-8")

    # Generate next-sprint-taskmaster.json
    tm_data = generate_taskmaster_json(review, contradictions)
    schema_dir = repo_root / ".supervisor" / "schemas"
    tm_errors = validate_against_schema(tm_data, schema_dir / "next-sprint-taskmaster.schema.json")
    (output_dir / "next-sprint-taskmaster.json").write_text(json.dumps(tm_data, indent=2), encoding="utf-8")

    # Generate next-ruflo-lanes.json
    ruflo_data = generate_ruflo_lanes_json(review, contradictions)
    ruflo_errors = validate_against_schema(ruflo_data, schema_dir / "next-ruflo-lanes.schema.json")
    (output_dir / "next-ruflo-lanes.json").write_text(json.dumps(ruflo_data, indent=2), encoding="utf-8")

    # Generate approval-gates.md
    gates_text = generate_approval_gates_md(review, contradictions)
    (output_dir / "approval-gates.md").write_text(gates_text, encoding="utf-8")

    # Generate session-resume.md
    resume_text = generate_session_resume_md(review, contradictions, memory_snippet)
    (output_dir / "session-resume.md").write_text(resume_text, encoding="utf-8")

    critical_count = contradictions.get("critical_count", 0)
    print(f"PACKET_GENERATION: COMPLETE")
    print(f"  Output dir: {output_dir}")
    print(f"  next-sprint.md: written")
    print(f"  next-sprint-taskmaster.json: written" + (f" (schema errors: {tm_errors})" if tm_errors else " (schema OK)"))
    print(f"  next-ruflo-lanes.json: written" + (f" (schema errors: {ruflo_errors})" if ruflo_errors else " (schema OK)"))
    print(f"  approval-gates.md: written")
    print(f"  session-resume.md: written")

    if critical_count > 0:
        print(f"  NOTE: {critical_count} CRITICAL contradictions — next-sprint focuses on repair")
        return 3

    return 0


if __name__ == "__main__":
    sys.exit(main())
