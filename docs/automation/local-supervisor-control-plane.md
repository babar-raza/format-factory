# Local Supervisor Control Plane

## Purpose

The Local Supervisor Control Plane (Layer 2) replaces the manual ChatGPT upload-review-handoff loop.
It is deterministic, evidence-first, and has no authority over Format Factory gates.

## What It Replaces

| Manual step removed | Automated by |
|---------------------|-------------|
| Upload evidence bundle to ChatGPT | `supervisor_loop.py discover` |
| ChatGPT reviews evidence | `validate_evidence_for_supervisor.py` + evidence-review.md prompt |
| ChatGPT detects contradictions | `compare_goal_to_evidence.py` |
| ChatGPT writes next sprint prompt | `generate_supervisor_packet.py` + next-sprint-generator.md prompt |
| Human pastes prompt into Claude Code | TM imports `next-sprint-taskmaster.json` |
| Human selects parallel work | Ruflo consumes `next-ruflo-lanes.json` |
| Human remembers project state | `sync_local_memory.py` appends `.supervisor/project-memory.md` |
| Human decides continue/stop | Approval gate classifier (8 outcomes) |

## Directory Layout

```
.supervisor/
  config.yaml            # Supervisor configuration — supervisor_is_authoritative: false
  policies.yaml          # No-drift contract, contradiction detection, gate classification
  project-memory.md      # Sprint-over-sprint memory (append-only, idempotent by sprint_id)
  sprint-loop.md         # Procedure documentation for repeatable supervisor loop
  prompts/
    evidence-review.md           # Evidence review prompt template
    adversarial-review.md        # 15-question adversarial review
    next-sprint-generator.md     # Next sprint generation prompt
    approval-gate-classifier.md  # 8-outcome gate classification
    memory-sync.md               # Memory sync prompt
  schemas/
    evidence-review.schema.json          # Evidence review output schema
    next-sprint-taskmaster.schema.json   # TM export schema
    next-ruflo-lanes.schema.json         # Ruflo lanes export schema
    supervisor-verdict.schema.json       # Supervisor verdict schema
  state/                 # GITIGNORED — runtime state only
    current-run.json
    last-reviewed-bundle.json
    last-verdict.json

tools/supervisor/
  supervisor_loop.py                  # Orchestrator — main entry point
  discover_latest_evidence.py         # Bundle discovery
  validate_evidence_for_supervisor.py # Evidence validation + fact extraction
  compare_goal_to_evidence.py         # Contradiction detection
  generate_supervisor_packet.py       # Next-sprint artifact generation
  sync_local_memory.py                # Append-only memory sync

reports/supervisor/                   # Runtime outputs (per-run)
  evidence-review.md
  evidence-review.json
  contradictions.md
  contradictions.json
  next-sprint.md
  next-sprint-taskmaster.json
  next-ruflo-lanes.json
  approval-gates.md
  session-resume.md
```

## Usage

```bash
# Full pipeline (discovery → review → next-sprint → memory-sync)
python tools/supervisor/supervisor_loop.py run-on-latest

# Individual steps
python tools/supervisor/supervisor_loop.py discover
python tools/supervisor/supervisor_loop.py review --bundle path/to/bundle.zip
python tools/supervisor/supervisor_loop.py next
python tools/supervisor/supervisor_loop.py export-taskmaster
python tools/supervisor/supervisor_loop.py export-ruflo
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | No evidence bundle found |
| 2 | Validation failed / malformed bundle |
| 3 | Critical contradictions — autonomous loop paused |
| 9 | Unexpected error |

## Authority Model

The supervisor is advisory only. It does NOT have authority to:
- Close Format Factory gates (requires human approval at G11-G and above)
- Override evidence validators
- Approve commercial readiness
- Push or merge code
- Activate MCP servers (MODE 4 requires explicit human approval)

Format Factory repo authority hierarchy:
1. `registry/format-registry.yaml` — gate status (highest)
2. `plans/master-plan.md` — operational authority
3. `taskcards/` — task authority
4. Evidence bundles — sprint output

The supervisor verdict is Layer 2 advisory. It becomes input to the next sprint prompt.

## No-Drift Contract

See `tools/taskmaster/validate_dual_orchestration_bridge.py` for enforcement:

1. TM task "done" does NOT mean FF gate closed
2. Ruflo lane "complete" does NOT mean evidence accepted
3. Supervisor verdict does NOT mean gate approval
4. TM done + evidence fails → TM state must revert
5. Ruflo state contradicting FF registry → marked stale, ignored
6. Supervisor next-sprint.md is INPUT to next sprint, not authority

## Contradiction Detection

`compare_goal_to_evidence.py` detects:

- **CRITICAL** (stops autonomous loop):
  - Tests failed when contract requires pass
  - PENDING markers in final state
  - Gate claimed closed but evidence missing
  - Evidence bundle SHA mismatch
  - G11-G self-approval attempt

- **WARNING** (logged, continues):
  - Sprint ID mismatch between contract and bundle
  - Stale SHA in verdict
  - Missing taskcard reference in TM export

## Approval Gate Classification (8 Outcomes)

| Condition | Classification |
|-----------|---------------|
| Tests pass, evidence valid, no contradictions | autonomous-continue |
| Minor contradictions | local-repair-loop |
| Credentials missing | stop-credentials-missing |
| Push/merge needed | stop-push-approval-required |
| Gate approval needed | stop-gate-approval-required |
| Governance conflict unresolvable | stop-governance-conflict |
| Paid API required | stop-paid-api-not-available |
| Destructive action required | stop-destructive-action |

## Safety Constraints

- No real API keys in any tracked file
- No commit without explicit user request
- No push under any circumstances
- No MCP activation without explicit human approval (MODE 4+)
- No modification to AGENTS.md, GOVERNANCE.md, master-plan.md, registry
- No modification to existing validators (tools/evidence/, tests/evidence/)
- No gate self-approval
