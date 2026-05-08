---
artifact_id: fods-gate8-security-report
artifact_type: report-security
path: reports/security/fods.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODS Gate 8 security review. Created run046 (2026-05-08). GATE8_SECURITY_REVIEW: PASS. Sign-off: Babar Raza 2026-05-08. TC-0038 DEC-034 inline verification PASS 20/20."
---

# Security Report — FODS Parser

**Format:** FODS (Flat OpenDocument Spreadsheet)
**Gate:** 8 — Security Review Complete
**Report date:** 2026-05-08
**Run:** run046
**Prepared by:** claude-sonnet-4-6 (run046)
**Parser reviewed:** `prototypes/by-format/fods/fods_parser.py` (Gate 4 prototype)
**Parser language:** Python 3 (stdlib only — `xml.etree.ElementTree`)

---

## Reviewer Sign-off

**GATE8_SECURITY_REVIEW: PASS**

| Field | Value |
|---|---|
| Sign-off | Babar Raza |
| Date | 2026-05-08 |
| Run | run046 |
| Gate status | 8 — APPROVED |
| TC-0038 DEC-034 | PASS 20/20 (run046 inline) |

---

## Threat Matrix

| # | Category | Status | Notes |
|---|---|---|---|
| TC-1 | XML External Entities (XXE) | **MITIGATED** | ElementTree/Expat blocks external entities by default (Python 3.8+) |
| TC-2 | DTD / Entity Expansion (Billion Laughs) | **MITIGATED** | Expat rejects DOCTYPE declarations; no entity expansion path |
| TC-3 | Zip Bombs / Decompression | **NOT-APPLICABLE** | FODS is flat XML — no ZIP container |
| TC-4 | Path Traversal in Archives | **NOT-APPLICABLE** | FODS is not archive-based; single file input only |
| TC-5 | Malformed File Handling | **MITIGATED** | Gate 7 PASS 18/18 — all malformed inputs handled safely |
| TC-6 | Memory Limits | **DEFERRED** | 100 MB file guard; ET.parse() non-streaming; deferred to Gate 10 |
| TC-7 | Recursion Limits | **MITIGATED** | Iterative traversal; Expat C-level handles XML nesting; Gate 7 deeply-nested PASS |
| TC-8 | Binary Parser Safety | **NOT-APPLICABLE** | FODS is pure XML; no binary parsing paths exist |

**Overall result: PASS** — All critical categories mitigated or not applicable.
One deferred item (TC-6 memory streaming) documented with explicit Gate 10 requirement.

---

## TC-1: XML External Entities (XXE)

**Status: MITIGATED**

**Evidence:**
- `fods_parser.py` uses `import xml.etree.ElementTree as ET` (Python stdlib).
- `ET.parse(str(path))` is called at the parse entry point.
- Python's ElementTree uses Expat as its C-level XML parser.
- Since Python 3.8, Expat's default configuration does not resolve external entity references.
- Parser file comment (line 15): "XML external entity injection: ET does not expand external
  entities by default (Python 3.8+ defenses, Expat back-end)."
- Gate 7 fixture category B includes entity-injection.fods — PASS (run045).

**Residual risk:** Low. Prototype-level mitigation is sufficient.
Product source should add `defusedxml` as defense-in-depth at Gate 10.

---

## TC-2: DTD / Entity Expansion (Billion Laughs)

**Status: MITIGATED**

**Evidence:**
- Expat (ElementTree back-end) does not process internal DTD declarations in Python 3.8+.
- Parser comment (line 17): "DTD/entity expansion: expat rejects DOCTYPE; billion-laughs not
  reachable."
- A FODS file with a DOCTYPE declaration causes Expat to raise `ET.ParseError`, caught by the
  error-handling wrapper which returns `{"error": ..., "errors": [...]}`.
- Gate 7 fixture category B: billion-laughs-style fixture — PASS (run045).

**Residual risk:** None for prototype scope.

---

## TC-3: Zip Bombs / Decompression Limits

**Status: NOT-APPLICABLE**

**Rationale:**
- FODS (Flat OpenDocument Spreadsheet) is a flat XML file. It has no ZIP container.
- The `.fods` extension is not a ZIP archive and cannot contain compressed streams.
- `ET.parse()` reads the file directly as XML — no decompression step exists.

**Note:** ODS (the ZIP-based ODF spreadsheet) will require this mitigation when acquired.

---

## TC-4: Path Traversal in Archives

**Status: NOT-APPLICABLE**

**Rationale:**
- FODS is a single file, not an archive. The parser accepts one file path as input.
- There is no archive extraction step; no entry paths are processed.
- Path traversal is structurally impossible for this format.

