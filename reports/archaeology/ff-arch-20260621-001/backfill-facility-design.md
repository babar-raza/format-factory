# Backfill Facility Design — ff-arch-20260621-001

## Current State

**No governed backfill subsystem exists.** There is a migration plan in `registry/odf-ontology/migration-plan.yaml` and the `qname-to-code-map.yaml` defines targets, but no executable facility to safely move existing malformed src/ to canonical locations.

---

## Required Backfill Facility

### Purpose

Take existing Generation 1-2 source that uses format-prefixed names and:
1. Move canonical logic to the spec-hierarchy location (e.g., `Table/TableCell.cs`)
2. Keep format-specific facade at `Compat/Fods/FodsCell.cs`
3. Delegate: FodsCell wraps Table.TableCell
4. Update tests to test through both canonical and facade paths
5. Preserve all existing public API behavior (backwards compatibility)

---

## Backfill Design (Governed, Per-Format, Safe)

### Step 1: Inventory current src/

For each product, collect:
- All class names
- All method/function names
- All public API surface
- Each class's likely spec counterpart (from qname-to-code-map.yaml)
- Files at wrong location

Output: `registry/backfill/{format}-inventory.yaml`

### Step 2: Classify source symbols

For each class/function:
- `spec_aligned`: Already in correct location with correct name
- `facade_candidate`: In wrong location; should move to Compat/
- `canonical_candidate`: Should become canonical spec class
- `utility`: No spec equivalent; utility function only
- `unmapped`: Cannot be traced to spec element

Output: `registry/backfill/{format}-classification.yaml`

### Step 3: Generate canonical class skeletons

For each `canonical_candidate`, generate:
```
src/net/fods/Spec/Table/TableCell.cs  (canonical)
src/python/fods/table/table_cell.py   (canonical)
```
Using the FODT architecture_only stub pattern:
```cs
// spec_qname: "table:table-cell"
// spec_fact_ref: "FACT-FODS-006"
// canonical_class: "Table.TableCell"
public sealed class TableCell { ... }
```

### Step 4: Extract canonical implementation from existing source

Move the existing implementation from `FodsCell.cs` into `Spec/Table/TableCell.cs`.
This is the critical migration step. Do NOT copy — move + slim down.

### Step 5: Create facade at Compat/ location

```cs
// Compat/Fods/FodsCell.cs
public sealed class FodsCell {
    private readonly Table.TableCell _canonical;
    // delegates all calls to _canonical
}
```

### Step 6: Update all internal references

Replace all `FodsCell` usage inside the product with `Table.TableCell`.
`FodsCell` remains for external/public API only.

### Step 7: Update tests

Add test that:
- `Table.TableCell` works directly
- `FodsCell` facade produces identical output
- Round-trip test passes through canonical path

### Step 8: Validate with governance

Run:
- Source structure baseline validator (no LOC regressions)
- QName compliance check (new canonical path matches map)
- Test suite (all tests must pass)
- `sprint_executor_validate.py` on evidence declaration

### Step 9: Produce migration evidence

```
.local/evidences/backfill-{format}-001/
  backfill-inventory.yaml
  classification.yaml
  before-state/
  after-state/
  test-results.log
  migration-evidence.yaml
```

---

## Priority Order for Backfill

1. **FODS .NET**: FodsCell, FodsSheet, FodsRow → Table.TableCell, Table.Table, Table.TableRow
2. **FODT Python**: Complete spec/ stubs; switch compat.py
3. **FODT .NET**: Complete Spec/ stubs; wire into FodtDocument
4. **FODS Python**: Fix triple nesting; add object model classes
5. All other formats: defer until ODF formats demonstrate the pattern

---

## Risk Assessment

| Format | Backfill Risk | Reason |
|--------|--------------|--------|
| FODS .NET | MEDIUM | Well-understood; FodsCell is small (74 LOC); tests exist |
| FODT Python | LOW | compat.py bridge already in place |
| FODT .NET | LOW | Spec/ stubs already generated; just need implementation |
| FODS Python | HIGH | Triple nesting must be fixed first; object model is missing |
| Other formats | LOW-MEDIUM | Simpler structures; less spec complexity |

---

## Rollback Plan

Each backfill sprint:
1. Operates on a separate git branch
2. Includes a ROLLBACK_COMMIT reference
3. Old Compat/ files are preserved until all tests pass
4. Feature flag in `compat.py` controls which layer is used
5. CI must pass before Compat/ old files are removed
