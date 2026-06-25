# Lane I: Backfill and Migration Facility Design
# Sprint: ff-machinery-readiness-audit-20260625

## Current State Assessment

### Backfill Inventory Scope

Direct evidence from `docs/audits/python-qname-backfill-inventory.csv` (lines 1–50+):

```
Formats with backfill inventory: 1 (ABW only)
Total symbols inventoried: 170+
Migration status: ALL PENDING (no DONE entries confirmed for functional symbols)
```

The inventory covers only ABW because ABW was the pilot format for the backfill process.
The remaining 19 Python FOSS formats have NO backfill inventory — their symbol-to-QName
mapping has never been created.

### What "Backfill" Means in This Project

The backfill problem: every Python module has symbols (functions, classes, constants)
that predate the QName registry. These symbols were named organically (e.g., `get_row_count`)
rather than spec-literally (e.g., following `table:table-row` → `TableRow.row_count`).

Backfill = the systematic process of:
1. Inventorying all existing symbols in a format module
2. Mapping each symbol to its QName (or marking it N/A for infrastructure symbols)
3. Planning any necessary renames or moves to achieve QName alignment
4. Creating Compat/ facades where the old API must be preserved
5. Updating the qname-registry YAML to reflect the mapping

### Current Compat/ Facade Inventory

**FODS** (`src/python/fods/Compat/`): 10 facades (verified 2026-06-25)
- fods_automatic_styles.py, fods_body.py, fods_covered_cell.py, fods_date_style.py
- fods_paragraph.py, fods_span.py, fods_spreadsheet.py, fods_style.py, fods_table_row.py
- FodsDocument, FodsSheet, FodsCell (architecture markers in Compat/)

**FODT** (`src/python/fodt/Compat/`): 4 facades (verified 2026-06-25)
- fodt_list.py, fodt_list_item.py, fodt_table.py, fodt_table_row.py

**All other formats**: 0 Compat/ facades (no backfill attempted)

---

## Gap Analysis

### BACKFILL-GAP-001: 19 Formats Without Symbol Inventory

| Format | Symbols (est.) | Key files needing inventory | Risk |
|---|---|---|---|
| CSV | 50+ | csv_parser.py (382 LOC), models.py | MEDIUM |
| DIF | 30+ | dif_parser.py (664 LOC) | MEDIUM |
| GNUMERIC | 40+ | gnumeric_codec.py, workbook_document.py (masquerade) | HIGH |
| NDJSON | 30+ | ndjson_codec.py (already well-organized) | LOW |
| SYLK | 30+ | sylk_parser.py | MEDIUM |
| TOML | 40+ | toml_codec.py, config_document.py (masquerade) | HIGH |
| TSV | 30+ | tsv_parser.py, models.py | MEDIUM |
| XCF | 60+ | xcf_parser.py (1272 LOC), xcf_image_metrics.py | HIGH |
| ZST | 40+ | zst_codec.py (1558 LOC) | MEDIUM |
| ODS | 30+ | ods_parser.py | MEDIUM |
| ODT | 30+ | odt_parser.py, odt_writer.py | MEDIUM |
| ABW | 170+ | abw_codec.py | PENDING (inventory exists, migration not done) |
| FODG | 50+ | fodg_codec.py (3176 LOC) | HIGH |
| FODP | 40+ | fodp_codec.py | MEDIUM |
| PBM | 20+ | pbm_parser.py | LOW |
| PGM | 20+ | pgm_parser.py | LOW |
| PPM | 20+ | ppm_parser.py | LOW |
| QOI | 20+ | qoi_parser.py | LOW |
| FODS | 80+ | fods_parser.py, models.py, writer.py, etc. | LOW (mostly done) |
| FODT | 60+ | fodt_parser.py, exporters.py, etc. | LOW (partially done) |

**Total estimated symbols without inventory: ~800**

### BACKFILL-GAP-002: No Automated Backfill Script

No `backfill.py` or `inventory_format.py` script exists.
All inventory work was done MANUALLY for ABW by reading source files and typing CSV rows.

