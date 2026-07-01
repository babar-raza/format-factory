# Tests

**Document type:** Directory Orientation — Phase 0 Foundation
**Last reviewed:** 2026-05-03

---

## Purpose

This directory contains test fixtures, oracle outputs, and fuzz seeds for all formats. These are not product test suites (those live in `src/`) — they are acquisition-layer testing artifacts that support prototype validation (Gate 4), oracle comparison (Gate 6), and fuzz testing (Gate 7).

---

## Directory Structure

```
tests/
+-- _readme.md                 This file
+-- fixtures/                  Static test inputs (created Phase 3, Gate 4)
|   +-- <format-id>/           Per-format fixtures
+-- oracle/                    Oracle comparison outputs (created Phase 3, Gate 6)
|   +-- <format-id>/           Per-format oracle outputs
+-- fuzz/                      Fuzz seeds (created Phase 3, Gate 7)
    +-- <format-id>/           Per-format fuzz seeds
        +-- minimal.ext        Minimal valid file
        +-- empty.ext          Empty/trivial file
        +-- truncated.ext      Truncated file
        +-- illegal-values.ext File with illegal values in key fields
        +-- oversized.ext      File with oversized length fields
```

All subdirectories under `tests/` are created in Phase 3. They do not exist in Phase 0.

---

## Test Fixtures (Gate 4)

Test fixtures are copies or symlinks of the sample corpus from `samples/by-format/<format-id>/`, potentially augmented with additional edge-case files needed for prototype testing. Fixtures must have the same license requirements as samples: all files must have confirmed provenance in `samples/_provenance.yaml`.

---

## Oracle Outputs (Gate 6)

Oracle outputs are the structured representation of a sample as produced by the oracle tool (e.g., LibreOffice). They capture "what the oracle thinks this file contains" so that the prototype parser output can be compared against it. Oracle outputs are generated artifacts (reproducible from the oracle tool + sample), so they are `visibility: internal` and `reusable: true` with `refresh_policy: tool-version-changed`.

---

## Fuzz Seeds (Gate 7)

Fuzz seeds are the starting inputs for the fuzz harness. They must include:
- A minimal valid file (smallest valid file the parser accepts).
- An empty file (zero bytes or a valid empty document).
- A truncated file (the minimal valid file cut at various points).
- A file with illegal values in key fields (e.g., negative cell index, invalid encoding).
- A file with oversized length fields (e.g., a cell count field set to INT_MAX).

The minimum fuzz iteration counts are defined in `docs/security.md`: 10,000 for XML formats; 100,000 for binary formats.

---

## Visibility

All files in `tests/` are `visibility: internal`. Test fixtures derived from CC-BY samples must carry attribution in their provenance entry.

---

## Relationship to Other Documents

- `docs/security.md` — fuzz testing requirements (Gate 7) and minimum iteration counts
- `docs/gates.md` — Gate 4 (prototype), Gate 6 (oracle), Gate 7 (fuzz) pass criteria
- `samples/_provenance.yaml` — license records for sample-derived fixtures
- `docs/python-foss/acquisition-workflow.md` — Stages 4, 6, 7 describe how these directories are used
