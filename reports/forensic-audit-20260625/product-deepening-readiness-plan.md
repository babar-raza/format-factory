# Product Deepening Readiness Plan

**Sprint/Run ID:** ff-archaeology-20260625

---

## Current State Assessment

| Category | Status | Details |
|----------|--------|---------|
| Machinery operational | YES | SAL + capability + validators + supervisor all GREEN |
| Gen4 Python formats | 13/20 | Fully compliant, safe to deepen |
| Gen3 Python formats | 7/20 | Need domain model upgrade before deepening |
| QName compliance | 84.5% | DIF and FODG have HIGH gaps |
| Wave 3 gate | PARTIALLY MET | Lanes 1-6, 14, 15 not all COMPLETE per master plan |
| Gate 11 technical | READY for FODS/FODT | Awaiting business authorization |

---

## What MUST Be Fixed First (Blockers)

### Blocker 1: DIF QName Gap (HIGH)
**Task:** QNAME-BACKFILL-001
**Files:** `src/python/dif/dif_parser.py`
**Action:** Add `spec_qname: ClassVar[str] = "dif:data"` to DifData class,
`spec_qname: ClassVar[str] = "dif:cell"` to DifCell class
**Time estimate:** 15 minutes
**Tests needed:** Run `tests/python/dif/test_dif_spec_qname.py` — should pass

### Blocker 2: FODG QName Gap (HIGH)
**Task:** QNAME-BACKFILL-002
**Files:** `src/python/fodg/fodg_codec.py`
**Action:** Add `spec_qname: ClassVar[str] = "draw:frame"` to the primary codec class
**Time estimate:** 10 minutes
**Tests needed:** Run `tests/python/fods/test_tc_sp_002_facade_spec_qnames.py` equivalent for FODG

### Blocker 3: Capability Compiler Integration (HIGH)
**Task:** CAP-REPAIR-001
**Files:** `tools/supervisor/autonomous_cycle.py`
**Action:** Wire `gap_ledger_to_work_items.py` into Step 3a task selection
or unify with `capability_feature_compiler.py` output
**Time estimate:** 1-2 hours

---

## What Is SAFE to Continue Now (Green Lane)

The following Python formats are Gen4, QName-compliant, and safe for product deepening
WITHOUT fixing anything first:

| Format | What Can Be Deepened |
|--------|---------------------|
| ABW | Additional domain model properties, more analytics |
| CSV | Export capabilities, cross-format conversion |
| FODS | Gate 11 preparation, exporter expansion |
| FODT | Gate 11 preparation, exporter parity |
| GNUMERIC | Additional domain model features |
| NDJSON | Exporter expansion, analytics growth |
| TOML | Writer features, validation |
| TSV | Export capabilities |
| XCF | Export expansion (PNG, SVG targets) |
| ZST | Decompression features, analytics expansion |

**Safe product deepening criteria for Gen4 formats:**
1. `spec_qname: ClassVar[str]` present on all authority classes ✓
2. Domain model class (`models.py`) exists ✓
3. `from_file()` factory works ✓
4. At least one writer exists ✓
5. GAP-* entry in gap-ledger references the new capability ✓

---

## What Needs Targeted Repair Before Deepening

### Gen3 Formats (Need Domain Models First)

| Format | Required Fix | Taskcard | Effort |
|--------|-------------|---------|--------|
| ODS | Create OdsDocument in models.py | SRC-STD-001 | 2h |
| ODT | Create OdtDocument in models.py | SRC-STD-002 | 2h |
| PBM | Create PbmImage in models.py | SRC-STD-003 | 1h |
| PGM | Create PgmImage in models.py | SRC-STD-004 | 1h |
| PPM | Create PpmImage in models.py | SRC-STD-005 | 1h |
| QOI | Create QoiImage in models.py | SRC-STD-006 | 1h |
| SYLK | Create SylkDocument in models.py | SRC-STD-007 | 2h |

**Total effort:** ~10 hours for all 7 domain models

### DIF / FODG (Need QName Fix Before Deepening)

These CAN be deepened immediately AFTER QNAME-BACKFILL-001/002 are executed (~25 min total).

---

## Product Deepening Rotation Order (After Fixes)

### Priority 1: Gate 11 Execution (Business Impact)
1. Prepare FODS Gate 11 commercial sign-off packet → Submit to Babar Raza
2. Prepare FODT Gate 11 commercial sign-off packet → Submit to Babar Raza

### Priority 2: Close Remaining Open Gaps (105 gaps)
- Follow gap-ledger priority order (P0 first, then P1-P3)
- Coordinate with capability_feature_compiler.py output

### Priority 3: Gen4 Format Deepening
- NDJSON: expand analytics (ndjson_analytics.py still has room)
- CSV: add export capabilities
- ZST: compression features
- XCF: export pipeline

### Priority 4: Gen3→Gen4 Upgrades
- ODS, ODT, PBM, PGM, PPM, QOI, SYLK domain models

### Priority 5: .NET Parity
- NetPBM: add spec_qname, close Gate 11 gaps
- NDJSON .NET: expand tests to 100+
- TSV .NET: expand tests to 100+
- ZST .NET: expand tests to 100+

---

## Go/No-Go Decision Matrix

| Decision | Condition | Status |
|----------|-----------|--------|
| Continue FODS/FODT product deepening? | Gen4, Green, Gate 11 ready | GO |
| Continue Gen4 Python deepening? | Gen4, QName-compliant | GO |
| Start Gen3 Python deepening? | After domain model creation | CONDITIONAL GO |
| Start DIF/FODG deepening? | After QNAME-BACKFILL-001/002 | CONDITIONAL GO |
| Resume .NET commercial work? | After Gate 11 authorization | CONDITIONAL GO |
| Expand SAL to non-ODF formats? | After SAL-REPAIR lane | CONDITIONAL GO |
| Start product regeneration (Lanes 7-13)? | After Wave 3 gate COMPLETE | BLOCKED |

---

## Bottom Line

**DO NOT blindly continue product deepening across all formats.**
**DO proceed with the following immediately:**
1. Fix QNAME-BACKFILL-001/002 (DIF, FODG) — 25 minutes
2. Wire CAP-REPAIR-001 (compiler integration) — 1-2 hours
3. Create domain models for ODS, ODT, PBM, PGM, PPM, QOI, SYLK — 10 hours
4. Prepare Gate 11 packet for FODS, FODT — 2-3 hours

**Then resume full product deepening on all 20 Python + FODS/FODT .NET commercial.**