---

## TC-5: Malformed File Handling

**Status: MITIGATED**

**Evidence (Gate 7 cross-reference):**

Gate 7 (GATE7_FUZZ_TEST: PASS 18/18 CRASH 0/18 CORRUPT 0/18, run045) tested 4 fixture categories:

| Category | Fixtures | Result |
|---|---|---|
| A — Structural | empty file, truncated XML, invalid header, not-XML | PASS 4/4 |
| B — Entity injection | XXE attempt, billion-laughs, CDATA edge case, binary payload | PASS 4/4 |
| C — Boundary values | deeply-nested (1000 deep), large-repeat, large-formula, large-text | PASS 4/4 |
| D — Semantic | wrong mime-type, missing attrs, mismatched tags, encoding issues | PASS 6/6 |

Error handling pattern: all errors returned as structured `{"error": ..., "errors": [...]}` dicts.
The parser never crashes or raises uncaught exceptions.

**Residual risk:** None identified.

---

## TC-6: Memory Limits

**Status: DEFERRED — documented, not a blocker for Gate 8**

**Evidence:**
- `fods_parser.py` line 44: `MAX_FILE_BYTES: int = 100 * 1024 * 1024  # 100 MB guard`
- Lines 105–107: file size checked before parsing; files > 100 MB return structured error.
- `ET.parse()` loads the full XML tree into memory. Peak usage may be 3–5× file size.
- No iterparse streaming in the prototype (intentional prototype scope decision).

**Deferral justification:**
The 100 MB guard provides a practical bound for prototype and test-corpus use (< 10 MB).
Full streaming/iterparse is a Gate 10 product-source scope item, documented here so
Gate 10 implementors know to address it.

**Gate 10 requirement:** Product source (`src/python/fods/`) must use `iterparse` or equivalent
streaming for arbitrary-size input. Configurable memory limit per deployment context.

---

## TC-7: Recursion Limits

**Status: MITIGATED**

**Evidence:**
- FODS parser traversal is iterative throughout:
  - `for table in root.iter(...)` — flat iteration, no Python recursion
  - `for row in table.iter(...)` — flat iteration
  - `for cell in row.iter(...)` — flat iteration
- No Python-level recursive function calls exist in the parser code.
- Expat handles XML nesting at the C level and is not subject to Python's recursion limit.
- Gate 7 fixture `deeply-nested.fods` (1000-deep elements) PASS without crash.

**Residual risk:** None identified.

---

## TC-8: Binary Parser Safety

**Status: NOT-APPLICABLE**

**Rationale:**
- FODS is a text-based XML format. No binary parsing paths exist.
- The parser reads the file as text via `ET.parse()`.
- No struct unpacking, binary framing, or byte-level operations exist in `fods_parser.py`.

---

## Residual Risk Summary

| Risk | Severity | Category | Disposition |
|---|---|---|---|
| No streaming parse (full tree in memory) | Medium | TC-6 | Deferred to Gate 10 — documented |
| No `defusedxml` hardening in prototype | Low | TC-1 | Prototype only; product source to use `defusedxml` |

No critical or high residual risks identified. All high-priority categories are mitigated
or not applicable for this format.

---

## Gate 7 Cross-Reference

Gate 7 approval (Babar Raza, 2026-05-08, run045) covers:
- GATE7_FUZZ_TEST: PASS 18/18 CRASH 0/18 CORRUPT 0/18
- 18 malformed fixtures across 4 categories; max elapsed 0.037s
- TC-0033 DEC-034 PASS 18/18 (run045 inline verification)

The Gate 7 evidence is the primary empirical backing for TC-5 (malformed file handling).
References: `acquisition-packs/fods/gate7-malformed-fuzz-report.md`, `tests/fixtures/fods/malformed/`.

---

## Reviewer Notes

This assessment covers the Gate 4 prototype (`prototypes/by-format/fods/fods_parser.py`).
Based on: full source code reading, Gate 7 fuzz evidence, and `docs/security.md` threat categories.

Gate 10 deferred requirements:
1. Use `defusedxml` or equivalent for XXE defense-in-depth.
2. Replace `ET.parse()` with `iterparse` streaming for large files.
3. Add configurable memory limits for production deployment context.

**TC-0038 DEC-034 inline verification: PASS 20/20** (run046 — separate session from run045
planning per DEC-034 Section V; Gate 8 execution and verification in same run046 session
per run046 execution prompt authorization).

---

*Report created by claude-sonnet-4-6, run046, 2026-05-08.*
*Sign-off: Babar Raza — 2026-05-08*
*Gate 8 APPROVED.*
