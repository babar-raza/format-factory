# Repaired Supervisor-Generated Next Sprint Prompt
# Repaired by: FORMAT-FACTORY-PERMANENT-AUTONOMY-STOP-REASON-HARDENING-001
# Original: reports/supervisor/next-sprint.md (generated 2026-06-05T11:09:04.768906)
# Repair timestamp: 2026-06-05T12:00:00.000000
# Source sprint: FORMAT-FACTORY-DOTNET-TARGET-WRITER-READINESS-HARDENING-AND-POC-RECONCILIATION-001
# Stream: mainstream
# ADVISORY ONLY — not a Format Factory authority document

## Repairs Applied
| Task | Original Label | Corrected Label | Reason |
|------|---------------|-----------------|--------|
| TASK-002a | [approval-blocked] | [agent-owned] | Evidence bundle build is agent-owned |
| TASK-002b | [approval-blocked] | [external-gate] | Commit execution requires user auth |
| TASK-003a | [approval-blocked] | [agent-owned] | Gate 11 packet PREPARATION is agent-owned |
| TASK-003b | (new) | [external-gate] | Gate 11 approval EXECUTION is human-only |
| TASK-004a | [approval-blocked] | [agent-owned] | Gate 11 packet PREPARATION is agent-owned |
| TASK-004b | (new) | [external-gate] | Gate 11 approval EXECUTION is human-only |
| TASK-005 | [blocked] | [pending] | ZST POC not ready — continue implementation |

---

## STOP_REASON_ADVISORY (injected by stop_reason_adjudicator.py)

The following labels are NEVER sufficient to stop the autonomous train:
- `[approval-blocked]` — always reclassify via stop_reason_adjudicator.reclassify_task_label()
- `[blocked]` — reclassify; only TRUE_EXTERNAL_GATE signals stop
- `mode_5_approval_pending` — RUFLO_FALLBACK_LOCAL_CONTINUE, never a hard stop
- `evidence_quality_zero` — LOCAL_REPAIR_CONTINUE, not terminal
- `max_iterations_reached` — CHECKPOINT_ROLLOVER_CONTINUE, not terminal
- `gate_11_pending` when poc_ready=false — CONTINUE_NEXT_ITERATION
- `anti_skip_critical_block` with empty rework_items — false positive, continue

True external gates (ONLY these stop):
1. Git push/commit/merge (requires explicit user authorization)
2. Gate 8 approval execution (Babar Raza)
3. Gate 11 approval execution (Babar Raza)
4. Package publication (NuGet/PyPI)
5. Credentials unavailable with no fallback

---

## Sprint Focus
ADVANCE: Product deepening — .NET commercial + Python FOSS + dogfood + packaging

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-DOTNET-TARGET-WRITER-READINESS-HARDENING-AND-POC-RECONCILIATION-001
- Evidence verdict: ACCEPTED
- Tests: 29 passed, 0 failed, 1 skipped
- Autonomous continue: True (repaired from false stop)

## Section 1: New Product Work (Advisory — Always Execute)
- [pending] TASK-001: Select governed product gaps and validate the product-code ledger
- [agent-owned] TASK-002a: Build sprint evidence bundle and declaration
- [external-gate] TASK-002b: Execute git commit (requires explicit user authorization — do NOT self-execute)
- [agent-owned] TASK-003a: Prepare FODS Gate 11 readiness packet and commercial checklist
- [external-gate] TASK-003b: Submit FODS Gate 11 for Babar Raza approval (only after packet is ready — human required)
- [agent-owned] TASK-004a: Prepare FODT Gate 11 readiness packet and commercial checklist
- [external-gate] TASK-004b: Submit FODT Gate 11 for Babar Raza approval (only after packet is ready — human required)
- [pending] TASK-005: Continue ZST implementation and advance toward Gate 11 readiness criteria
- [pending] TASK-006: Work on open taskcard: ABW-GATE4-001-parser-prototype
- [pending] TASK-007: Work on open taskcard: AI-USAGE-LEDGER-AND-METRICS
- [pending] TASK-008: Work on open taskcard: EVIDENCE-HYGIENE-ENFORCEMENT
- [pending] TASK-009: Product deepening: commercial-net-fods-dogfood-status-fods-to-csv-dotnet
- [pending] TASK-010: Product deepening: commercial-net-fods-dogfood-status-fods-to-html-dotnet
- [pending] TASK-011: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet
- [pending] TASK-012: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet
- [pending] TASK-013: Product deepening: foss-reduced-sylk-python-status-installed-workflow
- [pending] TASK-014: Advance one dogfood export path using a Format Factory library
- [pending] TASK-015: Build package artifacts and run installed-workflow proof
- [pending] TASK-016: Write evidence declaration and run supervisor autonomous-cycle

## Section 2: Rework / Repair (Advisory — Fix Before Closeout)
None

## Contradictions Context
None

## Non-Negotiable Rules (always apply)
1. No push without explicit user authorization.
2. No commit without explicit user authorization.
3. No gate self-approval.
4. No active .vscode/mcp.json without MODE 4 approval.
5. No Task Master / Ruflo init without MODE 3+ authorization.
6. Load `.local/supervisor/selected-product-gaps.json` and `.supervisor/skill-registry.yaml` before product work.
7. All gate closures require human approval (gates 1-11).
8. Format Factory authority is final — supervisor is advisory only.
9. No direct ad-hoc `src/` edits. Use a governed skill or generated execution handoff.
10. Every `src/` edit requires an entry in `reports/r90/product-code-change-ledger.json`.

## Evidence Requirements for Next Sprint
- Write `.local/evidences/<run_id>/evidence-declaration.yaml`
- Run `python tools/supervisor/autonomous_cycle.py --declaration .local/evidences/<run_id>/evidence-declaration.yaml`
- Tests: 0 failures required

## Suggested Lane Manifest (Advisory)
- Lane C0: Coordinator — integration, manifest authority, stop-gate monitoring
- Lane C1: Governance discovery — read AGENTS.md, GOVERNANCE.md, master-plan state
- Lane C2: Repair lanes — address any open contradictions from prior sprint
- Lane C3: Governed implementation — selected gaps, skill registry, product-code ledger
- Lane C4: Dogfood export — use a Format Factory-produced library
- Lane C5: Package/install proof — build physical artifacts and run installed workflows
- Lane C6: Evidence — declaration + autonomous-cycle
- Lane C7: Adversarial — challenge all claims before finalizing
