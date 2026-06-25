# Live Read-Only Run Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

This document defines the live read-only execution plan — Phase D of the product quality
review cycle. Phase D converts NEEDS_CONFIRMATION and LIKELY problems to VERIFIED status
through targeted source inspection and test analysis.

---

## Phase D Scope

**Inputs:** Phase B matrix files + Phase C dry run validation (PASS)
**Outputs:** Confirmed problem matrix + final product quality scores
**Source modifications:** NONE — read-only throughout

---

## Execution Sequence

### D-01: Confirm PQ-012 — FODT .NET Table Operations

**Target:** `src/net/fodt/FodtDocument.cs` and `src/net/fodt/Spec/Table/*.cs`

**Steps:**
1. Read `src/net/fodt/FodtDocument.cs` — search for: `AddTable`, `RemoveTable`, `GetTables`, `Table`
2. Read `src/net/fodt/Spec/Table/Table.cs` — check for `// GENERATED — architecture_only` marker
3. Read `src/net/fodt/Spec/Table/TableRow.cs` — same check
4. Read `src/net/fodt/Spec/Table/TableCell.cs` — same check

**Expected finding:** All Spec/Table/* files are architecture-only stubs. FodtDocument has no table API.
**Update:** Set PQ-012 confidence to VERIFIED; severity remains MEDIUM (table API not in initial scope)

**Decision required:** Is table support in FODT .NET release scope?
- If YES: P1, L effort fix required (wire table operations)
- If NO: P2, XS effort (remove stubs or document as architecture-only)

---

### D-02: Confirm Contradiction-002 — ZST .NET Capability Map

**Target:** `reports/capability-layer/commercial-capability-map.json`

**Steps:**
1. Read or grep `commercial-capability-map.json` for "zst" or "ZST" entries
2. Check what capabilities are listed (compress, decompress, parse, etc.)
3. Compare against confirmed source reality: ZstDocument = pure DTO, ZstParser only

**Expected finding:** Capability map may claim compress/decompress for ZST .NET (mismatch)
**Update:** Set Contradiction-002 to CLAIM_CONTRADICTED if capability is claimed

---

### D-03: Verify Contradiction-003 — 14 Python Formats at PROOF_LEVEL_4+

**Target:** `examples/python/*/consumer_roundtrip.py` + MEMORY.md claim

**Steps:**
1. List all `consumer_roundtrip.py` examples: `ls examples/python/*/consumer_roundtrip.py`
2. Check which formats have this file (indicates PROOF_LEVEL_4 consumer workflow)
3. Note which formats are missing (QOI, XCF, FODP — expected read-only/limited)
4. Assess: is PROOF_LEVEL_4 reasonably satisfied?

**Expected finding:** 14-16 formats have consumer_roundtrip.py — LIKELY TRUE
**Update:** Set Contradiction-003 to CLAIM_VERIFIED with minor qualification about FODP

---

### D-04: Quick-Check PQ-016 — _shared Dead Abstraction

**Target:** `src/python/_shared/` + grep across format __init__.py files

**Steps:**
```bash
ls src/python/_shared/
grep -l "_base_codec\|_base_parser\|_shared" src/python/*/
```

**Expected finding:** _shared/ files exist but zero formats import from them → VERIFIED dead abstraction

---

### D-05: Quick-Check PQ-020 — No .pyi Type Stubs

**Target:** `src/python/`

**Steps:**
```bash
find src/python -name "*.pyi" 2>/dev/null | wc -l
```

**Expected finding:** 0 .pyi files → VERIFIED

---

### D-06: Sprint-Named Test Count (PQ-017 precision)

**Target:** `tests/net/fods/`

**Steps:**
```bash
ls tests/net/fods/ | grep -E "R[0-9]+" | wc -l
ls tests/net/fods/ | wc -l
ls tests/net/fodt/ | grep -E "R[0-9]+" | wc -l
ls tests/net/fodt/ | wc -l
```

**Expected finding:** 70%+ of test files have sprint-prefix naming → VERIFIED HIGH confidence

---

### D-07: Verify FODS .NET static GetColumnHeaders (PQ-018)

**Target:** `src/net/fods/FodsDocument.cs` or `FodsDocumentAccessor.cs`

**Steps:**
```bash
grep -n "static.*GetColumnHeaders\|GetColumnHeaders.*static" src/net/fods/FodsDocument*.cs
```

**Expected finding:** At least one static overload of GetColumnHeaders → VERIFIED

---

### D-08: Final Score Reconciliation

After all confirmations complete:
1. Update confidence levels in `product-quality-problem-schema.json`
2. Re-score any products whose confirmed findings change their tier
3. Generate final sorted problem priority list (P0 first, then P1, P2, P3)
4. Identify which P0 problems are in scope for pilot fix (Phase E)

---

## Live Read-Only Run Success Criteria

| Item | Criteria |
|------|----------|
| PQ-012 confirmation | Status: VERIFIED or VERIFIED_FALSE |
| Contradiction-002 | Classification: CLAIM_CONTRADICTED or CLAIM_VERIFIED |
| Contradiction-003 | Classification: CLAIM_VERIFIED or CLAIM_OVERSTATED |
| PQ-016 quick check | Confirmed: dead abstraction or live abstraction |
| PQ-020 quick check | Confirmed: no .pyi files |
| PQ-017 precision | Exact percentage of sprint-named files |
| PQ-018 confirmation | Static overload confirmed line reference |
| Final sort | Problem list sorted by priority, ready for Phase E |

---

## Live Read-Only Run Time Estimate

| Step | Effort |
|------|--------|
| D-01 FODT table ops | 10 min |
| D-02 ZST capability map | 5 min |
| D-03 Consumer roundtrip list | 5 min |
| D-04 _shared grep | 2 min |
| D-05 .pyi check | 1 min |
| D-06 Test count | 2 min |
| D-07 GetColumnHeaders | 2 min |
| D-08 Score reconciliation | 15 min |
| **Total** | **~45 min** |

---

## Output After Phase D

A fully confirmed problem matrix (`product-quality-problem-schema.json`) with:
- All problems at VERIFIED confidence
- Final scores per product (potentially revised from Phase B)
- A sorted, actionable fix list grouped by (fix_priority, blocks_release, severity)
- Clear go/no-go signal for Phase E pilot fix

**Expected verdict:** `PHASE_D_COMPLETE — READY_FOR_PHASE_E_PILOT`
