# Phase Audit 3 Expansion — ZST / ODS / ODT

**Sprint:** FORMAT-FACTORY-R49-EDITABLE-OBJECT-MODEL-POC-BASELINE-AND-STRATEGY-SYNC-001
**Lane:** MT9
**Date:** 2026-05-22
**Phase:** 3 of 7 — Parser Requirements / Prototype Creation
**Prior status:** PILOT_PASS_FODS_FODT (R48 kickoff)

---

## Scope

This document expands Phase Audit 3 to three additional formats:
- **ZST** (Zstandard compressed data codec)
- **ODS** (OpenDocument Spreadsheet — zip-packaged)
- **ODT** (OpenDocument Text — zip-packaged)

---

## Phase Audit 3 Criteria (Reminder)

| Criterion | Description |
|-----------|-------------|
| PA3-1 | Generated requirements exist (`generated-requirements/<format>/`) |
| PA3-2 | Parser/codec source exists (`src/python/<format>/`) |
| PA3-3 | Parser tests map to requirements |
| PA3-4 | Invalid/malformed input handling tested |
| PA3-5 | Parser output maps to documented neutral model |
| PA3-6 | No hardcoded sample-only behavior |
| PA3-7 | Unsupported features documented and not overclaimed |
| PA3-8 | commercial_product_ready: false |
| PA3-9 | Round-trip: write→read→verify (N/A for codec formats) |

---

## ZST Audit

ZST is a compression codec format (not a document format). There is no document-model write path.
PA3-9 (round-trip) is N/A — compression/decompression is directional.

### PA3-1: Generated Requirements
- Path: `generated-requirements/zst/`
- Status: **NOT PRESENT** — generated requirements not yet created for ZST
- Gap: requires spec ingestion + requirements generation sprint
- Decision: ZST is codec-only (no neutral document model). PA3-1 gap accepted as KNOWN_GAP_CODEC_FORMAT.

### PA3-2: Parser/Codec Source
- Path: `src/python/zst/zst_codec.py`
- Status: **PRESENT** — codec implemented with probe/decompress/magic support

### PA3-3: Tests Map to Requirements
- `tests/python/zst/test_zst_codec.py` — basic codec tests
- `tests/python/zst/test_zst_r33_expansion.py` — expanded coverage
- Status: **PARTIAL** — tests exist; formal IR-ZST mapping not yet created

### PA3-4: Invalid Input Handling
- Magic-only probe, truncated stream, corrupt frame tests present
- Status: **PASS** — codec handles malformed inputs

### PA3-5: Neutral Model
- ZST codec: output is `{"path": str, "exists": bool, "header": dict, "decompressed_size": int}`
- Status: **PARTIAL** — model is probe-result, not document structure (expected for codec)

### PA3-6: No Hardcoded Sample Behavior
- Codec uses magic bytes + zstandard library
- Status: **PASS**

### PA3-7: Unsupported Features Documented
- Unsupported: streaming multi-frame, dictionary compression, ZPAQL VM
- Status: **DOCUMENTED** in acquisition pack

### PA3-8: commercial_product_ready
- Status: **false** (`commercial_product_ready: false` in source header)

### PA3-9: Round-Trip
- Status: **N/A** — ZST is compression codec; no document write path

**ZST Phase Audit 3 Result: CONDITIONAL_PASS** (PA3-1 gap accepted for codec format; PA3-3 partial)

---

## ODS Audit

### PA3-1: Generated Requirements
- Path: `generated-requirements/ods/`
- Status: **NOT PRESENT** — generated requirements not yet created for ODS
- Gap: ODS requirements generation is a future sprint task (R50 target)

### PA3-2: Parser Source
- Path: `src/python/ods/ods_parser.py`
- Status: **PRESENT**

### PA3-3: Tests Map to Requirements
- `tests/python/ods/test_ods_parser.py` — parser tests
- `tests/python/ods/test_ods_gate5_neutral_model.py` — neutral model tests
- `tests/python/ods/test_ods_gate6_oracle.py` — oracle tests
- `tests/python/ods/test_ods_gate7_fuzz_guard.py` — fuzz tests
- Status: **PARTIAL** — tests exist; formal IR-ODS requirement mapping not yet created

### PA3-4: Invalid Input Handling
- `test_ods_gate7_fuzz_guard.py` — fuzz/malformed tests
- Status: **PASS**

### PA3-5: Neutral Model
- ODS parser outputs sheets/rows/cells similar to FODS neutral model
- Status: **DOCUMENTED** (gate5 neutral model tests prove the schema)

