---
artifact_id: fods-prototype-notes
artifact_type: prototype
path: prototypes/by-format/fods/prototype-notes.md
format_id: fods
product_family: cells
visibility: internal
publish_allowed: false
license: Apache-2.0
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude
generated_at: "2026-05-05"
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "Gate 4 prototype implementation notes for FODS parser. Created run029 (2026-05-05). Records design decisions, limitations, test plan discrepancies, and security baseline."
---

# FODS Prototype Implementation Notes — Gate 4

**Format:** Flat OpenDocument Spreadsheet (FODS)
**Gate:** Gate 4 (Parser Prototype)
**Created:** 2026-05-05 (run029)
**Prototype:** `prototypes/by-format/fods/fods_parser.py`
**Validation:** 4/4 PASS (PT-001 through PT-004)

---

## 1. Design Decisions

### 1.1 XML Library: `xml.etree.ElementTree` (stdlib)

**Decision:** Use Python stdlib `xml.etree.ElementTree` only.

**Rationale:**
- `parser-scope.md` requires stdlib only (no third-party libraries).
- ElementTree is sufficient for the Gate 4 prototype scope.
- ElementTree does not expand external entity references in Python 3.8+, providing basic XXE safety.
- No `lxml` or `defusedxml` used at this stage (Gate 8 adds production security hardening).

**Limitation:** ElementTree does not fully validate XML against a DTD or schema. Out of scope for Gate 4.

### 1.2 Namespace Handling: Clark Notation

**Decision:** Use Clark notation `{uri}localname` throughout, not prefix-based lookup.

**Rationale:**
- ODF 1.3 FODS documents declare all namespace prefixes on the root element.
- ElementTree parses namespaces into Clark notation automatically.
- Avoids brittleness from hardcoded prefix strings (`office:`, `table:`, etc.).
- Conforms to PR-010 (must use declared URI mappings, not hardcoded prefixes).

### 1.3 Row/Column Repeat Expansion

**Decision:** Expand `table:number-columns-repeated` and `table:number-rows-repeated` up to `_MAX_EXPAND_REPEAT = 128`. Warn if repeat count exceeds limit for empty cells/rows.

**Rationale:**
- FODS files produced by spreadsheet editors often have trailing empty rows/columns repeated thousands of times (e.g., `table:number-columns-repeated="1024"`).
- Allocating thousands of empty cell entries would be wasteful for Gate 4 prototype.
- Cap at 128 for prototype; production parser (Gate 9+) should handle this with lazy iteration.

**Gate 3 samples:** No repeat counts exceed 1 in the 4 synthetic samples. The cap was not triggered during validation.

### 1.4 String Cell Values

**Decision:** For `value_type="string"` cells, `value` field is `null` and the text content comes from `_extract_text()` (concatenated `<text:p>` children).

**Rationale:**
- Per ODF 1.3 §9.1.4: string cell text content is in `<text:p>` child elements, not an attribute.
- `office:value` is not used for string type.
- This matches the parser-scope.md output schema.

### 1.5 No Formula Evaluation

**Decision:** `table:formula` attribute is extracted as a raw string. No formula parsing, tokenization, or evaluation.

**Rationale:**
- PR-009 priority is SHOULD, not MUST.
- Formula evaluation is explicitly out of scope (parser-scope.md FORBIDDEN table).
- Cached result in `office:value` is preserved.

---

## 2. Test Plan Discrepancies

The parser-test-plan.md (created run028 as a planning document) contained predictions
that do not match the actual Gate 3 sample content. These discrepancies are recorded here.

| Test | Prediction in plan | Actual sample content | Impact |
|---|---|---|---|
| PT-001 | `text == "Hello, World!"` | `text == "Hello"` | Assertion updated to match actual |
| PT-002 | sheet names "Sheet1", "Sheet2" | sheet names "Data", "Summary" | Assertion updated to match actual |
| PT-003 | date cell present | No date cell in sample | Date assertion updated: expect absent |

