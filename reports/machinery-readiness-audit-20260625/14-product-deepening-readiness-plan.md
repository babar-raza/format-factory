# Lane J: Product Deepening Readiness Plan
# Sprint: ff-machinery-readiness-audit-20260625

## Product Deepening Mission Definition

Product deepening = advancing each format from its current PROOF_LEVEL to the next level,
ultimately reaching Gate 11 readiness. Levels:
- PROOF_LEVEL_1: parse + basic property extraction
- PROOF_LEVEL_2: roundtrip + write
- PROOF_LEVEL_3: export (CSV/JSON/HTML/Markdown)
- PROOF_LEVEL_4: consumer roundtrip + dogfood example
- PROOF_LEVEL_5: spec-parity verified + QName fully backfilled
- GATE_11_READY: all 8 customer criteria + commercial sign-off

## Current State: 14 Python FOSS Formats at PROOF_LEVEL_4+

From MEMORY.md (2026-06-25, Product Deepening Mission COMPLETE):
> "14 Python FOSS formats all at PROOF_LEVEL_4+. All consumer_roundtrip.py examples created and
> CONSUMER_PROOF: PASS."

| Format | Current Level | Consumer Proof | Next Level Gap |
|---|---|---|---|
| FODS | GATE_11_READY | PASS | Commercial sign-off (TRUE_EXTERNAL_GATE) |
| FODT | GATE_11_READY | PASS | Commercial sign-off (TRUE_EXTERNAL_GATE) |
| PBM | GATE_11_READY | PASS | Commercial sign-off (TRUE_EXTERNAL_GATE) |
| PGM | GATE_11_READY | PASS | Commercial sign-off (TRUE_EXTERNAL_GATE) |
| PPM | GATE_11_READY | PASS | Commercial sign-off (TRUE_EXTERNAL_GATE) |
| CSV | PROOF_LEVEL_4 | PASS | Analytics separation (LOC healing) → LEVEL_5 |
| NDJSON | PROOF_LEVEL_4 | PASS | NdjsonField facade → spec-parity → LEVEL_5 |
| TSV | PROOF_LEVEL_4 | PASS | Spec-parity verification → LEVEL_5 |
| GNUMERIC | PROOF_LEVEL_4 | PASS | Masquerade fix + spec-parity → LEVEL_5 |
| SYLK | PROOF_LEVEL_4 | PASS | SylkDocument spec_qname + writer test → LEVEL_5 |
| TOML | PROOF_LEVEL_4 | PASS | config_document.py fix + spec-parity → LEVEL_5 |
| ZST | PROOF_LEVEL_4 | PASS | ZstDocument spec-parity tests → LEVEL_5 |
| ABW | PROOF_LEVEL_4 | PASS | Complete 170-symbol backfill → LEVEL_5 |
| DIF | PROOF_LEVEL_4 | PASS | LOC healing (mixed model) → LEVEL_5 |

**6 formats not yet at PROOF_LEVEL_4:**

| Format | Current Level | Key Blocker |
|---|---|---|
| ODS | PROOF_LEVEL_3 | Limited roundtrip proof, no consumer roundtrip |
| ODT | PROOF_LEVEL_3 | Writer + limited test coverage |
| XCF | PROOF_LEVEL_3 | At LOC cap (5 LOC headroom only) |
| FODG | PROOF_LEVEL_3 | Monolith (3176 LOC), no decomposition |
| FODP | PROOF_LEVEL_2 | Read-only (no writer), no roundtrip |
| QOI | PROOF_LEVEL_2 | Limited implementation |

---

## Proof-of-Concept: Spec-to-Library-to-Export

The key demonstration we need: spec fact → domain model class → library API → export output.

Best candidates for this pilot:

### Pilot A: NDJSON (Simple, Best-Supported)

**Why NDJSON:**
- NdjsonRecord authority class exists with spec_qname="ndjson:record"
- 2 SAL facts in cache (FACT-NDJSON-001, FACT-NDJSON-002)
- Clean domain model (NdjsonDocument in models.py)
- 1409 tests pass; analytics extracted (ndjson_analytics.py)
- Minimal spec complexity (single-page spec at ndjson.org)

**Pilot proof path:**
```
FACT-NDJSON-001 (ndjson:record definition)
  → NdjsonRecord.spec_qname = "ndjson:record"
  → NdjsonDocument.records: list[NdjsonRecord] (domain model)
  → load_ndjson(path) → list[dict] (parser)
  → write_ndjson(records, path) (writer)
  → Consumer proof: load → mutate → write → reload → verify
```

**Status: PILOT_A_READY** — all components exist, just needs linkage documentation

### Pilot B: GNUMERIC (Complex Workbook Hierarchy)

**Why GNUMERIC:**
- GnumericDocument in models.py with spec_qname="gnumeric:workbook"
- GnumericSheet spec class with spec_qname="gnumeric:sheet"
- Complex hierarchy: workbook → sheets → cells (map to Gap IDs)
- Consumer roundtrip PASS (2026-06-25)
- Tests: 150+ pass

