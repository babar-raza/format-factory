---
artifact_id: TC-0025-fods-gate6-oracle-planning
artifact_type: taskcard
path: taskcards/TC-0025-fods-gate6-oracle-planning.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-06"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 6 oracle comparison planning taskcard for FODS. Created run033 (2026-05-06). Blocked by Gate 5 human approval + explicit Gate 6 planning prompt."
---

# TC-0025: FODS Gate 6 — Oracle Comparison Planning

**Taskcard ID:** TC-0025
**Phase:** 3 (Gate 6 planning — future)
**Gate:** Gate 6 (Oracle Comparison)
**Status:** completed
**Created:** 2026-05-06 (run033)
**Created by:** claude-opus-4-6 (run033)
**Blocking:** Gate 6 execution
**Blocked by:** Gate 5 human approval + explicit Gate 6 planning prompt

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. TC-0024 independent verification sprint (DEC-034) completes with PASS
2. Gate 5 is approved by a human
3. A human issues an explicit Gate 6 planning prompt naming TC-0025

Current state (run035):
- Gate 5: PASSED (Babar Raza, 2026-05-06, run035)
- Gate 5 approved: YES
- Gate 6: oracle_blocked_missing_tool (TC-0026 blocked — LibreOffice not installed)
- Oracle tool selected (LibreOffice headless) — NOT YET INSTALLED on dev machine
- Planning docs created run034: gate6-oracle-plan.md, oracle-scope.md, oracle-risk-register.md
- Oracle harness created run035: tools/oracle/ (5 files: README.md + 4 Python scripts)
- TC-0026 status: blocked_missing_oracle_tool

---

## Purpose

This taskcard governs the Gate 6 oracle comparison planning phase for FODS.

Gate 6 produces:
- Selection and configuration of an oracle tool (e.g., LibreOffice in headless mode)
- Oracle-generated reference outputs for all Gate 3 samples
- Comparison methodology between neutral model output and oracle output
- Discrepancy analysis and resolution plan

Gate 6 validates that the parser and neutral model produce correct results by comparing against an independent reference implementation.

---

## Scope (planning only — execution is FORBIDDEN now)

### Will be in scope (after Gate 5 passes and explicit prompt issued)

1. Select oracle tool (LibreOffice headless or equivalent)
2. Define comparison methodology
3. Generate oracle reference outputs for 4 Gate 3 samples
4. Compare neutral model output against oracle output
5. Document and analyze discrepancies
6. Produce oracle comparison report

### Out of scope — FORBIDDEN (applies now and at Gate 6)

- Product source (`src/python/fods/`, `src/net/fods/`) — FORBIDDEN (Gate 9+)
- Gate 6 self-approval — FORBIDDEN (human-only)
- Fuzz testing — FORBIDDEN (Gate 7)
- Security report — FORBIDDEN (Gate 8)
- CI workflows — FORBIDDEN (Gate 10+)
- Changing the neutral model based on oracle comparison — requires separate TC

---

## Prerequisites

- [ ] Gate 5 PASSED — human approval required
- [ ] Explicit Gate 6 planning prompt issued by human
- [ ] Oracle tool available on development machine

---

## Related Files

- `schemas/neutral-model/fods/` — neutral model (Gate 5 deliverable, input to oracle comparison)
- `prototypes/by-format/fods/fods_parser.py` — prototype parser (Gate 4 deliverable)
- `samples/by-format/fods/` — 4 Gate 3 samples (comparison corpus)
- `docs/gates.md` — Gate 6 criteria
