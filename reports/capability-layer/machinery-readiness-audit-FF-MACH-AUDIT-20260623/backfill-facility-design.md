# Backfill Facility Design
**Plan:** sorted-purring-stardust | **Taskcard:** TC-SOL-001-03 | **Requirement:** REQ-SOL-001

## Purpose
Automate the migration from format-prefixed naming (FodsCell) to canonical naming (Table.TableCell) as defined by the QName registry.

## 5-Tool Architecture

### Tool 1: tools/backfill/inventory.py
**Type:** READ-ONLY analysis
**Input:** src/python/{format}/, shared/qname-registry/{format}.yaml
**Output:** .local/backfill/{format}-backfill-plan.yaml

```python
def scan_format(format_name: str, repo_root: Path) -> dict:
    """Scan format package for production classes and compare to QName registry."""
    # 1. List all .py files in src/python/{format}/ (excluding __pycache__, build)
    # 2. AST-parse each file for class definitions
    # 3. Read shared/qname-registry/{format}.yaml for canonical mappings
    # 4. Match production classes to registry entries
    # 5. Output: {format, classes: [{current_name, current_file, canonical_name, canonical_module, qname, migration_required}]}
```

### Tool 2: tools/backfill/plan_generator.py
**Type:** READ-ONLY analysis
**Input:** .local/backfill/{format}-backfill-plan.yaml
**Output:** .local/backfill/{format}-migration-plan.md (human-readable)

For each class requiring migration:
- Proposed rename (FodsCell → TableCell)
- Proposed namespace move (fods/models.py → fods/spec/table/table_cell.py)
- Compatibility shim needed? (yes → create Compat/fods_cell.py facade)
- Affected test files (grep for import references)
- Risk assessment (how many callers? public API impact?)

### Tool 3: tools/backfill/executor.py (NOT THIS SPRINT)
**Type:** WRITE — requires --approved flag
**Safety gate:** Will NOT execute without explicit `--approved` CLI argument
**Actions:** Rename classes, move files, update imports, create Compat/ shims

### Tool 4: tools/backfill/test_migrator.py (NOT THIS SPRINT)
**Type:** WRITE — runs after executor
**Actions:** Update test imports, rename test fixtures, re-run affected tests

### Tool 5: tools/backfill/validator.py (NOT THIS SPRINT)
**Type:** READ-ONLY post-migration check
**Actions:** Verify all renamed classes importable, all tests pass, QName matches

## Migration Priority Order
1. **FODS** — Most mature (GREEN), 12 QName entries, 3 production classes
2. **NDJSON** — GREEN, 2 QName entries, 1 production class
3. **XCF** — ORANGE, 3 QName entries, read-only parser
4. **PGM** — YELLOW, 2 QName entries
5. Remaining formats by maturity

## --approved Gate Design
```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved", action="store_true",
                        help="REQUIRED: Explicitly approve migration execution")
    args = parser.parse_args()
    if not args.approved:
        print("ERROR: Migration requires --approved flag. Review the plan first.")
        print("Run: python tools/backfill/plan_generator.py --format <format>")
        sys.exit(1)
```

## File Ownership
| Tool | Creates/Modifies |
|------|-----------------|
| inventory.py | .local/backfill/{format}-backfill-plan.yaml |
| plan_generator.py | .local/backfill/{format}-migration-plan.md |
| executor.py | src/python/{format}/**, Compat/** |
| test_migrator.py | tests/python/{format}/** |
| validator.py | (none — read-only) |
