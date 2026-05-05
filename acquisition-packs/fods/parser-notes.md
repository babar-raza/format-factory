---
artifact_id: fods-parser-notes-v1
artifact_type: acquisition-pack
path: acquisition-packs/fods/parser-notes.md
format_id: fods
product_family: cells
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-04"
reusable: true
refresh_policy:
  trigger: source-changed
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 planning artifact. Skeleton only — not started. Parser design must not proceed before Gate 2 spec review and Gate 3 sample corpus."
---

# Parser Notes — Flat OpenDocument Spreadsheet (FODS)

**Format ID:** `fods`
**Gate:** 4
**Status:** Not started — skeleton created run017 after Gate 1 approval

**Gate 1 approved by:** Babar Raza (2026-05-04)
**Gate 2 status:** PASSED — Babar Raza (2026-05-05, run023)
**Gate 3 status:** sample_corpus_verified_pending_human_review (run027)
**Gate 4 status:** not_started (blocked by Gate 3 approval)

**Important:** No prototype parser has been created. `prototypes/by-format/fods/` does not exist and must not be created until Gate 4 is passed and an explicit prototype implementation prompt is issued.

---

## Purpose

This document will record parser design decisions, implementation strategy, and security design choices for the FODS prototype parser. This is a skeleton — all sections are placeholders until Gate 2 spec review and Gate 3 sample corpus work are complete.

---

## Initial Assessment (from Gate 1 scoring)

Based on Gate 1 scoring evidence:
- FODS is a single flat XML file (no ZIP container)
- ODF XML semantics are complex (styles inheritance, OpenFormula, conditional formatting)
- Implementation complexity score: 2/3 (moderate — no ZIP layer but ODF XML semantics require real work)
- XML parsing approach is appropriate

---

## Parser Architecture Decision

*(To be completed after spec review in TC-0009.)*

**Parsing strategy:** TBD — likely streaming (iterparse / SAX) for memory efficiency on large spreadsheets
**Programming language:** Python (prototype); Python and/or .NET (product — Phase 4+)
**Key libraries:**
- Python: defusedxml (security requirement per AGENTS.md Q3), lxml or xml.etree.ElementTree
- .NET: System.Xml.XmlReader with DtdProcessing.Prohibit and XmlResolver = null (per AGENTS.md Q3)

---

## Security Design

*(High-level initial assessment — to be detailed after spec review.)*

### XXE (XML External Entities)

**Applicable:** yes
**Mitigation:** Use defusedxml (Python) or XmlReaderSettings with DtdProcessing.Prohibit (.NET) per AGENTS.md Section Q3.

### DTD / Entity Expansion (Billion Laughs)

**Applicable:** yes
**Mitigation:** defusedxml prevents this by default.

### Zip Bombs and Decompression Limits

**Applicable:** no — FODS is flat XML, not ZIP-based.

### Path Traversal in Archive Formats

**Applicable:** no — no archive container.

### Malformed File Handling

**Approach:** (to be detailed after spec review)
**Defensive checks:** (to be detailed)

### Memory Limits

**Maximum file size for in-memory parsing:** TBD
**Streaming approach:** TBD

### Recursion Limits

**Applicable:** possibly — ODF XML nesting depth to be verified from spec
**Approach:** TBD

---

## Known Parsing Challenges

*(Initial list from Gate 1 scoring context — to be detailed from spec review.)*

| Challenge | Spec Section | Approach |
|---|---|---|
| Styles inheritance | TBD | TBD |
| Formula syntax (OpenFormula) | TBD | TBD |
| Conditional formatting | TBD | TBD |
| Merged cells | TBD | TBD |

---

## Oracle Comparison Plan

*(To be completed in TC-0009 / Gate 4 work.)*

**Oracle tool:** LibreOffice (candidate — version TBD)
**Comparison approach:** TBD
**Expected discrepancies:** TBD

---

## Fuzz Testing Plan

*(To be completed in Gate 4 work.)*

**Fuzz harness approach:** TBD
**Fuzz seed types required:** minimal valid, empty, truncated, illegal values
**Expected issues:** TBD

---

## Gate 4 Sign-off

**Reviewed by:** (to be filled)
**Review date:** (to be filled)
**Prototype passes corpus:** (yes/no)
**Security baseline confirmed:** (yes/no)
**Notes:** (to be filled)