This is not scalable for 19 remaining formats × ~40 symbols each.

### BACKFILL-GAP-003: qname-backfill Skill Exists But Is Incomplete

From skill list: `/qname-backfill` is listed as an available skill.
However, no command file was found at `.claude/commands/qname-backfill.md` in Phase 1 reads.
The skill may be a registration stub without a complete execution guide.

---

## Governed QName Backfill System Design

### Module 1: Inventory Scanner

**Purpose:** Automatically scan a format's Python source directory, extract all public
symbols, and produce a CSV inventory file compatible with the existing format.

```python
# tools/supervisor/backfill_inventory_scanner.py
def scan_format(format_name: str, src_root: Path) -> list[dict]:
    """
    For each .py file in src/python/{format}/:
    - Extract all public names (no underscore prefix)
    - Categorize: class / function / constant
    - Infer domain from filename pattern (spec/ = spec class, Compat/ = facade)
    - Populate inferred_qname from shared/qname-registry/{format}.yaml if matching entry exists
    - Default migration_status = PENDING
    Returns list of CSV row dicts matching docs/audits/python-qname-backfill-inventory.csv schema
    """
    pass
```

**Output:** `docs/audits/python-qname-backfill-inventory-{format}.csv`

**Difficulty:** LOW — pure static analysis, no execution required

### Module 2: QName Mapper

**Purpose:** Given the symbol inventory, infer the QName mapping for each symbol
by cross-referencing the qname-registry YAML and any matching spec_qname attributes.

```python
# tools/supervisor/backfill_qname_mapper.py
def map_symbols(inventory: list[dict], registry_path: Path) -> list[dict]:
    """
    For each symbol:
    - Check if a spec class (in spec/) has matching spec_qname
    - Check qname-registry for matching canonical_class
    - If match: set inferred_qname + source_fact_ref
    - If no match: classify as N/A_INFRASTRUCTURE or N/A_ANALYTICS_SUSPENDED
    Returns updated inventory with inferred_qname populated
    """
    pass
```

**Output:** Updated CSV with inferred_qname and source_fact_ref columns populated

### Module 3: Migration Planner

**Purpose:** For each symbol with a QName mapping, determine what physical changes
are needed (if any) to achieve QName alignment.

Migration types:
- `NO_CHANGE` — symbol name already matches spec-literal naming
- `ADD_SPEC_QNAME_ATTR` — class exists but lacks `spec_qname` ClassVar
- `ADD_FACADE` — function exists at wrong location; needs Compat/ wrapper
- `RENAME_PENDING` — function name non-compliant; rename with old alias in __init__.py
- `MOVE_TO_ANALYTICS` — function is analytics, not spec-derived; move to {format}_analytics.py
- `ARCHITECTURE_ONLY` — spec class stub; no behavioral migration needed

```python
# tools/supervisor/backfill_migration_planner.py
def plan_migrations(inventory: list[dict]) -> list[dict]:
    """
    For each symbol, determine migration_type from above enum.
    Returns migration plan with estimated impact (LOW/MEDIUM/HIGH).
    """
    pass
```

**Output:** `docs/audits/python-qname-backfill-migration-{format}.yaml`

### Module 4: V53 Compliance Validator

**Purpose:** After migration changes are applied, validate that the format's spec classes
pass V53 (spec_qname ClassVar check) and that all public classes in the API match
a registry entry.

This module wraps the existing V53 governance validator logic.

```python
# Validation call after migration:
def validate_post_migration(format_name: str) -> tuple[bool, list[str]]:
    """
    Run V53 on all spec class files for the format.
    Run V43 on all public classes in __init__.py.
    Returns (passed, error_list).
    """
    pass
```

### Module 5: Evidence Declaration

**Purpose:** Produce a backfill work item declaration suitable for submission
to the supervisor evidence pipeline.

