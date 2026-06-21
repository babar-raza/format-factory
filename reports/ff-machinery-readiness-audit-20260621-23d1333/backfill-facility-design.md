# Backfill and Migration Facility Design
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Current State

### What Exists
- `reports/specification-authority-layer-mwp/qname-ontology/migration-plan.yaml` — DESIGN DOCUMENT
  - Phases 1-4 defined, ALL phases status: "not_started"
  - Blocked: "until system-healing gate passes (Lanes 1, 3, 6 complete)"
- `reports/specification-authority-layer-mwp/qname-ontology/canonical-class-inventory.yaml`
  - All classes are `not_implemented` or `facade_exists_no_canonical`
- `.claude/commands/spec-parity-source-regeneration-and-migration.md` — SKILL, no tooling

### What is Missing
1. No backfill script or tool
2. No inventory generator (what classes exist in current src/?)
3. No QName gap analyzer (what's the delta from current to qname-compliant?)
4. No compatibility shim generator
5. No per-product migration executor
6. No test migration tracker
7. No safe-rollback mechanism for backfill

## Designed Backfill System

### Phase 1 — Inventory

Tool: `tools/backfill/inventory_current_source.py`

Purpose: Scan all src/**/*.py and src/**/*.cs, extract:
- All class names (with module/namespace path)
- All public function/method names
- All spec references in comments (§ section markers)
- File LOC

Output: `reports/backfill/current-source-inventory.json`

```json
{
  "format": "fods",
  "language": "dotnet",
  "classes": [
    {"name": "FodsDocument", "file": "src/net/fods/FodsDocument.cs",
     "spec_refs": ["§3.1.2", "§3.7", "§9.4.2"], "loc": 1293}
  ]
}
```

### Phase 2 — QName Gap Analysis

Tool: `tools/backfill/analyze_qname_gaps.py`

Purpose: For each class in inventory, map to canonical QName target:
- FodsDocument → Office.Document (qname: office:document)
- FodsSheet → Table.Table (qname: table:table)
- FodsRow → Table.TableRow (qname: table:table-row)
- FodsCell → Table.TableCell (qname: table:table-cell)
- FodtDocument → Office.Document (qname: office:document)
- FodtParagraph → Text.Paragraph (qname: text:p)
- FodtBody → Office.Body (qname: office:body)

Output: `reports/backfill/{format}-qname-gap-analysis.yaml`

```yaml
format: fods
language: dotnet
gaps:
  - existing_class: FodsDocument
    expected_canonical: Office.Document
    expected_path: src/net/FormatFactory/Office/Document.cs
    migration_action: move_to_compat
    compat_path: src/net/fods/Compat/FodsDocument.cs
    delegates_to: Office.Document
```

### Phase 3 — Safe Migration (per product, per file)

Migration MUST:
1. Create canonical class first (Wave 1: `src/net/FormatFactory/`)
2. Move existing class to Compat/ with forwarding delegates (Wave 2)
3. Run tests after each file move
4. Verify zero test regressions before proceeding to next file

Tool: `tools/backfill/execute_migration_step.py --format fods --step M1.1`

This must be stepwise and reversible. Never batch-migrate multiple files at once.

### Phase 4 — Python Class-Based Model Layer

Current Python products use dict-based models. Migration to typed dataclasses:

```python
# Current (dict-based, hard to use)
workbook = {"sheets": [{"name": "Sheet1", "rows": [...]}]}

# Target (typed dataclass, spec-aligned)
@dataclass
class Workbook:  # → Office.Document qname
    sheets: list[Sheet]
    mimetype: str
    version: str

@dataclass
class Sheet:  # → Table.Table qname
    name: str
    rows: list[Row]
```

This migration is HIGHER RISK for Python because:
- 1039 FODS Python tests use dict-based model
- 1000+ tests for other formats use format-specific APIs
- All tests must continue passing during migration

**Strategy:** Add dataclass model alongside dict model, then gradually migrate tests.

### Compatibility Strategy

- Compat/ layer MUST expose the same public API as the pre-migration class
- Tests MUST pass without modification after Compat/ wrapping
- The old function signatures must be preserved as Compat/ delegates
- API deprecation warnings SHOULD be added for format-prefixed names

### Backfill Evidence Requirements

Each migration step requires:
1. Before/after test count (must be equal or higher)
2. QName compliance validator pass
3. Product code ledger entry
4. Spec parity verification for moved class

## Priority Order for Migration

1. **src/net/fods/** — Most complete, most tested, safest to pilot
2. **src/net/fodt/** — Second commercial target
3. **src/python/fods/fods/** — Modular Python, good candidate
4. **src/python/fodt/** — Similar to FODS Python
5. Others after pilot proves process

## Blockers Before Backfill Can Start

1. `tools/supervisor/qname_ontology_generator.py` must exist
2. Canonical class library (`src/net/FormatFactory/`) must be created
3. `spec-shaped-product-architecture-blueprint` must be run for FODS
4. `validate_qname_compliance` validator must be added to governance_validators.py
5. Separate machinery lane must exist to isolate backfill from product deepening
