# Product Deepening Execution Plan
# Sprint: ff-machinery-readiness-audit-20260625

## Authorization Status

**Current status:** AUTHORIZED for Wave C targets only (ODS, ODT)
**Wave B (spec-parity deepening):** BLOCKED pending SAL-REPAIR-001
**Wave D (FODP/QOI):** AUTHORIZED — no SAL dependency for basic PROOF_LEVEL_3 work

This plan defines the execution sequence, format priority, and skill invocations
for product deepening once machinery repairs complete.

---

## Immediate Work (No Machinery Repairs Required)

### PILOT-ODS-001: ODS Consumer Roundtrip

**Authorization:** AUTHORIZED NOW — ODS has SAL CHAIN_INTACT (ODF spec)
**Target level:** PROOF_LEVEL_4

Steps:
1. Read examples/python/ods/ — check if roundtrip example exists
2. Read src/python/ods/ods_parser.py — verify set_cell_value, add_row, write_ods available
3. Create examples/python/ods/ods_consumer_roundtrip.py using /add-installed-package-example skill
4. Add 5+ tests in tests/python/ods/ using /add-roundtrip-test skill
5. Declare PROOF_LEVEL_4 for ODS in product-deepening-ledger.yaml

**Expected API (from ODS format notes):**
```python
from ods import load_ods, set_cell_value, add_row, rename_sheet, write_ods
model = load_ods(src_path)
set_cell_value(model, sheet_index=0, row=0, col=0, value="CONSUMER_PROOF")
add_row(model, sheet_index=0, values=["A", "B", "C"])
rename_sheet(model, old_name="Sheet1", new_name="Proof")
write_ods(model, dest_path)
```

### PILOT-ODT-001: ODT Consumer Roundtrip Completeness

**Authorization:** AUTHORIZED NOW
**Target level:** PROOF_LEVEL_4 verification

Steps:
1. Verify examples/python/odt/dogfood_odt_roundtrip.py exists (MEMORY.md: created 2026-06-24)
2. Expand tests to 40+ (currently ~19)
3. Create examples/python/odt/odt_consumer_roundtrip.py if distinct from dogfood proof
4. Update product-deepening-ledger.yaml: ODT → PROOF_LEVEL_4

### PILOT-FODP-001: FODP Read-Only Proof

**Authorization:** AUTHORIZED NOW — read-only proof requires no writer
**Target level:** PROOF_LEVEL_3 (read + inspect + analytics)

Steps:
1. FODP is read-only (no write_fodp) — proof = load + inspect + analytics
2. Create examples/python/fodp/fodp_consumer_proof.py:
   - load(path) → model dict
   - get_page_count(path), fodp_slide_count(path)
   - fodp_titles(path) → list of slide titles
3. Tests: 10+ tests in tests/python/fodp/

---

## Wave B Execution (After SAL-REPAIR-001 Complete)

### Format Priority Order

Based on: spec complexity, test count, current gap count, strategic value

| Priority | Format | Current Level | Gap to Level 5 | Notes |
|---|---|---|---|---|
| 1 | NDJSON | 4 | Spec-parity proof | Simplest schema; authority class exists |
| 2 | CSV | 4 | Analytics separation + spec proof | RFC 4180 — SAL-REPAIR-001 target |
| 3 | TSV | 4 | Spec-parity proof | Near-identical to CSV pattern |
| 4 | SYLK | 4 | spec_qname on SylkDocument | Small fix; high leverage |
| 5 | ZST | 4 | ZstDocument spec-parity tests | ZstDocument already has spec_qname |
| 6 | TOML | 4 | config_document masquerade fix | Fix masquerade first |
| 7 | GNUMERIC | 4 | workbook_document masquerade fix | Fix masquerade first |
| 8 | ABW | 4 | Complete 170-symbol backfill | Needs QNAME-BACKFILL-PILOT + ABW phase |
| 9 | DIF | 4 | LOC healing + writer test | Mixed model at cap |

### Per-Format Sprint Design

#### NDJSON Spec-Parity Sprint

Taskcard: derived from GAP-NDJSON-* entries in gap-ledger.json
Skill: /add-python-api

Steps:
1. Read sal-facts-ndjson.json (currently has FACT-NDJSON-001)
2. Verify NdjsonRecord.spec_qname="ndjson:record" and NdjsonDocument in models.py
3. Run /python-qname-code-reviewer for NDJSON format
4. Add NdjsonField to Compat/ (GAP-NDJSON-FIELD per Phase 1 evidence)
5. Declare PROOF_LEVEL_5 with evidence of FACT-NDJSON-001 in spec_fact_refs

