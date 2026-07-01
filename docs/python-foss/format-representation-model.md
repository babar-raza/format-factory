# Format Representation Model

**Document type:** Architecture / Backlog
**Status:** Active for XML-type formats; non-XML is backlog only.
**Created:** 2026-05-08 (memory sprint)
**Last updated:** 2026-05-11
**Visibility:** internal

---

## 1. Purpose

This document defines the physical representation categories for file formats in format-factory, establishes the immediate XML-first scope, and captures non-XML adaptability as explicit backlog.

The project must avoid hardcoding XML-only assumptions in its architecture. The gates, evidence system, oracle harness, and product source should be adaptable to non-XML formats without rework. However, non-XML adaptability is backlog only and must not be implemented without explicit authorization.

---

## 2. Representation Categories

| Category | Description | Examples |
|---|---|---|
| `text_xml` | Single flat XML file | FODS, FODT, FODP, FODG |
| `zip_container` | ZIP archive containing XML parts | ODS, ODT, XLSX, DOCX, PPTX |
| `binary_records` | Sequential binary record stream | XLS BIFF, DOC Word97 |
| `compound_document` | OLE/CFB compound file | DOC, XLS, PPT Office 97-2003 |
| `delimited_text` | Character-delimited rows | CSV, TSV |
| `json_like` | JSON or JSON-adjacent structures | GeoJSON, some export formats |
| `hybrid_container` | Mixed or non-standard container | Some scientific formats |

---

## 3. Immediate Focus: XML-Type Formats

Current work is `text_xml` only:

- FODS: Gate 10 passed; Python source created in `src/python/fods/`.
- FODT: Gates 1-9 passed; Gate 10 planning_verified; Python source implemented in `src/python/fodt/` pending human review.

The acquisition pipeline has been validated on two `text_xml` formats. The gates, evidence system, spec cache, oracle harness, fuzz infrastructure, product mapping process, and Phase 4 Python source pattern all work for this representation family.

Additional `text_xml` formats such as FODP and FODG can reuse the pipeline, but they still require their own gates, evidence, samples, models, tests, and human approvals.

---

## 4. XML Pipeline Reuse Vs. Format-Specific Work

### What Another XML Format Can Reuse

| Reusable infrastructure | Notes |
|---|---|
| 11-gate pipeline | Same gates, same DEC-034, same approval process |
| Evidence bundle system | Same contracts, validator, and builder |
| Spec cache and normalization | If using the same spec body, such as OASIS ODF 1.3 |
| Sample provenance policy | Same license requirements |
| XML safety patterns | XXE and DTD mitigations from Gate 7/8 are reusable |
| Oracle harness pattern | `run_{format}_oracle.py` pattern is reusable |
| Evidence contracts | Base contract reusable; format-specific contract extends it |
| Product mapping process | Tier model and feature enumeration reusable |

### What Another XML Format Still Needs New

| Format-specific work | Notes |
|---|---|
| Domain model | New neutral model for the format family |
| Sample corpus | New synthetic samples for the format |
| Parser semantics | New parser understanding, such as cells vs paragraphs vs slides |
| Oracle comparison logic | New output comparison for the format |
| Fuzz cases | New malformed input categories |
| Product tier map | New feature enumeration and tier assignment |
| Security surface | New threat model for that format's elements and behavior |

### Expected Adaptation Ranges

These are directional estimates, not guaranteed metrics:

| Format type | Expected format-specific effort |
|---|---|
| Different XML format, same spec body | 20-40% format-specific |
| Different XML format, different spec body | 30-50% format-specific |
| ZIP/container format | 40-60% format-specific |
| Binary format | 55-75% format-specific |

---

## 5. Non-XML Adaptability Backlog

### ZIP/Container Formats

Examples: ODS, XLSX, DOCX.

- Parser strategy: Extract XML from ZIP, then apply XML pipeline.
- Security surface: ZIP bombs, path traversal, malformed ZIP headers, nested ZIP.
- Expected reusable infrastructure: XML-layer patterns, gates, evidence system, product mapping.
- Expected new work: ZIP extraction layer and relationship handling.

### Binary Record Formats

Examples: XLS BIFF, DOC Word97.

- Parser strategy: Structured binary reader; no XML parser reuse.
- Security surface: Integer overflow, truncated records, malformed record headers.
- Expected reusable infrastructure: Pipeline gates, evidence system, product mapping.
- Expected new work: Binary parser and spec analysis from documentation.

### Compound Document Formats

Examples: OLE/CFB based DOC, XLS, PPT.

- Parser strategy: OLE/CFB layer before content parsing.
- Security surface: CFB corruption, stream overflow, directory structure issues.
- Expected new work: CFB reader, stream identification, OLE metadata.

### Delimited Text

Examples: CSV, TSV.

- Parser strategy: Record and field parsing.
- Security surface: CSV injection, very long fields, null bytes, encoding attacks.
- Expected new work: Dialect detection, encoding handling, injection detection.

---

## 6. Backlog Taskcards

| Taskcard | Title | Status |
|---|---|---|
| REP-001 | Format representation profile schema and design | proposed_pending_human_approval |
| REP-002 | XML representation profile for FODS and FODT | proposed_pending_human_approval |
| REP-003 | Non-XML adaptability architecture | proposed_pending_human_approval |
| REP-004 | ZIP/container pilot planning | proposed_pending_human_approval |
| REP-005 | Binary-record pilot planning | proposed_pending_human_approval |

None of these are authorized for execution unless a human prompt names the taskcard and allowed files.

---

## 7. Prohibition

Do not implement non-XML format support, ZIP container extraction, or binary record parsing without an explicit human-authorized execution prompt that names the format, representation type, and gate entry point.