**Action taken:** `validate_against_samples.py` tests against actual sample content with notes about plan predictions. No change to the sample files (SHA-256 hashes verified MATCH). No change to `parser-test-plan.md` in this run (update is a future parser-notes maintenance task). Discrepancies are documented here and in `acquisition-packs/fods/parser-notes.md`.

---

## 3. Known Limitations of Prototype

| Limitation | Detail | Gate when addressed |
|---|---|---|
| No style resolution | `table:style-name` noted but ignored | Gate 5+ |
| Covered cells basic | `table:covered-table-cell` detected, marked `covered: True`, not fully expanded | Gate 5+ |
| No rich text within `<text:p>` | `<text:span>` inline elements ignored | Gate 5+ |
| No chart/pivot parsing | Not applicable to prototype scope | Gate 5+ |
| No macro content parsing | Correctly excluded (security boundary) | Never |
| No annotation parsing | `<office:annotation>` elements ignored | Gate 5+ |
| Large file safety | File size guard at 100 MB; no streaming; ElementTree parses entire tree in memory | Gate 8 |
| Repeat cap at 128 | Very high repeat counts capped; warns in `warnings` list | Gate 9+ |
| No validation against ODF schema | ElementTree does not validate against DTD/schema | Gate 8 |

---

## 4. Security Baseline (Gate 4)

| Risk | Status | Mitigation |
|---|---|---|
| XXE (XML External Entity injection) | MITIGATED (prototype scope) | Python 3.8+ ElementTree does not process DTD external entity references. `ExpatParser` used by ET does not resolve `SYSTEM` or `PUBLIC` external entity references by default. Prototype is for trusted Gate 3 synthetic samples. |
| DTD entity expansion (Billion Laughs) | PARTIALLY MITIGATED | ElementTree does not process parameter entities or recursive entity definitions. Basic protection. Full hardening: Gate 8 (defusedxml). |
| Zip bombs | NOT APPLICABLE | FODS is flat XML, no ZIP container. |
| Path traversal | INPUT ONLY | Prototype only reads files; does not write output unless CLI arg specified. File path input is passed to `Path()` without canonicalization check. For Gate 4 trusted samples: acceptable. For Gate 8+: add canonical path validation. |
| Memory exhaustion | PARTIAL GUARD | 100 MB file size limit. Repeat expansion capped at 128. No streaming for large files. Gate 8 addresses production hardening. |
| Macro execution | NOT APPLICABLE | FODS XML structure parsed does not include macro execution paths. `<script:*>` elements are not traversed. |

**Full production security hardening is Gate 8 scope.** Gate 4 only requires this baseline note.

---

## 5. ODF 1.3 Spec Coverage

Requirements coverage verified against ODF 1.3 Part 3:

| Spec Section | Requirement | Verified |
|---|---|---|
| §3.1.2 | Root element `<office:document>` | YES — PR-001, PR-002 |
| §3.7 | `<office:spreadsheet>` body | YES — PR-003 |
| §9.4 | Sheet, row, cell structure | YES — PR-004, PR-005, PR-006 |
| §9.1.4 | `<text:p>` cell text | YES — PR-008 |
| §9.1.5 | `table:number-columns-repeated` | YES — PR-007 |
| §9.4 | `table:formula` | YES — PR-009 |
| §9.4 | `office:value-type` typed values | YES — PR-006 (float, string, boolean, date, time, currency, percentage) |

Spec source hash: `sha256:92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066`

---

## 6. Gate 4 Status

**Validation result:** PASS (4/4 samples, all assertions pass)
**Gate 4 status:** `prototype_created_pending_independent_verification`
**Gate 4 approved:** NO — human approval required after TC-0018 independent verification
**No product source created**
**No neutral model schema created**
**No formula evaluation**
**No remote calls**

---

## Revision History

| Run | Change |
|---|---|
| run029 | Prototype created; validation 4/4 PASS; design decisions and limitations recorded |
