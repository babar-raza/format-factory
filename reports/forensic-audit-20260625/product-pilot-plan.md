# Product Pilot Plan

**Sprint/Run ID:** ff-archaeology-20260625

---

## Purpose

A pilot is a full spec→SAL→capability→feature→source→test→export proof for a single format.
It demonstrates that the machinery produces professional, repeatable, maintainable libraries —
not just parsers that work once.

Four formats are selected as pilots because they represent the full range of format categories
and machinery maturity levels.

---

## Pilot 1: FODS (.NET + Python) — Commercial Pilot

**Status:** PILOT_READY (highest maturity)
**Gate 11 sub-gate:** APPROVED (2026-06-05)

### Evidence of Pilot Readiness

| Criterion | Python | .NET |
|-----------|--------|------|
| Domain model class | FodsDocument (models.py) | FodsDocument (FodsDocument.cs) |
| spec_qname | office:document (ClassVar) | const SpecQName |
| SAL facts | 5,013 (FACT-FODS-001..5013) | same |
| Capability records | 92% coverage | same |
| Compat/ facades | FodsDocument, FodsSheet, FodsCell | FodsDocument.cs (Compat layer) |
| spec/ hierarchy | office/, table/, text/ directories | Spec/Table/, Spec/Text/ |
| Tests | 93 Python + 638 .NET = 731 total | |
| Exporter | .NET: CSV, HTML, JSON, PNG, PDF(stub) | |
| Writer | Python: write_fods() | |

### Pilot Proof Steps (FODS)

1. **Load:** `FodsDocument.from_file("sample.fods")` → typed Python object
2. **Inspect:** `.sheet_count`, `.get_cell(0, 0, 0)`, `.headers` → all return typed values
3. **Edit:** Modify cell via Python neutral model → write_fods() → re-load → verify change
4. **Export (.NET):** `FodsDocument.Load("sample.fods").ExportToCsv("out.csv")` → valid CSV
5. **Spec trace:** Show FACT-FODS-001 → capability record → domain model property chain
6. **QName trace:** `office:document` → `spec/office/document.py:OfficDocument` → `Compat/fods_document.py:FodsDocument`

### Pilot Success Criteria
- Round-trip: parse → edit → save → parse matches original (except modified cell)
- Export: output file validates as correct CSV/HTML
- Spec trace: at least 3 capability records trace to specific FACT-FODS-NNN IDs
- QName trace: all 3 Compat/ facades can be traced from spec/ class to qname-registry entry
- .NET test suite: 638 tests pass

**Pilot output:** `reports/pilots/fods/pilot-report.md` + evidence YAML

---

## Pilot 2: FODT (.NET + Python) — Word Processing Pilot

**Status:** PILOT_READY
**Gate 11 sub-gate:** APPROVED (2026-06-05)

### Evidence of Pilot Readiness

| Criterion | Python | .NET |
|-----------|--------|------|
| Domain model | FodtDocument (neutral_model.py) | FodtDocument.cs (977 LOC) |
| spec_qname | office:document | const SpecQName |
| SAL facts | 4,500+ | same |
| Capability records | 85% coverage | same |
| Analytics | fodt_document_edit.py, fodt_neutral_ops.py | — |
| Exporters | fodt_to_txt, fodt_to_markdown, fodt_to_html (exporters.py) | HTML, Markdown, PDF, PNG, TXT |
| Tests | 131 Python + partial .NET | |

### Pilot Proof Steps (FODT)

1. **Load:** `load("sample.fodt")` → neutral model dict (Python) / `FodtDocument.Load(path)` (.NET)
2. **Inspect:** `.paragraphs`, `.headings`, `.section_count`, `GetParagraphs()` → typed access
3. **Export (Python):** `fodt_to_markdown(path)` → valid Markdown with headings preserved
4. **Export (.NET):** `FodtDocument.Load(path).ExportToHtml("out.html")` → valid HTML
5. **Spec trace:** FODT spec section → SAL fact → capability entry → exporter function
6. **Round-trip:** load → append paragraph → write_fodt → reload → paragraph_count += 1

### Pilot Success Criteria
- Python export: Markdown output contains all headings from original document
- .NET export: HTML output is valid, contains paragraph text
- Round-trip: paragraph count increases by 1 after append+save+reload
- 131 Python tests pass

**Pilot output:** `reports/pilots/fodt/pilot-report.md`

---

## Pilot 3: ZST (Python) — Binary Format Pilot

**Status:** PILOT_READY

### Evidence of Pilot Readiness

| Criterion | Value |
|-----------|-------|
| Domain model | ZstDocument (models.py) |
| spec_qname | zst:frame (ClassVar) |
| SAL facts | 14 (minimal — binary format) |
| Capability records | 70% |
| Analytics | zst_analytics.py (4,604 LOC) — fully extracted |
| Writer | compress_string() / bytes write-through |
| Tests | 83 Python |

