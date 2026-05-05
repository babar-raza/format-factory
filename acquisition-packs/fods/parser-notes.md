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
notes: "Gate 4 execution artifact. Prototype created run029 (2026-05-05). Validation 4/4 PASS. Status: prototype_created_pending_independent_verification. TC-0018 independent verification required before Gate 4 human approval."
---

# Parser Notes — Flat OpenDocument Spreadsheet (FODS)

**Format ID:** `fods`
**Gate:** 4
**Status:** Not started — skeleton created run017 after Gate 1 approval

**Gate 1 approved by:** Babar Raza (2026-05-04)
**Gate 2 status:** PASSED — Babar Raza (2026-05-05, run023)
**Gate 3 status:** PASSED — Babar Raza (2026-05-05, run028)
**Gate 4 status:** prototype_created_pending_independent_verification (run029)

**Prototype:** `prototypes/by-format/fods/fods_parser.py` — created run029 (2026-05-05)
**Validation:** PT-001 through PT-004 PASS (4/4) — run029
**Next step:** TC-0018 independent verification (DEC-034) before Gate 4 human approval
**Gate 4 approved:** NO

---

## Purpose

This document records parser design decisions, implementation strategy, and security design choices for the FODS prototype parser. Updated with Gate 4 execution findings (run029).

---

## Initial Assessment (from Gate 1 scoring)

Based on Gate 1 scoring evidence:
- FODS is a single flat XML file (no ZIP container)
- ODF XML semantics are complex (styles inheritance, OpenFormula, conditional formatting)
- Implementation complexity score: 2/3 (moderate — no ZIP layer but ODF XML semantics require real work)
- XML parsing approach is appropriate

---

## Parser Architecture Decision (Gate 4 Prototype — run029)

**Parsing strategy:** ElementTree tree parse (full document loaded into memory). Appropriate for Gate 4 prototype scope. Production parser (Gate 9+) should use iterparse for large file streaming.
**Programming language:** Python 3.11+ (prototype, stdlib only); Python and/or .NET (product — Phase 4+)
**Key libraries (prototype):** `xml.etree.ElementTree` (stdlib). No third-party dependencies.
**Namespace handling:** Clark notation `{uri}localname` — uses declared URI mappings from document (per PR-010).

**Test plan discrepancies discovered during Gate 4 execution (run029):**
- PT-001: parser-test-plan.md predicted `text="Hello, World!"`. Actual sample: `text="Hello"`. No sample change needed; test updated to match actual.
- PT-002: plan predicted sheet names "Sheet1", "Sheet2". Actual: "Data", "Summary". Test updated.
- PT-003: plan predicted date cell present. Actual sample: no date cell (string, float, boolean only). Test updated.
- Formula sample: `oooc:=SUM([.A1:.A3])` cached value 60.0 — matches plan prediction.

All discrepancies between plan predictions and actual samples are documented here and in `prototypes/by-format/fods/prototype-notes.md`. The sample files are unchanged (SHA-256 hashes verified MATCH).

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