**Pilot proof path:**
```
gnumeric:workbook (workbook-level facts)
  → GnumericDocument.spec_qname = "gnumeric:workbook"
  → GnumericDocument.sheets: list[GnumericSheet]
  → load(path) → dict (parser)
  → write_gnumeric(model, path) (writer)
  → Export: export_to_csv(path), export_to_json(model)
```

**Status: PILOT_B_READY** — needs SAL facts for Gnumeric (currently CHAIN_BROKEN_AT_SAL)
Gap: No spec-derived facts for Gnumeric workbook hierarchy; would need MANUAL fact seeding

### Pilot C: ODS (ODF Heritage, SAL CHAIN_INTACT)

**Why ODS:**
- SAL CHAIN_INTACT — spec facts CAN be extracted automatically
- ODF spec is the richest format spec (thousands of sections)
- ODS shares ODF infrastructure with FODS (already Gold Standard)
- FODS has 4988 SAL facts — ODS can leverage same pipeline
- OdsRow.spec_qname = "table:table-row" (ClassVar — FIXED 2026-06-24)

**Pilot proof path:**
```
FACT-ODS-NNN (table:table-row from ODF spec)
  → OdsRow.spec_qname = "table:table-row"
  → OdsDocument → sheets → rows → cells
  → ods_parser.parse_ods(path)
  → write_ods (to be verified/built)
  → set_cell_value, add_row, rename_sheet functions
  → Consumer roundtrip proof
```

**Status: PILOT_C_READY** — needs consumer roundtrip proof and write_ods verification

---

## Product Deepening Sequence

### Wave A: Gate 11 Pending (no agent work needed)
Formats: FODS, FODT, PBM, PGM, PPM
Action: Wait for Babar Raza commercial sign-off + publication credentials

### Wave B: PROOF_LEVEL_4 → PROOF_LEVEL_5 (spec-parity)
Formats: CSV, NDJSON, TSV, SYLK, ZST, TOML, GNUMERIC, ABW, DIF
Prerequisite: SAL-REPAIR-001 (prove fact extraction for 1 non-ODF format)
Prerequisite: QNAME-BACKFILL-PILOT-001 (3 format backfill inventories)
Action per format: Complete backfill migration + V53 compliance + spec_fact_refs

### Wave C: PROOF_LEVEL_3 → PROOF_LEVEL_4
Formats: ODS, ODT, XCF, FODG
Prerequisite: For ODS/ODT — SAL is CHAIN_INTACT (can proceed now)
Prerequisite: For XCF — must resolve LOC cap (decompose xcf_parser.py)
Prerequisite: For FODG — must decompose monolith (3176 LOC)
Action: Consumer roundtrip proof + dogfood example per format

### Wave D: PROOF_LEVEL_2 → PROOF_LEVEL_3
Formats: FODP, QOI
Prerequisite: For FODP — needs write_fodp() implementation
Action: Add export functions + roundtrip proof

---

## Readiness Prerequisites Summary

For product deepening to produce SPEC-BACKED results (not ad-hoc):

| Prerequisite | Status | Blocks |
|---|---|---|
| SAL fact extraction for 1 non-ODF format | NOT STARTED | Wave B all formats |
| Backfill system (5 modules) | NOT STARTED | Wave B quality |
| EXPANSION_GOALS → gap-ledger-driven | NOT STARTED | Wave B task selection |
| Feature compiler Phase 1 | NOT STARTED | Gap→taskcard automation |
| V43 FAIL mode for implementing formats | NOT STARTED | Wave B enforcement |
| Lane DAG code-enforced pre-check | NOT STARTED | Wave A-D collision prevention |

**Conclusion:** Wave B (PROOF_LEVEL_5 advancement) requires machinery repairs first.
Wave C (PROOF_LEVEL_4 for ODS/ODT) CAN proceed immediately — SAL is CHAIN_INTACT for ODF.
Wave D (FODP/QOI) CAN proceed immediately — add writer + exports (no SAL required for basic proofs).

---

## Product Deepening Pilot Execution Plan

### Immediate (no machinery repairs needed):

**PILOT-ODS-001:** ODS consumer roundtrip proof
- Read samples/by-format/ods/valid/minimal.ods
- set_cell_value, add_row, rename_sheet operations
- write_ods (verify or implement)
- Create examples/python/ods/ods_consumer_roundtrip.py

**PILOT-ODT-001:** ODT consumer roundtrip completeness
- odt_from_text + odt_from_model already implemented
- Expand tests to 40+
- Create examples/python/odt/odt_consumer_roundtrip.py (verify exists)

### After SAL-REPAIR-001 completes:

**PILOT-CSV-SPEC-001:** CSV spec-parity proof
- Wire SAL to extract CSV spec facts (RFC 4180 §2.1 etc.)
- Map facts → CsvRecord.spec_qname = "csv:record"
- Run V53 compliance verification
- Declare PROOF_LEVEL_5 for CSV

### After feature compiler Phase 1 completes:

**PILOT-NDJSON-COMPILER-001:** NDJSON spec→feature proof
- Input: GAP-NDJSON-* from gap-ledger.json
- Feature compiler generates taskcard skeleton with spec_fact_refs
- Agent executes taskcard (adds feature to ndjson library)
- Evidence: compiler was the source of taskcard, not _EXPANSION_GOALS
