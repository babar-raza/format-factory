# Ruflo Mode Authority Decision
# Taskcard: TC1 — Resolve Ruflo Mode Contradiction
# Sprint: FORMAT-FACTORY-CROSS-PLAN-HARMONIZATION-BEFORE-EXECUTION-001
# Date: 2026-06-04

## Decision

**Supervisor runtime detection is authoritative for all Ruflo mode decisions.**

No plan may hardcode `MODE 4 ACTIVE` as a static assertion. At execution time, the executing
worker must read the Supervisor's current MCP status before invoking or assuming claude-flow
is available.

## Evidence of Contradiction

| Source | Claim | Status |
|--------|-------|--------|
| Mainstream plan (pre-fix) | `Current mode: MODE 4 ACTIVE — already has explicit human approval from 2026-05-30` | INCORRECT as static assertion |
| Supervisor (`check_mcp_status.py` detection) | `DETECTED_NOT_CONFIGURED` — registered in `.vscode/mcp.json` via `npx -y`, not running, not confirmed active | AUTHORITATIVE |
| `.vscode/mcp.json` | claude-flow registered as `npx -y claude-flow@3.10.14 mcp start` | Registration only; NOT activation |
| `.supervisor/policies.yaml` | `ruflo_complete_implies_evidence_accepted: false` | Enforced |

## Authoritative Rule

```
1. Before any Mainstream iteration starts, read Supervisor MCP status.
2. If Supervisor reports FULL_LOOP_APPROVED:
   - Assign mode: RUFLO_FULL_LOOP_APPROVED
   - May use claude-flow as NON-AUTHORITATIVE lane coordinator only
   - Must run validate_dual_orchestration_bridge.py before first use
   - All claude-flow outputs carry non_authoritative: true
3. If Supervisor reports DETECTED_NOT_CONFIGURED, ABSENT, BLOCKED, or unclear:
   - Assign mode: RUFLO_ABSENT
   - Use local Mainstream coordinator only
   - No claude-flow invocation
4. Ruflo absence NEVER blocks Mainstream execution.
5. Ruflo lane "complete" NEVER equals evidence accepted (policies.yaml enforced).
6. No claude-flow invocation unless Supervisor runtime governance has approved that mode
   for THIS run (not a historical approval from a prior sprint date).
```

## Changes Applied to Mainstream Plan

File: `C:\Users\prora\.claude\plans\twinkling-percolating-hare.md`

| Location | Old text | New text |
|----------|----------|----------|
| Key repo facts (line ~22) | `Current mode: **MODE 4 ACTIVE** — already has explicit human approval from 2026-05-30.` | `Current mode: **DETECT AT RUNTIME** — Supervisor runtime detection is authoritative. Do NOT hardcode MODE 4 ACTIVE...` |
| Pre-Execution reads (line ~67) | `confirm MODE 4 ACTIVE, claude-flow version` | `read claude-flow version; do NOT assume MODE 4 ACTIVE; confirm Supervisor runtime detection status` |
| TC-MAINSTREAM-RUFLO-001 content (line ~96) | `Mode: MODE 4 ACTIVE (approved 2026-05-30)` | `Mode: **RUNTIME DETECTED** — Supervisor runtime detection is authoritative...` |
| TC-MAINSTREAM-RUFLO-002 Current Repo State (line ~191) | `MODE 4 ACTIVE → RUFLO_FULL_LOOP_APPROVED is currently valid.` | `**Supervisor runtime detection is authoritative. Do NOT hardcode MODE 4 ACTIVE.**...` |
| Repo Facts Verified (line ~692) | `Current mode: MODE 4 ACTIVE (approved 2026-05-30)` | `Current mode: RUNTIME DETECTED (do NOT assume MODE 4 ACTIVE at execution time)` |
| IV question 4 (line ~756) | `YES — v3.10.14, MODE 4 ACTIVE, CLI = claude-flow` | `YES — v3.10.14 registered; mode determined at runtime by Supervisor detection` |

## Patch Notes for ruflo-mode-fallback-model.md

See `reports/mainstream-plan-repair/ruflo-mode-fallback-model-patch-note.md`.

The `TC-MAINSTREAM-RUFLO-002` content in the Mainstream plan already defines the correct 5-mode
detection model (RUFLO_ABSENT, RUFLO_LITE_AVAILABLE, RUFLO_FULL_LOOP_PENDING_APPROVAL,
RUFLO_FULL_LOOP_APPROVED, RUFLO_BLOCKED). The only fix needed was the "Current Repo State"
section which previously said "MODE 4 ACTIVE → RUFLO_FULL_LOOP_APPROVED is currently valid"
as a hard assertion. This has been changed to require runtime detection.

## Patch Notes for final-single-go-mainstream-poc-mega-train-execution-prompt.md

See `reports/mainstream-plan-repair/final-execution-prompt-patch-note.md`.

The `TC-EXEC-CONTINUE-002` content already includes runtime detection in the iteration loop
(Step 3: "Detect Ruflo mode → select Path A or Path B"). The fix ensures the Key repo facts
at the top of the plan no longer pre-decide the mode, so the Step 3 detection is actually used.

## Acceptance Criteria — Met

- [x] No plan currently says Mainstream may assume MODE 4 ACTIVE without Supervisor detection
- [x] Mainstream defaults to local coordinator when runtime mode is unclear
- [x] Ruflo absence never blocks Mainstream (policies: RUFLO_ABSENT → local coordinator, no stop)
- [x] Ruflo lane complete never equals evidence accepted (policies.yaml unchanged, always enforced)
- [x] No claude-flow invocation may happen unless Supervisor runtime governance approves
