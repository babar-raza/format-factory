# Supervisor-Generated Next Sprint Prompt
# Source sprint: FORMAT-FACTORY-ACCELERATION-R101-DEEP-TOOLING-MEGA-TRAIN-001
# Generated: 2026-06-03T13:10:42.366198
# ADVISORY ONLY — not a Format Factory authority document
# This is INPUT to the next sprint, not a gate approval or commit authorization.

---

## Sprint Focus
ADVANCE: Product deepening — .NET commercial + Python FOSS + dogfood + packaging

## Prior Sprint Summary
- Sprint ID: FORMAT-FACTORY-ACCELERATION-R101-DEEP-TOOLING-MEGA-TRAIN-001
- Evidence verdict: ALL_ACCEPTED_AUTONOMOUS_CONTINUE
- Tests: 816 passed, 0 failed, 0 skipped
- Autonomous continue: True

## Section 1: New Product Work (Advisory — Always Execute)
- [pending] TASK-001: Select governed product gaps and validate the product-code ledger
- [approval-blocked] TASK-002: Commit uncommitted product code and build sprint evidence bundle
- [approval-blocked] TASK-003: Advance FODS Gate 11 commercial readiness
- [approval-blocked] TASK-004: Advance FODT Gate 11 commercial readiness
- [blocked] TASK-005: Open ZST Gate 11
- [pending] TASK-006: Work on open taskcard: ABW-GATE4-001-parser-prototype
- [pending] TASK-007: Work on open taskcard: AI-USAGE-LEDGER-AND-METRICS
- [pending] TASK-008: Work on open taskcard: EVIDENCE-HYGIENE-ENFORCEMENT
- [pending] TASK-009: Product deepening: commercial-net-fods-dogfood-status-fods-to-csv-dotnet — dogfood_status.fods_to_csv_dotnet
- [pending] TASK-010: Product deepening: commercial-net-fods-dogfood-status-fods-to-html-dotnet — dogfood_status.fods_to_html_dotnet
- [pending] TASK-011: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-markdown-dotnet — dogfood_status.fodt_to_markdown_dotnet
- [pending] TASK-012: Product deepening: commercial-net-fodt-dogfood-status-fodt-to-txt-dotnet — dogfood_status.fodt_to_txt_dotnet
- [pending] TASK-013: Product deepening: foss-reduced-sylk-python-status-installed-workflow — python_status.installed_workflow
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
- Run `python tools/supervisor/supervisor_loop.py autonomous-cycle --declaration .local/evidences/<run_id>/evidence-declaration.yaml`
- ZIP bundle export is optional for archive or external transfer
- Final verdict must contain: VERDICT: <enum>
- All SHAs must be filled (no PENDING markers in final state)
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

## Acceptance Criteria Per Lane
(Fill from open taskcards in taskcards/ directory)

## Project Memory Context
```

```

---
END OF SUPERVISOR-GENERATED NEXT SPRINT PROMPT
