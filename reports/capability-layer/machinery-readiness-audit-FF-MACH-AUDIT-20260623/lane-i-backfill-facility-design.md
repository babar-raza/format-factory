# Lane I — Backfill Facility Design
**Plan:** sorted-purring-stardust | **Taskcard:** TC-LANE-I | **Requirement:** REQ-LANE-I

## 1. Current State — No Backfill Facility Exists

### Search Results
- No files matching backfill*.py, migrate*.py, or rename*.py in tools/
- `tools/spec/generate_canonical_stubs.py` produces architecture_only stubs only (skeleton spec classes with `# GENERATED — architecture_only` markers)
- No automated mechanism to rename existing production classes to canonical names

### Naming Compliance — 3 Key Formats

| Format | Production Code | Naming | Canonical Target | Status |
|--------|----------------|--------|-----------------|--------|
| FODS | fods/models.py | FodsCell, FodsSheet, FodsDocument | Table.TableCell, Table.Table, Office.Document | Format-prefixed (NOT canonical) |
| FODS | fods/Compat/ | FodsCell, FodsSheet, FodsDocument | Facades | Empty shells (architecture markers) |
| NDJSON | ndjson/ | NdjsonRecord | Ndjson.Record | Format-prefixed |
| XCF | xcf/ | XcfImage | Xcf.Image | Format-prefixed |

**Key finding:** Both production code (models.py) AND Compat/ facades use format-prefixed names. The canonical naming (spec QName → canonical class) exists only in spec/ stubs which are architecture_only skeletons.

## 2. Backfill Facility Design — 5-Tool Architecture

### Tool 1: inventory.py (READ-ONLY)
- Scans src/python/{format}/ for production classes
- Reads shared/qname-registry/{format}.yaml for expected canonical names
- Outputs .local/backfill/{format}-backfill-plan.yaml with class mapping
- Example output:
  ```yaml
  format: fods
  classes:
    - current_name: FodsCell
      current_file: src/python/fods/models.py
      canonical_name: TableCell
      canonical_module: Table
      qname: "table:table-cell"
      migration_required: true
  ```

### Tool 2: plan_generator.py (READ-ONLY)
- Reads backfill-plan.yaml
- For each class: generates proposed rename, namespace move, compatibility_shim_needed flag, affected_test_files list
- Outputs human-readable migration plan

### Tool 3: executor.py (WRITE — REQUIRES --approved)
- **NOT created this sprint** — requires separate user-approved plan
- Would execute the migration plan: rename classes, update imports, create Compat/ shims
- Safety gate: --approved flag is MANDATORY, no default execution

### Tool 4: test_migrator.py (WRITE — after executor)
- Updates test imports and assertions after class renames
- Runs affected tests to verify no regressions

### Tool 5: validator.py (READ-ONLY)
- Post-migration validation: all renamed classes importable, all tests pass, QName registry entries match

### Key Constraints
- **inventory.py and plan_generator.py are safe** — read-only analysis tools
- **executor.py requires --approved flag** — no migration without explicit user authorization
- **Migration priority:** FODS first (most mature, GREEN rating), then NDJSON, then remaining formats
- **This sprint scope:** Create inventory.py + plan_generator.py ONLY (tools 1-2)
