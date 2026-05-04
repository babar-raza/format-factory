---
artifact_id: <format-id>-parser-notes-v1
artifact_type: acquisition-pack
path: acquisition-packs/<format-id>/parser-notes.md
format_id: <format-id>
product_family: <cells|words|slides|imaging|diagram|archive>
visibility: evidence-only
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: <human|claude>
generated_at: <ISO-8601>
reusable: true
refresh_policy:
  trigger: source-changed
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: Gate 4 planning artifact. Documents parser strategy and security design decisions.
---

# Parser Notes — [Format Name]

**Format ID:** `<format-id>`
**Gate:** 4
**Status:** Not started

---

## Purpose

This document records parser design decisions, implementation strategy, and security design choices for the prototype parser. It is an input to the prototype README (Gate 4) and to the security review (Gate 8). The goal is to document the "why" behind implementation choices before and during prototype development.

---

## Parser Architecture Decision

**Parsing strategy:** [Describe the chosen approach: streaming (iterparse / SAX), DOM (ElementTree / XmlDocument), or custom. Justify the choice.]

**Programming language:** [Python — prototype. Python and/or C# — product.]

**Key libraries:**
- Python: [e.g., defusedxml, lxml, xml.etree.ElementTree]
- .NET: [e.g., System.Xml.Linq, System.Xml.XmlReader]

**Rationale for library choices:** [Why these libraries? What security properties do they provide?]

---

## Security Design

Reference: `docs/security.md`. Address each applicable threat category.

### XXE (XML External Entities)

**Applicable:** [yes | no | not applicable]
**Mitigation:** [How is XXE disabled? e.g., "Using defusedxml, which disables external entity resolution by default."]
**Code reference:** [Function or module name]

### DTD / Entity Expansion (Billion Laughs)

**Applicable:** [yes | no | not applicable]
**Mitigation:** [How is entity expansion limited? e.g., "defusedxml prevents this by default."]

### Zip Bombs and Decompression Limits

**Applicable:** [yes | no — FODS is flat XML, not ZIP-based]
**Mitigation:** [If applicable: describe decompression limits. If not applicable: state why.]

### Path Traversal in Archive Formats

**Applicable:** [yes | no]
**Mitigation:** [If applicable: describe path sanitization approach.]

### Malformed File Handling

**Approach:** [How does the parser handle malformed input? Return structured error? Raise exception? What is the error reporting strategy?]
**Defensive checks:** [List the key defensive checks: length fields, offsets, counts checked before use]

### Memory Limits

**Maximum file size for in-memory parsing:** [e.g., 256 MB for text formats]
**Streaming approach:** [If streaming is used, describe where. If not, justify the memory limit.]

### Recursion Limits

**Applicable:** [yes | no]
**Approach:** [Explicit depth counter? Iterative algorithm? System recursion limit?]

---

## Known Parsing Challenges

[List known challenges, complex cases, or areas that require careful implementation based on the spec evidence and sample corpus.]

| Challenge | Spec Section | Approach |
|---|---|---|
| | | |

---

## Oracle Comparison Plan

**Oracle tool:** [e.g., LibreOffice 7.6.x]
**Comparison approach:** [How will oracle output be captured and compared? What data structure will be compared?]
**Expected discrepancies:** [Based on spec analysis, what discrepancies are anticipated?]

---

## Fuzz Testing Plan

**Fuzz harness approach:** [Describe the intended fuzz harness. Python: atheris? AFL? Custom?]
**Fuzz seed types required:** [minimal valid, empty, truncated, illegal values, oversized fields]
**Expected issues:** [Based on parsing challenges above, what types of crashes are expected?]

---

## Gate 4 Sign-off

**Reviewed by:** (to be filled)
**Review date:** (to be filled)
**Prototype passes corpus:** (yes/no)
**Security baseline confirmed:** (yes/no)
**Notes:** (to be filled)
