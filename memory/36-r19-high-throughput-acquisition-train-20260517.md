# Memory 36 — R19 High-Throughput Acquisition Train

**Sprint:** FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001
**Date:** 2026-05-16
**Commit:** 2dcd7f869845e9c21b3de88f9776cdf9b989b74a
**Author:** Babar Raza <babar.raza@aspose.com>
**BACKFILL NOTE:** This memory file was created 2026-05-17, after R20 (memory/37 missing) and
R21 (memory/38) were already committed. It captures R19 state only. memory/38 is authoritative
for R21 and later state. memory/37 (R20 backfill) remains out of scope for this sprint.

---

## Sprint Summary

R19 "high-throughput acquisition train" executed a 6-format multi-gate push:
- ZST Gates 4-7 completed (all passed or waived)
- FODP/FODG Gates 2-3 completed (fast-path spec + corpus)
- Gnumeric/ABW Gates 2-3 completed (spec retrieval + corpus)
- ORA formally deferred (borderline score)
- Evidence hygiene policies established (P-EVID-001 through P-EVID-004)
- Gate 11 commercial train plan documented (planning only; not approved)

Test baseline at R19 completion: **1181 passed, 8 skipped, 0 failed**

---

## ZST Gates 4-7

### Gate 4 — Prototype Complete (Delegated Approval)
- Prototype: `prototypes/by-format/zst/` (4 files)
- Tests: `tests/skills/test_zst_gate4_prototype.py` — 27/27 PASS (R18 created; R19 delegated approval)
- Oracle comparison: `acquisition-packs/zst/oracle-comparison-report.md`
- Delegated approval report: `reports/planning/r19-zst-gate4-delegated-approval-report-20260516.md`
- Registry state after R19: `gate_4.status: passed` (upgraded from prototype_complete in R18)
- Python source authorization: NOT GRANTED (DEFER_ZST_PYTHON_SOURCE — deferred to R20+)

### Gate 5 — Waived (G-NORM-004)
- Decision: NEUTRAL_MODEL_NOT_APPLICABLE
- Reason: ZST is a pure compression codec — no document object model, no named fields
- Waiver: `acquisition-packs/zst/gate5-requirements-readiness.md`
- Delegated waiver report: `reports/planning/r19-zst-gate5-waiver-delegated-approval-report-20260516.md`
- Registry state after R19: `gate_5.status: waived_not_applicable`

### Gate 6 — Oracle Verified
- Oracle plan: `acquisition-packs/zst/gate6-oracle-plan.md`
- Tests: `tests/skills/test_zst_gate6_oracle.py` — 27+1 PASS
- Registry state after R19: `gate_6.status: passed`

### Gate 7 — Security/Fuzz Passed
- Fuzz plan: `acquisition-packs/zst/gate7-malformed-fuzz-plan.md`
- Fuzz report: `acquisition-packs/zst/gate7-malformed-fuzz-report.md`
- Risk scope: `acquisition-packs/zst/gate7-risk-scope.md`
- Tests: `tests/skills/test_zst_gate7_security_fuzz.py` — 27 PASS; 5 malformed samples tested
- Registry state after R19: `gate_7.status: passed`

### ZST Post-R19 State (as of R19 completion)
- Gates 1-7: ALL PASSED (Gate 5 waived per G-NORM-004)
- Python source authorization: DEFERRED (ZST-IMPL-001 taskcard created)
- Gate 8+: Not started at R19 completion
- RESOLVED_BY_LATER_SPRINT: R20 (commit 0d7e8c7) added ZST source; R21 advanced to Gates 8-10

---

## FODP / FODG — Gates 2-3

### Gate 2 — Fast-Path Spec Retrieval
- Fast-path authorization: `reports/planning/r18-fodp-fodg-gate2-fastpath-decision-20260516.md` (R18)
- Fast-path basis: ODF 1.3 spec already cached for FODS/FODT; same spec applies
- Gate 2 report: `reports/planning/r19-fodp-fodg-gate2-fastpath-20260516.md`
- Pack files updated: `acquisition-packs/fodp/spec-evidence.md`, `acquisition-packs/fodg/spec-evidence.md`
- Legal notes confirmed: `acquisition-packs/fodp/legal-notes.md`, `acquisition-packs/fodg/legal-notes.md`
- Registry state after R19: FODP gate_2, gate_3 both passed; FODG gate_2, gate_3 both passed