### Pilot Proof Steps (ZST)

1. **Compress:** `compress_string("hello world", level=3)` → bytes
2. **Write:** `open("out.zst", "wb").write(data)`
3. **Load:** `ZstDocument.from_file("out.zst")` → domain model
4. **Inspect:** `.compressed_size`, `.decompressed_size`, `.frame_count`, `.is_empty`
5. **Decompress:** `decompress_to_string(data)` → "hello world" (round-trip proof)
6. **Analytics:** `zst_compression_ratio(path)`, `zst_frame_count(path)` — both return valid values

### Pilot Success Criteria
- Round-trip: compress → write → load → decompress matches original string
- Domain model: ZstDocument.from_file() returns typed instance with all 6 properties
- Analytics: compression_ratio > 1.0 for typical text input
- 83 tests pass

**Pilot output:** `reports/pilots/zst/pilot-report.md`

---

## Pilot 4: NDJSON (Python) — Structured Data Pilot

**Status:** PILOT_READY

### Evidence of Pilot Readiness

| Criterion | Value |
|-----------|-------|
| Domain model | NdjsonDocument (models.py) |
| spec_qname | ndjson:record (NdjsonRecord authority class) |
| SAL facts | 0 (CHAIN_BROKEN_AT_SAL — text format) |
| Capability records | 75% |
| Analytics | ndjson_analytics.py (923 LOC) |
| Writer | write_ndjson(records, path) |
| Tests | 142 Python |

### Pilot Proof Steps (NDJSON)

1. **Load:** `NdjsonDocument.from_file("minimal.ndjson")` → typed document
2. **Inspect:** `.record_count`, `.records`, `.get_record(0)` → typed access
3. **Analytics:** `ndjson_has_uniform_types(records)`, `ndjson_null_ratio(records)` → float/bool
4. **Append:** `records.append({"name": "Pilot", "score": 99})` → write_ndjson()
5. **Reload:** `NdjsonDocument.from_file(path)` → `record_count` increased by 1
6. **QName trace:** `ndjson:record` → `NdjsonRecord` (authority class in ndjson_codec.py)

### Pilot Success Criteria
- Domain model: NdjsonDocument.from_file() returns typed instance with record_count, records, get_record()
- Round-trip: append + write + reload → record_count += 1
- Analytics: at least 5 analytics functions return valid results on sample file
- NdjsonRecord.spec_qname == "ndjson:record" (authority class)
- 142 tests pass

**Pilot output:** `reports/pilots/ndjson/pilot-report.md`

---

## Pilot Execution Order

| Priority | Format | Why First |
|----------|--------|-----------|
| 1 | FODS | Gate 11 candidate; richest machinery; largest test coverage |
| 2 | FODT | Gate 11 candidate; exporter diversity proof |
| 3 | NDJSON | Structured data canonical case; good analytics coverage |
| 4 | ZST | Binary format canonical case; compression round-trip proof |

Execute pilots 1 and 2 in parallel (independent formats).
Execute pilots 3 and 4 in parallel after 1+2 complete (validate general pattern, not just ODF).

---

## Pilot Report Schema

Each `reports/pilots/{format}/pilot-report.md` must contain:

```markdown
## Pilot: {FORMAT}
**Date:** YYYY-MM-DD
**Status:** PASS | FAIL | PARTIAL

### Load Test
- Input: {path}
- Result: {domain_class}.from_file() returned typed instance
- Properties verified: {list}

### Round-Trip Test
- Edit: {description}
- Verify: {assertion}
- Result: PASS | FAIL

### Export Test (if applicable)
- Exporter: {function}
- Output: {path}
- Validation: {method}
- Result: PASS | FAIL

### Spec Trace
- FACT-{FORMAT}-NNN → capability record {id} → {function/property}

### QName Trace
- {ns}:{name} → spec/{path}.py:{Class} → Compat/{facade}.py:{FacadeClass}

### Test Suite
- Total tests: N
- Passed: N
- Failed: 0
```

---

## Definition of Pilot Success

A pilot is **SUCCESSFUL** if all of:
1. Domain model `from_file()` returns typed instance with at least 3 typed properties
2. Round-trip edit+save+reload changes exactly what was expected
3. At least one export/serialization path works end-to-end
4. Spec trace connects at least 1 SAL fact (or gap ledger entry if SAL unavailable) to a code symbol
5. QName trace connects registry entry to spec/ class to Compat/ facade
6. All existing tests for that format pass

A pilot is **PARTIAL** if 4/6 criteria are met.
A pilot is **FAILED** if fewer than 4 criteria are met (requires machinery investigation before continuing).
