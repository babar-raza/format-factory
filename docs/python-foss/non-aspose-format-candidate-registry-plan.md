# Non-Aspose Format Candidate Registry Plan

**Document type:** Backlog / Planning
**Status:** Backlog only. Registry file not yet created.
**Created:** 2026-05-08 (memory sprint)
**Last updated:** 2026-05-08
**Visibility:** internal

---

## 1. Purpose

Maintain a visible registry of file formats that are not common to Aspose products, or that are
underserved by current Aspose tooling. This registry helps identify high-value acquisition targets
where format-factory can provide unique or superior support.

---

## 2. Claim Policy

**Do not claim a format is not supported by Aspose without verification.**

Verification sources:
- Aspose product documentation (aspose.com/products/)
- Aspose API references
- Public file format specifications
- Aspose product/package pages (NuGet, PyPI)
- Manual confirmation where documentation is unclear

Unverified candidates must be tagged `verification_status: unverified` in the registry.

---

## 3. Proposed Registry File

**Location:** `registry/non-aspose-format-candidates.yaml`

**Status of this file:** Not yet created. Requires NAC-001 design taskcard first.

### 3.1 Required Fields

```yaml
- format_id: <short-id>
  display_name: <Full Name>
  extensions: [.<ext>]
  domain: <cells|words|slides|imaging|diagram|scientific|cad|finance|ebook|data|game>
  physical_representation: <text_xml|zip_container|binary_records|compound_document|delimited_text|json_like|hybrid_container>
  container_model: <none|zip|ole_cfb|custom>
  xml_based: <true|false>
  known_aspose_overlap: <full|partial|none|unknown>
  why_not_common_to_aspose: <text or null>
  evidence_required: <list of what needs to be verified>
  oracle_candidates: <list of tools that can serve as reference>
  spec_availability: <open|restricted|proprietary|undocumented>
  complexity: <low|medium|high|very_high>
  product_potential: <low|medium|high>
  recommended_priority: <1-5>
  verification_status: <verified|unverified|in_progress>
  status: <proposed|accepted|rejected|deferred>
  notes: <text>
```

---

## 4. Candidate Categories

| Category | Description | Notes |
|---|---|---|
| XML-based less-common formats | XML formats not in Aspose mainstream | E.g., DITA, DocBook, OPML |
| ZIP/container formats | Container-based document formats | E.g., EPUB, OpenDocument derivatives |
| Binary scientific formats | Scientific/engineering data formats | E.g., HDF5, NetCDF |
| CAD/GIS formats | Technical drawing and geo formats | E.g., DXF, GeoJSON, KML |
| Finance/reporting formats | Financial document formats | E.g., XBRL, iXBRL |
| E-book/document-adjacent | E-reader and publishing formats | E.g., EPUB |
| Data interchange formats | Structured data exchange | E.g., SDMX-ML |
| Game/resource formats | Game asset formats | Low priority; listed for completeness |

---

## 5. Relationship to Existing Registry

The existing `registry/format-registry.yaml` tracks formats that have entered the 11-gate pipeline.
The non-Aspose candidate registry is a pre-pipeline discovery layer — it holds formats being
evaluated for future pipeline entry.

A format moves from `registry/non-aspose-format-candidates.yaml` to `registry/format-registry.yaml`
when a human authorizes a Gate 1 scoring sprint for it.

---

## 6. Backlog Taskcards

| Taskcard | Title | Status |
|---|---|---|
| NAC-001 | Non-Aspose candidate registry schema and design | proposed_pending_human_approval |
| NAC-002 | Verified candidate discovery pilot | proposed_pending_human_approval |
| NAC-003 | Candidate scoring model extension | proposed_pending_human_approval |
| NAC-004 | Candidate evidence requirements | proposed_pending_human_approval |

See `taskcards/NAC-*.md` for definitions. None are authorized for execution in this sprint.

---

## 7. Status

**BACKLOG ONLY.** No registry file created in this memory sprint.
`registry/non-aspose-format-candidates.yaml` does not yet exist.
NAC-001 is the first required step.
