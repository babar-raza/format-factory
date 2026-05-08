---
artifact_id: TC-0026-fods-gate6-oracle-execution
artifact_type: taskcard
path: taskcards/TC-0026-fods-gate6-oracle-execution.md
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
notes: "Gate 6 oracle comparison execution taskcard for FODS. Created run034 (2026-05-06). Blocked by Gate 5 approval + Gate 6 planning review + explicit execution prompt."
---

# TC-0026: FODS Gate 6 — Oracle Comparison Execution

**Taskcard ID:** TC-0026
**Phase:** 3 (Gate 6 execution — future)
**Gate:** Gate 6 (Oracle Comparison Complete)
**Status:** COMPLETED
**Created:** 2026-05-06 (run034)
**Created by:** claude-opus-4-6 (run034)
**Completed:** 2026-05-08 (run043)
**Completed by:** claude-sonnet-4-6 (run043)
**Outcome:** ORACLE_COMPARE: PASS — 3/4 PASS, 1/4 WARN (SHEET_COUNT_MISMATCH on multi-sheet sample, expected LibreOffice CSV export limitation)
**Previously blocked:** Oracle provider not installed (LibreOffice not found — 9 preflight runs FAIL: run035–run042 + run043 pre-install)

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. ~~Gate 5 is approved by a human~~ **DONE** — Gate 5 PASSED (Babar Raza, 2026-05-06, run035)
2. ~~TC-0025 (Gate 6 planning) has been reviewed~~ **DONE** — TC-0025 completed (run035)
3. Oracle tool (LibreOffice) is installed and version verified — **STILL BLOCKED**
4. A human issues an explicit Gate 6 execution prompt naming TC-0026 — **SATISFIED** by current run038 prompt (conditional on oracle availability)

---

## Objective

Execute the oracle comparison for FODS: run all 4 Gate 3 samples through both the prototype parser and the oracle tool (LibreOffice headless), compare cell-by-cell, classify all discrepancies, and produce the oracle comparison report.

---

## Preconditions

- [x] Gate 5 PASSED (Babar Raza, 2026-05-06, run035 human-authorized prompt)
- [x] TC-0025 planning reviewed (completed run035)
- [ ] LibreOffice installed, version recorded — BLOCKER: not installed on dev machine (run035 preflight FAIL)
- [ ] Explicit TC-0026 execution prompt from human — pending LibreOffice installation

**BLOCKED:** LibreOffice not found on this machine. Install LibreOffice per `acquisition-packs/fods/oracle-installation-checklist.md` and re-execute TC-0026 with explicit prompt.
Oracle harness ready at tools/oracle/ (hardened run036: oracle_common.py, FORMAT_FACTORY_SOFFICE env var, --soffice-path CLI). Pre-flight tool: tools/oracle/preflight_oracle.py.
Provider registry: tools/oracle/provider_registry.yaml. Environment check: tools/oracle/validate_oracle_environment.py.
Provider options (alternatives considered): acquisition-packs/fods/oracle-provider-options.md.

---

## Deliverables

1. Oracle reference outputs in `.local/oracle/fods/` (local-only CSV exports — never committed)
2. Comparison tool at `tools/oracle/compare_fods_oracle.py`
3. Oracle comparison report at `acquisition-packs/fods/gate6-oracle-comparison-report.md` (committed sanitized summary only)
4. All discrepancies classified
5. Prototype bug fixes (if any discrepancies reveal bugs)
6. TC-0027 (Gate 6 verification) ready for execution

**Path model (canonical — run036):**
- Raw oracle outputs: `.local/oracle/fods/` (local-only, gitignored, never committed)
- Committed report: `acquisition-packs/fods/gate6-oracle-comparison-report.md`
- Blocker report (if oracle missing): `acquisition-packs/fods/gate6-oracle-blocker-report.md`

---

## Out of Scope — FORBIDDEN

- Product source code (`src/python/fods/`, `src/net/fods/`)
- Gate 6 self-approval (human-only)
- Fuzz testing (Gate 7)
- Security report (Gate 8)
- CI workflows (Gate 10+)
- Neutral model changes (requires separate TC)

---

## Related Files

- `acquisition-packs/fods/gate6-oracle-plan.md` — planning document
- `acquisition-packs/fods/oracle-scope.md` — scope definition
- `acquisition-packs/fods/oracle-risk-register.md` — risk register
- `taskcards/TC-0025-fods-gate6-oracle-planning.md` — planning taskcard
- `prototypes/by-format/fods/fods_parser.py` — prototype parser
- `samples/by-format/fods/` — Gate 3 samples (comparison corpus)
- `schemas/neutral-model/fods/` — neutral model (Gate 5 deliverable)
