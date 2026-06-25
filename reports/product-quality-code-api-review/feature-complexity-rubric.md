# Feature Complexity Rubric

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Scores how complex (deep, comprehensive, and production-grade) a product's feature
implementation is — not whether features exist, but how sophisticated they are.

---

## Complexity Levels (C0–C5)

| Level | Label | Criteria |
|-------|-------|---------|
| **C0** | Absent | Feature not implemented; absent or raises NotImplementedError |
| **C1** | Trivial | Hardcoded or passthrough behavior; minimal real implementation |
| **C2** | Simple | Basic happy-path only; real parsing/modeling but no variants |
| **C3** | Structured | Multiple format variants handled; error paths; real model depth |
| **C4** | Advanced | Edge cases, roundtrip, stream support, multiple overloads, culture-invariant handling |
| **C5** | Professional | Streaming + bulk + parallel; exhaustive error handling; conformance suite tested; production-proven |

---

## C-Level Scoring Criteria Detail

### C0 — Absent

Examples:
- ZST .NET compress/decompress (no ZstWriter exists)
- FODP Python write (no write_fodp function)
- ABW Python Markdown export (no implementation)

Score requirements: Feature name is not callable from public API OR raises stub exception.

### C1 — Trivial

Examples:
- NDJSON .NET filter (returns subset of raw JsonElement list — no typed access)
- FODG Python write (wraps dict into minimal XML — no validation)
- TSV .NET save (writes raw string join with tabs — no quoting)

Score requirements: Feature callable; produces some output; but behavior is hardcoded or delegates everything to framework.

### C2 — Simple

Examples:
- CSV .NET parse (splits by comma; handles basic quoting; single-sheet only)
- SYLK Python parse (reads SLK format; returns flat cell list; no formula support)
- QOI Python encode (produces valid QOI binary; no compression level control)

Score requirements: Real domain logic present; handles common case; no edge case handling.

### C3 — Structured

Examples:
- FODS Python roundtrip (parse → model → edit → write; real XML DOM; partial formula support)
- PBM Python parse (P1/P4 ASCII and binary; error hierarchy; security bounds)
- ZST Python compress (real Zstandard compression; decompress verified; no stream API)

Score requirements: Multiple format variants; custom error types; real model (not raw dict); basic roundtrip.

### C4 — Advanced

Examples:
- FODS .NET cell operations (SetCellValue, SetCellFormula, SetCellStyle, MergeCells; culture-invariant; sort+filter)
- NetPBM .NET transforms (FlipH, FlipV, Crop, Resize, Rotate, filters; stream load)
- FODT .NET export (HTML, Markdown, TXT, PDF, PNG exporters; paragraph + heading + list support)

Score requirements: Edge cases explicitly handled; roundtrip verified; stream overloads; at least one non-trivial algorithm.

### C5 — Professional

Examples (aspirational for Format Factory):
- FODS .NET at C5 would add: async load, streaming parse for large files, culture-invariant across all operations, full ODF 1.3 spec conformance including extended attributes
- FODT .NET at C5 would add: embedded font handling, nested table support, tracked changes, review comments

Score requirements: Streaming; parallel operations; conformance suite tested; no known correctness gaps; documentation matches implementation.

---

## Feature Complexity Scores — Format Factory

### .NET Products

| Feature Domain | FODS | FODT | NetPBM | NDJSON | CSV | TSV | ZST |
|---------------|------|------|--------|--------|-----|-----|-----|
| Parse/Load | C4 | C4 | C4 | C3 | C2 | C2 | C2 |
| Edit/Mutate | C4 | C4 | C4 | C1 | C1 | C0 | C0 |
| Save/Write | C4 | C4 | C4 | C3 | C2 | C2 | C0 |
| Export | C4 | C4 | C3 | C3 | C0 | C3 | C0 |
| Error handling | C4 | C4 | C4 | C3 | C1 | C3 | C3 |
| **Overall** | **C4** | **C4** | **C4** | **C3** | **C2** | **C2** | **C1** |

### Python Products

| Feature Domain | FODS | FODT | ODS | ODT | PBM | ZST | FODP |
|---------------|------|------|-----|-----|-----|-----|------|
| Parse/Load | C4 | C4 | C3 | C3 | C4 | C3 | C2 |
| Edit/Mutate | C3 | C3 | C2 | C2 | C2 | C3 | C0 |
| Save/Write | C3 | C3 | C3 | C3 | C2 | C3 | C0 |
| Export | C3 | C4 | C2 | C1 | C3 | C0 | C0 |
| Error handling | C3 | C3 | C2 | C2 | C4 | C2 | C1 |
| **Overall** | **C3** | **C3-C4** | **C3** | **C2-C3** | **C4** | **C3** | **C1** |

---

## Complexity Band Definitions

| Band | C-Level | Meaning |
|------|---------|---------|
| Demo | C0-C1 | Not usable for real work |
| Basic | C2 | Happy-path only; demo scenarios |
| Practical | C3 | Useful for real use cases |
| Professional | C4 | Production-grade with edge cases |
| Exemplary | C5 | Best-in-class; specification-conformant |

---

## Highest and Lowest Complexity Products

**Highest overall:** FODS .NET (C4), FODT .NET (C4), NetPBM .NET (C4), PBM Python (C4)

**Lowest overall:** ZST .NET (C1), FODP Python (C1), CSV .NET (C2), TSV .NET (C2)

**Gap requiring immediate fix:** ZST .NET is C1 (compress=C0) — critical for a compression library.