Evidence files:
- tests/python/ndjson/test_ndjson_spec_qname.py (12 tests; existing)
- shared/qname-registry/ndjson.yaml (verified)
- .local/spec-cache/sal-facts-ndjson.json

#### CSV Spec-Parity Sprint (requires SAL-REPAIR-001)

Taskcard: from SAL-REPAIR-001 output (FACT-CSV-001 through FACT-CSV-005)
Skill: /add-python-api

Steps:
1. Confirm sal-facts-csv.json has FACT-CSV-NNN entries (SAL-REPAIR-001 proof)
2. Verify CsvRecord in spec/ has spec_qname="csv:record"
3. Analytics separation: move remaining analytics from csv_parser.py → csv_analytics.py
4. Declare PROOF_LEVEL_5

---

## Wave C Execution (XCF, FODG — After LOC Healing)

### XCF Decomposition Sprint

**Prerequisite:** xcf_parser.py is at 1272/1277 (5 LOC headroom only)
**Required action:** Decompose xcf_parser.py further before any product deepening

Skill: /decompose-monolithic-codec or /extract-analytics-from-monolith
Steps:
1. Identify lowest-LOC analytical functions in xcf_parser.py
2. Move them to xcf_analytics.py (which already exists at 4773 LOC — check if XCF analytics.py has room)
3. After healing: consumer roundtrip example + tests

### FODG Decomposition Sprint

**Prerequisite:** fodg_codec.py at 3176 LOC (FODG analytics was healed 2026-06-18 per MEMORY.md)
**Question:** Was FODG already healed? MEMORY.md says "fodg_analytics.py 3214 LOC (extracted)"
**Check first:** Verify current state of src/python/fodg/fodg_codec.py LOC before sprint

---

## Wave D Execution (FODP/QOI — Immediate)

### FODP: Add Python Writer

**Current state:** No write_fodp function (read-only proof only)
**Path:** ODP (OpenDocument Presentation) format — complex ZIP+XML
**Decision point:** Is a write_fodp() feasible without ODF SAL facts? Probably yes for a minimal proof.

Minimal approach:
- Copy/read an existing FODP → modify text_content in memory → write back using XML rebuild
- Must NOT break existing FODP parser tests

---

## Product Deepening Progress Ledger

| Format | Level Before Audit | Level After Wave C/D | Gate 11 ETA |
|---|---|---|---|
| FODS | GATE_11_READY | GATE_11_READY | TRUE_EXTERNAL_GATE |
| FODT | GATE_11_READY | GATE_11_READY | TRUE_EXTERNAL_GATE |
| PBM/PGM/PPM | GATE_11_READY | GATE_11_READY | TRUE_EXTERNAL_GATE |
| CSV | 4 | 5 (after REPAIR-02) | +4 sprints |
| NDJSON | 4 | 5 (immediate) | +3 sprints |
| TSV | 4 | 5 (after REPAIR-02) | +4 sprints |
| GNUMERIC | 4 | 5 (after REPAIR-05) | +5 sprints |
| SYLK | 4 | 5 (after REPAIR-05) | +5 sprints |
| TOML | 4 | 5 (after REPAIR-05) | +5 sprints |
| ZST | 4 | 5 (after REPAIR-03) | +4 sprints |
| ABW | 4 | 5 (after ABW backfill) | +6 sprints |
| DIF | 4 | 5 (after SRC-STD-001) | +5 sprints |
| ODS | 3 | 4 (immediate) | +6 sprints |
| ODT | 3 | 4 (immediate) | +6 sprints |
| XCF | 3 | 4 (after decomp) | +7 sprints |
| FODG | 3 | 4 (verify healed) | +7 sprints |
| FODP | 2 | 3 (immediate) | +8 sprints |
| QOI | 2 | 3 (+1 sprint) | +9 sprints |

---

## Decision Gates Before Each Wave

Before starting any product sprint, agent must check:
1. `check_continuation.py` returns CONTINUE
2. Target format has gap_ledger_ref available for work items
3. Target format has CHAIN_INTACT or SAL-REPAIR-001 closed
4. Source file LOC is below cap (check source-structure-baseline.json)
5. No GOV_BLOCK rework items in continuation signal

If all 5 conditions met: execute sprint.
If any condition fails: address blocker first.
