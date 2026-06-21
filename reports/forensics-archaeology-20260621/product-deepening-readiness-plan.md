# Product Deepening Readiness Plan

**Sprint:** forensics-archaeology-20260621

---

## Can Product Deepening Resume?

**For FODS and FODT: YES — with conditions**
**For all other formats: NO — machinery repairs required first**

---

## FODS + FODT Deepening Conditions

Before resuming product deepening for FODS/FODT:

1. [x] Spec stubs exist in fods/spec/ and fodt/spec/ ✓
2. [x] FODS Compat/ facade layer exists (in progress) ✓
3. [x] SAL facts exist (4987 FODS, 4933 FODT) ✓
4. [ ] FODT Compat/ facade layer — MISSING (TC-FODT-COMPAT-001)
5. [ ] fods/fods/spec/ duplicate removed — MISSING (TC-QNAME-DEDUP-001)
6. [ ] FODT models.py classes have spec_qname — MISSING (TC-FODT-COMPAT-001)
7. [ ] SAL path aligned with capability compiler — MISSING (TC-SAL-PATH-001)
8. [ ] add-python-object-model-feature requires spec_qname — MISSING (TC-SKILL-HARDEN-001)

**Estimated time to meet conditions:** 3-5 days of machinery repair sprints

---

## Formats Blocked from Deepening

| Format | Blocker | Required Before Deepening |
|--------|---------|--------------------------|
| ODS | No spec stubs; no spec_qname on domain classes | TC-QNAME-BACKFILL-001 |
| ODT | No spec stubs; no spec_qname on domain classes | TC-QNAME-BACKFILL-002 |
| FODG | 6421 LOC monolith; analytics rotation suspended | TC-QNAME-BACKFILL + analytics separation |
| XCF | 0 SAL facts; 7022 LOC monolith; no spec_qname | SAL facts + TC-BACKFILL |
| ZST | No spec_qname; 7130 LOC (at cap) | TC-BACKFILL |
| CSV | 0 SAL facts; no spec_qname domain class | SAL facts + TC-BACKFILL |
| DIF | No spec_qname; no canonical naming | TC-SKILL-CANONICAL-001 + TC-BACKFILL |
| SYLK | No spec_qname; no canonical naming | TC-SKILL-CANONICAL-001 + TC-BACKFILL |
| Netpbm | No spec_qname; binary format | TC-BACKFILL + canonical naming |
| QOI | No spec_qname; binary format | TC-BACKFILL |
| TOML | No spec_qname; 0 SAL facts | SAL + TC-BACKFILL |
| NDJSON | No spec_qname domain class | TC-BACKFILL |
| TSV | No spec_qname domain class | TC-BACKFILL |
| ABW | No spec_qname; 1708 LOC | TC-BACKFILL |
| Gnumeric | No spec_qname | TC-BACKFILL |
| FODP | No spec_qname | TC-BACKFILL |

---

## Proposed Deepening Resume Sequence

### Tier 1 (after machinery R1-R8): FODS, FODT
- Focus: Python write capability, SAL-to-export proof, Gate 11 packet
- Duration: 2-3 sprints

### Tier 2 (after ODS/ODT backfill): ODS, ODT
- Focus: spec stubs, parser depth, neutral model
- Duration: 2-3 sprints after backfill

### Tier 3 (after non-XML canonical naming): CSV, DIF, SYLK, NDJSON, TSV
- Focus: canonical naming registry, spec stubs, basic load/save
- Duration: 1-2 sprints per format

### Tier 4 (after SAL facts): ZST, XCF, FODG, binary formats
- Focus: SAL fact generation, spec stubs, capability expansion
- Duration: 2-3 sprints per format

---

## Format-Completion-Matrix Recommended Updates

The current `format-completion-matrix.yaml` shows both FODS and FODT as `production_track_real`.
This is overclaiming — the correct rating based on evidence:

| Format | Current Matrix | Evidence-Based Rating |
|--------|---------------|----------------------|
| FODS (Python) | production_track_real | read_only_library_foundation (no write, no export from Python) |
| FODS (.NET) | G11-E prototype | commercial_candidate (load/edit/save/export verified) |
| FODT (Python) | production_track_real | read_only_library_foundation |
| FODT (.NET) | G11-E prototype | commercial_candidate |
| ODS | read_write_library_foundation | read_write_library_foundation (correct) |
| ODT | read_only_prototype | read_only_prototype (correct) |
| ZST | export_capable_library | read_only_prototype (overclaim) |
| Others | Various | Most are probe_only or read_only_prototype |

---

## Gate 11 Closest Candidates

1. **FODS .NET** — load/edit/save/export fully implemented, 611 tests; nearest to C1-C20 complete
2. **FODT .NET** — similar depth; 567 tests
3. **FODS Python** — read-only but strong; nearest to P1-P11 complete for FOSS track

Recommended first Gate 11 attempt: **FODS .NET** (commercial track, most capability coverage)