### Gate 3 — Sample Corpus (3 synthetic samples each)
- FODP samples: `samples/by-format/fodp/` — minimal-presentation.fodp, title-only.fodp, two-slides-basic.fodp
- FODG samples: `samples/by-format/fodg/` — empty-page.fodg, minimal-drawing.fodg, shapes-basic.fodg
- Parser notes: `acquisition-packs/fodp/parser-notes.md` (112 lines), `acquisition-packs/fodg/parser-notes.md` (121 lines)
- Sample source files: `acquisition-packs/fodp/sample-sources.md`, `acquisition-packs/fodg/sample-sources.md`

### FODP/FODG Post-R19 State (as of R19 completion)
- Gates 1-3: ALL PASSED
- Gate 4 parser prototype: PLANNED (taskcards FODP-GATE4-001, FODG-GATE4-001 created)
- RESOLVED_BY_LATER_SPRINT: R20 advanced these to full source implementation

---

## Gnumeric / ABW — Gates 2-3

### Gate 2 — Spec Retrieval
- Gnumeric: XSD v10 schema from gnumeric GitHub (primary); release tarball (secondary)
  - Spec evidence: `acquisition-packs/gnumeric/spec-evidence.md`
  - Report: `reports/planning/r19-gnumeric-gate2-spec-retrieval-20260516.md`
- ABW: AWML 1.0 DTD (secondary; outdated); AbiWord source reference required
  - Spec evidence: `acquisition-packs/abw/spec-evidence.md`
  - Report: `reports/planning/r19-abw-gate2-spec-retrieval-20260516.md`
  - Risk: MEDIUM (DTD outdated; AbiWord source supplement required at Gate 4)

### Gate 3 — Sample Corpus (3 synthetic samples each)
- Gnumeric samples: `samples/by-format/gnumeric/` — empty-sheet.gnumeric, minimal-spreadsheet.gnumeric, multi-cell-basic.gnumeric
- ABW samples: `samples/by-format/abw/` — empty-section.abw, minimal-document.abw, two-paragraphs.abw
- Sample sources: `acquisition-packs/gnumeric/sample-sources.md`, `acquisition-packs/abw/sample-sources.md`
- Legal notes: `acquisition-packs/gnumeric/legal-notes.md`, `acquisition-packs/abw/legal-notes.md`

### Gnumeric/ABW Post-R19 State (as of R19 completion)
- Gates 1-3: ALL PASSED
- Gate 4 parser prototype: PLANNED (taskcards GNUMERIC-GATE4-001, ABW-GATE4-001 created)
- RESOLVED_BY_LATER_SPRINT: R20 advanced these to full source implementation

---

## ORA — Deferred Borderline

- Score: 6.8 / 10.0 (threshold: 7.0)
- Decision: DEFERRED_BORDERLINE
- Decision report: `reports/planning/r19-ora-gate1-deferred-decision-20260516.md`
- Registry state: `gate_1.status: deferred_borderline`
- Pack file: `acquisition-packs/ora/pack.yaml`
- Reason: Score below threshold; re-evaluate if community engagement or spec quality improves
- Status at R19 completion: Deferred (no Gate 2 or further work authorized)

---

## FODS/FODT Gate 11 Commercial Train Plan

- Document: `reports/planning/r19-fods-fodt-gate11-commercial-train-plan-20260516.md`
- Status: PLANNING ONLY — not approved
- Sub-gates G11-A through G11-G defined: architecture → human approval
- commercial_product_ready: false (unchanged)
- Gate 11 sub-gate states: all NOT_STARTED or PROPOSED
- No implementation performed (plan only)

---

## Evidence Hygiene Policies Established (P-EVID-001 to P-EVID-004)

| Policy | Rule |
|--------|------|
| P-EVID-001 | Post-commit bundle required after every sprint |
| P-EVID-002 | No IN_PROGRESS state in final bundle |
| P-EVID-003 | AUTHORITATIVE_TEST_RESULT line required in verdict |
| P-EVID-004 | No stale HEAD in verdict |

