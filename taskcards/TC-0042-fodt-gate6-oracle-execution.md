---
artifact_id: TC-0042-fodt-gate6-oracle-execution
artifact_type: taskcard
path: taskcards/TC-0042-fodt-gate6-oracle-execution.md
format_id: fodt
product_family: words
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODT Gate 6 oracle execution taskcard. Created run046 (2026-05-08). COMPLETED run047 (2026-05-08): FODT_ORACLE_RUN: PASS 4/4; FODT_ORACLE_COMPARE: PASS (with 2 WARN); run_fodt_oracle.py + compare_fodt_oracle.py created; gate6-oracle-comparison-report.md created. Gate 6 APPROVED Babar Raza."
---

# TC-0042: FODT Gate 6 — Oracle Execution

**Taskcard ID:** TC-0042
**Status:** completed — FODT Gate 6 oracle executed run047 (2026-05-08); FODT_ORACLE_RUN: PASS; FODT_ORACLE_COMPARE: PASS (with 2 WARN); Gate 6 APPROVED Babar Raza
**Gate:** FODT Gate 6
**Created:** 2026-05-08 (run046)
**Prerequisite:** FODT Gate 5 PASSED ✓ (Babar Raza, 2026-05-08, run046)

---

## STOP — Authorization Required

Must not execute until human issues explicit prompt naming "FODT Gate 6 oracle execution."

---

## Objective

Run LibreOffice oracle comparison for all 4 FODT samples. Produce oracle comparison report.

## Execution Steps

1. Run oracle preflight: `python tools/oracle/validate_oracle_environment.py`
   - Must output ORACLE_ENV: READY before proceeding
2. Create FODT-specific oracle scripts:
   - `tools/oracle/run_fodt_oracle.py` (LibreOffice --convert-to txt:Text)
   - `tools/oracle/compare_fodt_oracle.py` (parser vs oracle text comparison)
3. Run oracle on all 4 samples
4. Produce `acquisition-packs/fodt/gate6-oracle-comparison-report.md`
5. Record ORACLE_RUN result and ORACLE_COMPARE result

## Expected Output

- ORACLE_RUN: PASS 4/4 (all 4 samples converted)
- ORACLE_COMPARE: PASS 4/4 or WARN (with documented limitations)
- gate6-oracle-comparison-report.md created

## Forbidden

- No Gate 6 self-approval
- No product source creation
