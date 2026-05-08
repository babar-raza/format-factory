---
artifact_id: fods-gate10-oss-scope
artifact_type: acquisition-pack
path: acquisition-packs/fods/gate10-oss-scope.md
format_id: fods
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: claude-sonnet-4-6
generated_at: "2026-05-08"
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: "FODS Gate 10 OSS release scope. First OSS release: Tiers 0-2 (12 features). run048 (2026-05-08)."
---

# FODS Gate 10 — First OSS Release Scope

**Gate:** 10 — OSS Release Readiness
**Format:** FODS (Flat OpenDocument Spreadsheet)
**Run:** run048 (2026-05-08)
**Status:** APPROVED — Babar Raza (2026-05-08, run048)
**Tier map source:** acquisition-packs/fods/tier-map.yaml v1.0

---

## First OSS Release: Tiers 0-2

The first FODS Python OSS release (`format-factory-fods` v0.1.0) covers Tiers 0, 1, and 2
as defined in tier-map.yaml v1.0. Total: 12 features.

### Tier 0 — File Identity (4 features)

| Feature ID | Feature Name | Description |
|---|---|---|
| T0-F001 | Format Detection | Detect FODS by root element + MIME type |
| T0-F002 | MIME Type | Extract office:mimetype attribute |
| T0-F003 | Version | Extract office:version attribute |
| T0-F004 | Document Stats | Sheet count, total row count, total cell count |

### Tier 1 — Structural Extraction (4 features)

| Feature ID | Feature Name | Description |
|---|---|---|
| T1-F001 | Sheet Names | List all table:table names in document order |
| T1-F002 | Row Count per Sheet | Count table:table-row elements per sheet |
| T1-F003 | Column Count per Sheet | Count table:table-cell elements in first row |
| T1-F004 | Cell Addresses | List all non-empty cell addresses (Sheet.Row.Col) |

### Tier 2 — Typed Values (4 features)

| Feature ID | Feature Name | Description |
|---|---|---|
| T2-F001 | String Cells | Extract office:value-type="string" cell values |
| T2-F002 | Float Cells | Extract office:value-type="float" with numeric value |
| T2-F003 | Boolean Cells | Extract office:value-type="boolean" cells |
| T2-F004 | Date Cells | Extract office:value-type="date" cells |

---

## Deferred Tiers (not in first release)

- **Tier 3** (Formulas + References): Deferred to v0.2.0
- **Tier 4** (Advanced): Deferred to v0.3.0+

---

## Security Requirements for Product Source

- TC-6 (Memory): `iterparse` REQUIRED for streaming arbitrary-size files
- TC-1 (XXE): `defusedxml` RECOMMENDED as defense-in-depth
- These are documented in gate10-product-source-readiness-report.md
