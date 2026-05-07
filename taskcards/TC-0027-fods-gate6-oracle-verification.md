---
artifact_id: TC-0027-fods-gate6-oracle-verification
artifact_type: taskcard
path: taskcards/TC-0027-fods-gate6-oracle-verification.md
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
notes: "Gate 6 oracle comparison DEC-034 independent verification taskcard for FODS. Created run034 (2026-05-06). Blocked by TC-0026 execution + explicit verification prompt."
---

# TC-0027: FODS Gate 6 — Oracle Comparison Independent Verification

**Taskcard ID:** TC-0027
**Phase:** 3 (Gate 6 verification — future)
**Gate:** Gate 6 (Oracle Comparison Complete)
**Status:** not_started
**Created:** 2026-05-06 (run034)
**Created by:** claude-opus-4-6 (run034)
**Blocking:** Gate 6 human approval
**Blocked by:** TC-0026 execution + explicit TC-0027 verification prompt

---

## STOP — Authorization Required

**This taskcard must not be executed until:**
1. TC-0026 (Gate 6 oracle execution) is complete
2. A human issues an explicit TC-0027 verification prompt

Per DEC-034 and AGENTS.md Section V: independent agent verification must be performed in a separate execution session before Gate 6 is submitted for human approval.

---

## Objective

Perform an independent DEC-034 verification sprint on the Gate 6 oracle comparison. Verify all TC-0026 claims before requesting Gate 6 human approval.

---

## Scope

### In scope

1. Independently re-run the oracle comparison tool
2. Verify oracle reference outputs match claimed results
3. Verify all discrepancies are correctly classified
4. Verify no unresolved data-loss discrepancies remain
5. Verify oracle comparison report is complete and accurate
6. Verify no forbidden paths created
7. Verify no Gate 6 self-approval
8. Produce DEC-034 verification evidence
9. Create Gate 6 human-review packet
10. Request Gate 6 human approval

### Out of scope — FORBIDDEN

- Gate 6 self-approval (human-only)
- Model changes during verification (read-only)
- Product source creation
- Fuzz testing (Gate 7)

---

## Related Files

- `taskcards/TC-0026-fods-gate6-oracle-execution.md` — execution parent
- `acquisition-packs/fods/gate6-oracle-comparison-report.md` — oracle comparison report (TC-0026 deliverable; committed sanitized summary)
- `tools/oracle/compare_fods_oracle.py` — comparison tool (TC-0026 deliverable)
- `.local/oracle/fods/` — raw oracle outputs (local-only, never committed)