Source: `reports/planning/r19-evidence-hygiene-and-post-commit-bundle-policy-20260516.md`
These policies are durable and apply to all subsequent sprints.

---

## Delegated Decision Normalization

- Report: `reports/planning/r19-delegated-decision-normalization-20260516.md`
- Several prior sprint decisions were retroactively normalized to follow delegated-decision format
- No gate state changes from normalization — historical cleanup only

---

## Taskcards Created by R19

| Taskcard | Status at R19 | Later Status |
|----------|--------------|-------------|
| ZST-IMPL-001 (Python source scaffold) | DEFERRED_PENDING_AUTHORIZATION | RESOLVED_BY_LATER_SPRINT: R20 |
| FODP-GATE4-001 (parser prototype) | PLANNED | RESOLVED_BY_LATER_SPRINT: R20/R21 |
| FODG-GATE4-001 (parser prototype) | PLANNED | RESOLVED_BY_LATER_SPRINT: R20/R21 |
| GNUMERIC-GATE4-001 (parser prototype) | PLANNED | RESOLVED_BY_LATER_SPRINT: R20/R21 |
| ABW-GATE4-001 (parser prototype) | PLANNED | RESOLVED_BY_LATER_SPRINT: R20/R21 |
| EVIDENCE-HYGIENE-ENFORCEMENT | NEW | Policies P-EVID-001 to P-EVID-004 applied |

---

## Registry State After R19 (14 Gate Transitions)

| Format | Gate Changes |
|--------|-------------|
| ZST | G4: prototype_complete → passed; G5: not_applicable → waived; G6: → passed; G7: → passed |
| FODP | G2: → passed; G3: → passed |
| FODG | G2: → passed; G3: → passed |
| Gnumeric | G2: → passed; G3: → passed |
| ABW | G2: → passed; G3: → passed |
| ORA | G1: scored_pending → deferred_borderline |

---

## What R19 Did NOT Complete

- ORA Gate 2+ (deferred — score below threshold)
- ZST Python source implementation (deferred — authorization not granted)
- FODS/FODT Gate 11 sub-gate execution (planning only)
- Any Gate 4 parser prototypes for FODP/FODG/Gnumeric/ABW (planned; deferred to R20+)
- R19 memory file (TC-SKILL-PRD-009) — this backfill is that missing step

---

## Evidence References

| Item | Path |
|------|------|
| R19 evidence bundle | `.local/r19-bundle.zip` |
| R19 bundle metadata | `.local/r19-metadata/` |
| R19 contract | `tools/evidence/contracts/r19-high-throughput-acquisition-train-swarm.yaml` |
| R19 commit | `2dcd7f869845e9c21b3de88f9776cdf9b989b74a` |
| R19 planning reports | `reports/planning/r19-*.md` (12 files) |

---

## Next Actions (Post-R19 Perspective)

All items below are marked with status relative to later sprints:

1. ZST Python source authorization → RESOLVED_BY_LATER_SPRINT: R20 (commit 0d7e8c7)
2. FODP/FODG Gate 4 parser prototypes → RESOLVED_BY_LATER_SPRINT: R20 (commit 0d7e8c7)
3. Gnumeric/ABW Gate 4 parser prototypes → RESOLVED_BY_LATER_SPRINT: R20 (commit 0d7e8c7)
4. ORA formal re-evaluation → REMAINS_DEFERRED (no later sprint changed ORA gate state)
5. FODS/FODT Gate 11 sub-gate execution → IN_PROGRESS (R21/R22 advanced G11-A/B/C/E; G11-G not approved)
6. R19 memory file creation → RESOLVED_BY_THIS_SPRINT: memory/36 (backfill 2026-05-17)

---

## Hard Invariants Maintained in R19

- No `src/python/zst/` or `src/net/zst/` created ✓
- No generated-requirements/zst/ created ✓
- commercial_product_ready: false for all formats ✓
- FODS/FODT Gate 11 not executed (plan only) ✓
- No GitHub push or PR ✓
- ZST Python source authorization not granted ✓
