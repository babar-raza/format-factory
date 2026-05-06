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
notes: "Gate 4 execution artifact. Prototype created run029 (2026-05-05). TC-0018 independent verification PASS (run030, 2026-05-06). Status: prototype_verified_pending_human_review. Human Gate 4 approval required. Spec Workbench v1 created run030 (.local/spec-cache/fods/1.3/workbench/)."
---

# Parser Notes — Flat OpenDocument Spreadsheet (FODS)

**Format ID:** `fods`
**Gate:** 4
**Status:** Not started — skeleton created run017 after Gate 1 approval

**Gate 1 approved by:** Babar Raza (2026-05-04)
**Gate 2 status:** PASSED — Babar Raza (2026-05-05, run023)
**Gate 3 status:** PASSED — Babar Raza (2026-05-05, run028)
**Gate 4 status:** prototype_verified_pending_human_review (TC-0018 PASS — run030)

**Prototype:** `prototypes/by-format/fods/fods_parser.py` — created run029 (2026-05-05)
**Validation:** PT-001 through PT-004 PASS (4/4) — run029 (original) and run030 (TC-0018 independent re-verification)
**TC-0018 result:** PASS — DEC-034 independent verification complete (run030, 2026-05-06)
**Next step:** Human Gate 4 approval
**Gate 4 approved:** NO — human approval required

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

## Spec Workbench References (run030)

The FODS Spec Workbench v1 was built in run030. All parser requirements are now cross-referenced with workbench artifacts:

| Workbench Artifact | Location (local-only) | Description |
|---|---|---|
| `verified-facts.yaml` | `.local/spec-cache/fods/1.3/workbench/` | 10 core verified FODS facts |
| `parser-requirements.yaml` | `.../workbench/requirement-packs/` | PR-001..PR-010 with full provenance |
| `parser-coverage-matrix.yaml` | `.../workbench/coverage/` | PR-001..PR-010 × PT-001..PT-004 coverage |
| `gate4-parser-packet.yaml` | `.../workbench/task-packets/` | Concise Gate 4 task packet (120 lines) |

**Coverage summary (parser requirements × test samples):**

| Req | PT-001 | PT-002 | PT-003 | PT-004 | Coverage |
|---|---|---|---|---|---|
| PR-001 (root element) | ✓ | ✓ | ✓ | ✓ | 4/4 |
| PR-002 (mimetype) | ✓ | — | — | — | 1/4 |
| PR-003 (body/spreadsheet) | ✓ | ✓ | ✓ | ✓ | 4/4 |
| PR-004 (sheets) | ✓ | ✓ | ✓ | ✓ | 4/4 |
| PR-005 (rows) | ✓ | ✓ | ✓ | ✓ | 4/4 |
| PR-006 (typed cells) | ✓ | ✓ | ✓ | ✓ | 4/4 |
| PR-007 (col-repeated) | ✓ | ✓ | ✓ | ✓ | 4/4 |
| PR-008 (text:p) | ✓ | ✓ | ✓ | ✓ | 4/4 |
| PR-009 (formula) | — | — | — | ✓ | 1/4 |
| PR-010 (namespaces) | ✓ | ✓ | ✓ | ✓ | 4/4 |

**Gaps for unsupported spec areas (Tier 0/1 subset only):**
- Style resolution (§14+) — not covered by Gate 4 samples or prototype
- Conditional formatting (§9.3) — not in Gate 4 scope
- Merged cells / covered-table-cell — detected but not fully expanded
- Date cell type — PT-003 sample does not include date cell (string/float/boolean only)
- Formula evaluation — raw extraction only; no evaluation (OpenFormula out of scope)

---

## Gate 4 Sign-off

**TC-0018 independent verification:** PASS (run030, 2026-05-06)
**Prototype passes corpus:** YES — 4/4 PASS (PT-001 through PT-004)
**Security baseline confirmed:** YES — stdlib only; no network; no formula evaluation
**Human Gate 4 approval:** PENDING — required before Gate 5 work begins
**Reviewed by:** (to be filled by human approver)
**Review date:** (to be filled)
**Notes:** Gate 4 approved = false until human explicitly approves