```yaml
# Output: .local/evidences/{run_id}/backfill-evidence.yaml
item_id: QNAME-BACKFILL-{FORMAT}-001
item_type: PRODUCT_SOURCE
work_type: QNAME_BACKFILL
format: {format}
symbols_inventoried: {count}
symbols_mapped: {count}
symbols_no_change: {count}
symbols_migrated: {count}
symbols_pending: {count}
spec_fact_refs:
  - FACT-{FORMAT}-001
gap_ledger_ref: GAP-QNAME-BACKFILL-{FORMAT}-001
v53_result: PASS
evidence_paths:
  - docs/audits/python-qname-backfill-inventory-{format}.csv
  - docs/audits/python-qname-backfill-migration-{format}.yaml
```

---

## Phased Implementation Plan

### Phase 1 (Sprint 1): Automated Inventory for 5 Priority Formats

Priority order (easiest to hardest, maximum return):

1. **NDJSON** — already well-organized; fast inventory; proves scanner works
2. **TSV** — similar structure to CSV; fast
3. **SYLK** — flat symbol set; no analytics masquerade
4. **PBM/PGM/PPM** — netpbm formats share pattern; can batch
5. **ZST** — LOC at cap; inventory provides baseline for analytics extraction

Deliverable: 5 inventory CSVs + migration plans

**Time estimate:** Not provided (per instructions)

### Phase 2 (Sprint 2): Analytics Masquerade Formats

6. **GNUMERIC** — resolve workbook_document.py masquerade first, then inventory
7. **TOML** — resolve config_document.py masquerade first, then inventory
8. **XCF** — at LOC cap; inventory reveals extraction opportunities

### Phase 3 (Sprint 3): High-Symbol Formats

9. **DIF** — mixed model; inventory drives analytics extraction plan
10. **FODG** — large monolith (3176 LOC); inventory reveals scope
11. **CSV** — mixed model; key format for community use

### Phase 4 (Sprint 4): Remaining + ABW Migration Completion

12-19. **ODS, ODT, FODP, QOI, ABW (complete migration), FODS, FODT, remaining**

---

## Required Taskcard

### QNAME-BACKFILL-SYSTEM-001

| Field | Value |
|---|---|
| Title | Build automated qname-backfill system (5 modules) |
| Lane | Machinery Lane 2 (QName registry) |
| Wave | Wave 1A |
| Severity | HIGH — 800 symbols currently un-inventoried |
| Input | `docs/audits/python-qname-backfill-inventory.csv` schema |
| Output | 5 Python modules in `tools/supervisor/backfill_*.py` |
| Blocked by | None (pure tool build, no product source changes) |
| Blocks | QNAME-BACKFILL-001 through QNAME-BACKFILL-019 (per-format execution) |
| Tests needed | Unit tests for scanner (verify ABW CSV matches existing inventory) |

### QNAME-BACKFILL-PILOT-001

| Field | Value |
|---|---|
| Title | Run backfill scanner for NDJSON, TSV, SYLK (Phase 1 pilot) |
| Lane | Machinery Lane 2 |
| Wave | Wave 1A (after QNAME-BACKFILL-SYSTEM-001) |
| Format targets | ndjson, tsv, sylk |
| Expected output | 3 inventory CSVs + 3 migration plans |
| Evidence | docs/audits/python-qname-backfill-inventory-{format}.csv |
| V53 gate | Must pass for all spec classes in target formats |

---

## Assessment

**Current backfill state: EARLY_PROTOTYPE**
- 1/20 formats have symbol inventory (ABW)
- 0/20 formats have completed migration (ABW inventory all PENDING)
- FODS/FODT have Compat/ facades but no formal backfill inventory
- No automated tooling exists

**Path to OPERATIONAL:**
1. Build 5-module automated backfill system (~1 sprint)
2. Run Phase 1 pilot (NDJSON/TSV/SYLK) — validates scanner correctness
3. Complete Phase 2-4 over subsequent sprints

**Blocking factor:** Not blocking current Gate 11 candidates (FODS/FODT/Netpbm).
But BLOCKING for formats targeting Gate 11 in future (any format at "implementing" status
cannot reach "implemented" without completing its backfill migration).