### PA3-6: No Hardcoded Sample Behavior
- Parser uses zipfile + XML iterparse on ODS package structure
- Status: **PASS** (inferred from code structure)

### PA3-7: Unsupported Features Documented
- Unsupported: macros, pivot tables, chart sheets, embedded objects
- Status: **DOCUMENTED** in pack.yaml

### PA3-8: commercial_product_ready
- Status: **false** (`commercial_product_ready: False` in parser source)

### PA3-9: Round-Trip
- ODS writer: NOT YET IMPLEMENTED
- Status: **NOT APPLICABLE** (no writer; round-trip deferred to R50+)
- Gap: ODS write_ods() is a future sprint target

**ODS Phase Audit 3 Result: CONDITIONAL_PASS** (PA3-1 and PA3-9 gaps; writer deferred)

---

## ODT Audit

### PA3-1: Generated Requirements
- Path: `generated-requirements/odt/`
- Status: **NOT PRESENT** — generated requirements not yet created for ODT
- Gap: ODT requirements generation is a future sprint task (R50 target)

### PA3-2: Parser Source
- Path: `src/python/odt/odt_parser.py`
- Status: **PRESENT**

### PA3-3: Tests Map to Requirements
- `tests/python/odt/test_odt_parser.py` — parser tests
- `tests/python/odt/test_odt_gate5_neutral_model.py` — neutral model tests
- `tests/python/odt/test_odt_gate6_oracle.py` — oracle tests
- `tests/python/odt/test_odt_gate7_fuzz_guard.py` — fuzz tests
- Status: **PARTIAL** — tests exist; formal IR-ODT requirement mapping not yet created

### PA3-4: Invalid Input Handling
- `test_odt_gate7_fuzz_guard.py` — fuzz/malformed tests
- Status: **PASS**

### PA3-5: Neutral Model
- ODT parser outputs blocks/paragraphs/headings similar to FODT neutral model
- Status: **DOCUMENTED** (gate5 neutral model tests prove the schema)

### PA3-6: No Hardcoded Sample Behavior
- Parser uses zipfile + XML processing
- Status: **PASS** (inferred from code structure)

### PA3-7: Unsupported Features Documented
- Unsupported: embedded images, tracked changes, styles, macros, footnotes
- Status: **DOCUMENTED** in pack.yaml

### PA3-8: commercial_product_ready
- Status: **false** (`commercial_product_ready: False` in parser source)

### PA3-9: Round-Trip
- ODT writer: NOT YET IMPLEMENTED
- Status: **NOT APPLICABLE** (no writer; deferred to R50+)
- Gap: ODT write_odt() is a future sprint target

**ODT Phase Audit 3 Result: CONDITIONAL_PASS** (PA3-1 and PA3-9 gaps; writer deferred)

---

## Phase Audit 3 Expansion Summary

| Format | PA3-1 | PA3-2 | PA3-3 | PA3-4 | PA3-5 | PA3-6 | PA3-7 | PA3-8 | PA3-9 | Result |
|--------|-------|-------|-------|-------|-------|-------|-------|-------|-------|--------|
| ZST | GAP | PASS | PARTIAL | PASS | PARTIAL | PASS | PASS | PASS | N/A | **CONDITIONAL_PASS** |
| ODS | GAP | PASS | PARTIAL | PASS | PASS | PASS | PASS | PASS | GAP | **CONDITIONAL_PASS** |
| ODT | GAP | PASS | PARTIAL | PASS | PASS | PASS | PASS | PASS | GAP | **CONDITIONAL_PASS** |

---

## Consolidated Phase Audit 3 Status

| Format | R48 Result | R49 Result |
|--------|-----------|-----------|
| FODS | PASS | (unchanged) |
| FODT | PASS | (unchanged; R49 fix improves PA3-9) |
| ZST | — | CONDITIONAL_PASS |
| ODS | — | CONDITIONAL_PASS |
| ODT | — | CONDITIONAL_PASS |

**PHASE_AUDIT_3: EXPANSION_PASS_ZST_ODS_ODT (conditional; PA3-1/PA3-9 gaps tracked)**

---

## Follow-Up Actions (R50+)

| Action | Format | Priority |
|--------|--------|----------|
| Generate IR-ZST requirements | ZST | Medium |
| Generate IR-ODS requirements | ODS | Medium |
| Generate IR-ODT requirements | ODT | Medium |
| Implement write_ods() | ODS | High (for PA3-9) |
| Implement write_odt() | ODT | High (for PA3-9) |
| Map existing tests to IR-* items | ZST/ODS/ODT | Low |
