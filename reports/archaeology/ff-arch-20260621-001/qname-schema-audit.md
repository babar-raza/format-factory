# QName Schema Audit — ff-arch-20260621-001

## QName Infrastructure Exists

### 1. QName-to-Code Map (registry/odf-ontology/qname-to-code-map.yaml)
**Status: EXISTS and well-formed**

Contains:
- 20+ ODF element QName mappings
- Canonical class names (e.g., `Table.TableCell`, `Text.Paragraph`)
- Expected .NET and Python paths
- Facade definitions (`FodsCell → Compat/Fods/`, `FodtDocument → Compat/Fodt/`)
- Spec section references
- Value type mappings

Example mapping:
```yaml
"table:table-cell":
  canonical_class: "Table.TableCell"
  dotnet_path: "src/FormatFactory/Table/TableCell.cs"     # DOES NOT EXIST
  python_path: "src/python/{format}/table/table_cell.py"  # DOES NOT EXIST
  facades:
    - name: "FodsCell"
      location: "Compat/Fods/"                           # DOES NOT EXIST
      delegates_to: "Table.TableCell"
```

**The map defines the target. The target does not exist.**

### 2. FODT QName Registry (shared/qname-registry/fodt.yaml)
**Status: EXISTS and populated**

Contains 9 QName entries (office:body, text:p, text:h, text:span, text:list, text:list-item,
table:table, table:table-row, table:table-cell), all with:
- `status: architecture_only`
- `dotnet_file:` pointing to existing stub files in `src/net/fodt/Spec/`
- `python_file:` pointing to existing stub files in `src/python/fodt/spec/`

**All entries are `architecture_only`. No entry is `implemented`.**

### 3. ODF Ontology (registry/odf-ontology/)
Contains:
- `attribute-property-map.yaml`
- `canonical-class-inventory.yaml`
- `containment-graph.yaml`
- `legacy-alias-map.yaml`
- `migration-plan.yaml`
- `namespace-tree.yaml`
- `naming-exceptions.yaml`
- `prefix-namespace-registry.yaml`
- `qname-to-code-map.yaml`

**Rich ontology infrastructure exists but is NOT enforced or used in source generation.**

### 4. QName Ontology Generator (tools/supervisor/qname_ontology_generator.py)
**Status: EXISTS**

Generates QName-to-code maps from spec facts. Output goes to `.local/qname-output/`.
Evidence: `.local/qname-output/FODS/`, `FODT/`, `FODG/`, `FODP/` directories exist.

### 5. SAL QName Test (tests/specification-authority-layer/test_sal_qname_prefix_correctness.py)
**Status: EXISTS**

Tests that QName prefixes match namespace URIs in spec outputs.

---

## QName Compliance Gap Analysis

### Is QName schema properly implemented?
**NO.** The canonical class hierarchy (Generation 4) does not exist in `src/`. Only skeleton stubs exist for FODT.

### Is QName schema integrated into generation?
**PARTIALLY.** The `qname_ontology_generator.py` produces maps but does not generate source code from them.
No code generator converts `Table.TableCell` mapping into actual `Table/TableCell.cs` files.

### Is QName schema integrated into validation?
**MINIMALLY.** `test_sal_qname_prefix_correctness.py` validates prefix/namespace consistency.
No validator checks whether `src/` classes match the canonical map.

### Is QName schema integrated into skills?
**NO.** Skills (`add-python-api.md`, `add-dotnet-api.md`) do not require or verify QName compliance.
Skills are free to name classes `FodsCell` or `FodsDocument` without a registry check.

### Is QName schema integrated into product deepening?
**NO.** Product deepening sprints generate functions like `fods_sheet_count()` without any
requirement to reference spec QNames or canonical class names.

---

## QName Translation Standard: Current vs Required

### Current (observed in src/)
- `FodsCell` — format-prefixed, not spec-derived
- `FodtParagraph` — format-prefixed, not spec-derived
- `FodsDocument` — format-prefixed, not spec-derived
- `Table.TableCell` in FODT Spec/ — correct, but architecture_only
- `Text.Paragraph` in FODT Spec/ — correct, but architecture_only

### Required (per qname-to-code-map.yaml)
- Primary class: `Table.TableCell` in `src/FormatFactory/Table/TableCell.cs`
- Facade: `FodsCell` in `Compat/Fods/FodsCell.cs` delegating to `Table.TableCell`
- Python: `table_cell.py` in `src/python/fods/table/table_cell.py`

### Gap
The qname-to-code-map defines the required standard. Zero implementations meet it.
The FODT stubs are the closest (correct names, wrong status: architecture_only).

---

## QName Compliance Score by Product

| Product | Has QName map entry | Canonical class exists | Facade exists | Compliance |
|---------|--------------------|-----------------------|---------------|------------|
| .NET FODS | Yes (in odf-ontology map) | NO | NO (FodsCell IS the implementation) | Red |
| .NET FODT | Yes (in shared/qname-registry/fodt.yaml) | NO (stubs only) | NO | Orange |
| Python FODS | Yes | NO | NO | Red |
| Python FODT | Yes | NO (stubs only) | Partially (compat.py switch) | Orange |
| All others | No map entry | NO | NO | Gray |
