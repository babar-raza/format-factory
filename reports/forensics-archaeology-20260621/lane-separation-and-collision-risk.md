# Lane Separation and Collision Risk

**Sprint:** forensics-archaeology-20260621

---

## Lane Architecture

The spec-to-feature plan defines 16 lanes:
- **System Healing:** Lanes 0, 1, 2, 3, 4, 5, 6, 14, 15
- **Product Regeneration:** Lanes 7, 8, 9, 10, 11, 12, 13

**Rule:** Lanes 1-6, 14, 15 MUST complete before product work (Lanes 7-13)

---

## Current Lane State

| Lane | Purpose | Status |
|------|---------|--------|
| 0 | Coordinator/supervision | PARTIAL — machinery sprints done, not formalized |
| 1 | SAL Pipeline Wiring | PARTIAL — sal_master_runner active, 14k+ facts |
| 2 | Capability Reintegration | PARTIAL — capability_compiler exists, advisory-only concerns |
| 3 | Capability-to-Feature Compiler | PARTIAL — compiler exists, path mismatch |
| 4 | Skills + Prompt Wiring | PARTIAL — 40+ skills, but spec_qname enforcement missing |
| 5 | Validators + Gate Hardening | PARTIAL — 46 validators, overclaim not wired |
| 6 | QName-to-Code Ontology | PARTIAL — spec stubs for 2 formats only |
| 14 | Autonomous Supervision Audit | PARTIAL — gaps identified, some fixed |
| 15 | Autonomous Healing/Learning | EARLY — failure-memory.json exists, propagation missing |
| 7 | .NET Architecture Blueprint | PARTIAL — FODS/FODT done |
| 8 | Python Blueprint + Migration | PARTIAL — FODS/FODT spec stubs created |
| 9 | FODS Product Rebuild | PARTIAL — in progress |
| 10 | FODT Product Rebuild | PARTIAL — in progress |
| 11 | ZST Hardening | NOT STARTED |
| 12 | CI/Package/Evidence | PARTIAL |
| 13 | Post-Regeneration Recompute | NOT STARTED |

---

## Collision Risk Assessment

### Risk 1: Product work mixed with machinery work (HIGH)

**Current state:** Product deepening (Lanes 9, 10) has been running CONCURRENTLY with
machinery healing (Lanes 1-6). This violates the "Wave ordering" rule.

**Evidence:** Recent commits show both machinery fixes (V45, SAL idempotency) and product
work (FODS neutral model, spec stubs) in the same sprints.

**Collision risk:** Machinery changes may invalidate assumptions product code was built on.
Product code may bypass machinery checks (e.g., spec_qname) that haven't been wired yet.

**Mitigation:** The LLM follows CLAUDE.md instruction to prioritize machinery before product.
But there is no CODE-LEVEL enforcement of this ordering.

### Risk 2: Spec stubs without production wiring (MEDIUM)

**Current state:** FODS spec stubs exist (fods/spec/) and Compat/ facades exist.
But the production parser (parser.py) returns raw dict objects, not spec stub instances.

**Evidence:** `neutral_model.py` builds dicts (Workbook/Sheet/Row/Cell as plain Python dicts).
`models.py` wraps those dicts (FodsCell wraps dict). `Compat/FodsCell` inherits from spec stub
`TableCell`. But the chain is: parser → dict → wrapper (models.py) → NOT going through Compat/.

**Collision risk:** Two parallel object hierarchies exist for FODS (models.py and Compat/).
Users importing from models.py get the non-spec-stub version. Users importing from Compat/
get the spec-aware version. These can diverge.

### Risk 3: Analytics files at LOC cap (LOW — contained)

**Current state:** xcf_analytics.py (4773 LOC), zst_analytics.py (4604 LOC), fodg_analytics.py (3214 LOC)
are at or near baseline_loc_cap. New functions would trigger GOV_BLOCK.

**Contained by:** deepening_suspension_validator (V42) and monolith_detection_validator (V43).

### Risk 4: fods/fods/ duplicate causing import confusion (MEDIUM)

**Current state:** Two spec stub locations with conflicting class names for the same qnames.
An import of `from fods.fods.spec.spreadsheet.workbook import Workbook` gives a DIFFERENT
class from `from fods.spec.office.document import Document` despite both being office:document.

**Collision risk:** If any code imports from the wrong location, you get the wrong class.

---

## Lane Contamination Can Happen: YES

Lane contamination is possible because:
1. No code-level lane enforcement exists
2. The autonomous loop selects work from `next-sprint.md` which mixes machinery and product tasks
3. Skills don't check which lane they belong to before executing

**But:** The corruption risk is bounded. The spec_qname pattern means ANY code that
CORRECTLY follows the standard is safe. Code that doesn't follow it is flagged by qname_structure_validator.

---

## Recommendations

1. Create `registry/lane-completion-ledger.yaml` to track lane status per sprint
2. Add lane ownership check to `autonomous_cycle.py` (TC-SUPERVISOR-LANES-001)
3. Resolve the dual-object-hierarchy problem in FODS (models.py vs Compat/ must converge)
4. Remove fods/fods/ duplicate immediately (TC-QNAME-DEDUP-001)
