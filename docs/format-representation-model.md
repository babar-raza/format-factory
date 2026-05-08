# Format Representation Model

**Document type:** Architecture / Backlog
**Status:** Active (XML-type immediate focus); non-XML is backlog only.
**Created:** 2026-05-08 (memory sprint)
**Last updated:** 2026-05-08
**Visibility:** internal

---

## 1. Purpose

This document defines the physical representation categories for file formats in format-factory,
establishes the immediate XML-first scope, and captures non-XML adaptability as explicit backlog.

The project must avoid hardcoding XML-only assumptions in its architecture — the gates, evidence
system, oracle harness, and product source should be adaptable to non-XML formats without rework.
However, non-XML adaptability is backlog only and must not be implemented now.

---

## 2. Representation Categories

| Category | Description | Examples |
|---|---|---|
| `text_xml` | Single flat XML file | FODS, FODT, FODP, FODG |
| `zip_container` | ZIP archive containing XML parts | ODS, ODT, XLSX, DOCX, PPTX |
| `binary_records` | Sequential binary record stream | XLS (BIFF), DOC (Word97) |
| `compound_document` | OLE/CFB compound file | DOC, XLS, PPT (Office 97-2003) |
| `delimited_text` | Character-delimited rows | CSV, TSV |
| `json_like` | JSON or JSON-adjacent structures | GeoJSON, some export formats |
| `hybrid_container` | Mixed or non-standard container | Some scientific formats |

---

## 3. Immediate Focus: XML-type Formats

**Current work:** `text_xml` formats only — FODS (Gate 10 PASSED), FODT (Gates 1–8 PASSED).

The full acquisition pipeline has been validated on two `text_xml` formats. The gates, evidence
system, spec cache, oracle harness, fuzz infrastructure, and product mapping process all work
for `text_xml`. No changes are needed to support additional `text_xml` formats (e.g., FODP, FODG).

---

## 4. XML Pipeline Reuse vs. Format-Specific Work

### 4.1 What another XML format can reuse

| Reusable infrastructure | Notes |
|---|---|
| 11-gate pipeline | Same gates, same DEC-034, same approval process |
| Evidence bundle system | Same contracts, same validator, same builder |
| Spec cache and normalization | If using the same spec body (OASIS ODF 1.3) |
| Sample provenance policy | Same license requirements |
| XML safety patterns | XXE/DTD mitigations from Gate 7/8 are reusable |
| Oracle harness pattern | `run_{format}_oracle.py` pattern is reusable |
| Evidence contracts | Base contract reusable; format-specific contract extends it |
| Product mapping process | Tier model and feature enumeration reusable |

### 4.2 What another XML format still needs new

| Format-specific work | Notes |
|---|---|
| Domain model | New neutral model for new format family |
| Sample corpus | New synthetic samples for the format |
| Parser semantics | New parser understanding (paragraph vs cell vs slide) |
| Oracle comparison logic | New output comparison for the format |
| Fuzz cases | New malformed input categories |
| Product tier map | New feature enumeration and tier assignment |
| Security surface | New threat model (different XML elements, different attack surface) |

### 4.3 Expected adaptation ranges (directional estimates only)

| Format type | Expected format-specific effort |
|---|---|
| Different XML format (same spec body) | 20–40% format-specific |
| Different XML format (different spec body) | 30–50% format-specific |
| ZIP/container format | 40–60% format-specific |
| Binary format | 55–75% format-specific |

These are directional estimates, not guaranteed metrics. Actual effort depends on format complexity,
spec quality, and domain model similarity.

---

## 5. Non-XML Adaptability Backlog

### 5.1 ZIP/Container Formats (e.g., ODS, XLSX, DOCX)

**Parser strategy:** Extract XML from ZIP, then apply XML pipeline. Adds ZIP layer complexity.
**Sample strategy:** Same license requirements; more complex to create synthetically.
**Oracle strategy:** Same harness pattern; different export format.
**Fuzz/security surface:** ZIP bomb attacks, path traversal, malformed ZIP headers, nested ZIP.
**Expected reusable infrastructure:** All XML-layer patterns.
**Expected format-specific work:** ZIP extraction layer, multi-part relationships.

### 5.2 Binary Record Formats (e.g., XLS BIFF, DOC Word97)

**Parser strategy:** Requires structured binary reader; no XML reuse.
**Sample strategy:** May need LibreOffice to generate samples; provenance harder.
**Oracle strategy:** May need different reference tool (not LibreOffice text export).
**Fuzz/security surface:** Integer overflow, truncated records, malformed record headers.
**Expected reusable infrastructure:** Pipeline gates, evidence system, product mapping.
**Expected format-specific work:** Binary parser, spec analysis from documentation only.

### 5.3 Compound Document Formats (OLE/CFB)

**Parser strategy:** Requires OLE/CFB layer before content parsing.
**Fuzz/security surface:** CFB corruption, directory traversal, stream overflow.
**Expected format-specific work:** CFB reader, stream identification, OLE metadata.

### 5.4 Delimited Text (CSV, TSV)

**Parser strategy:** Simple record/field parsing; no binary complexity.
**Oracle strategy:** Round-trip through LibreOffice or similar.
**Fuzz/security surface:** CSV injection, very long fields, null bytes, encoding attacks.
**Expected format-specific work:** Dialect detection, encoding handling, injection detection.

---

## 6. Backlog Taskcards

| Taskcard | Title | Status |
|---|---|---|
| REP-001 | Format representation profile schema and design | proposed_pending_human_approval |
| REP-002 | XML representation profile for FODS and FODT | proposed_pending_human_approval |
| REP-003 | Non-XML adaptability architecture | proposed_pending_human_approval |
| REP-004 | ZIP/container pilot planning | proposed_pending_human_approval |
| REP-005 | Binary-record pilot planning | proposed_pending_human_approval |

See `taskcards/REP-*.md` for definitions. None of these are authorized for execution in this sprint.

---

## 7. Prohibition

Do not implement non-XML format support, ZIP container extraction, or binary record parsing
without an explicit human-authorized execution prompt that names the format, representation type,
and gate entry point.
