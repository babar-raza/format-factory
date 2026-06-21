# QName Schema Audit — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## QName Schema Existence and Design

### Registry
- `registry/odf-ontology/qname-to-code-map.yaml` EXISTS (schema_version 1.0, generated 2026-06-15)
- Maps ODF QNames to canonical classes and paths
- Rule: `Spec QName -> Canonical Class -> Facade (Compat/ only)`
- Example: `table:table-cell -> Table.TableCell -> FodsCell (facade)`

### QName Validator
- `tools/validators/qname_structure_validator.py` EXISTS and FUNCTIONAL
- Scans src/python/ for spec_qname class attributes
- Checks `in_spec_dir` (whether class is in spec/ subdirectory)

### Current QName Validator Results (live run this session)

| Format | Status | Spec Classes | Compliant | Missing |
|--------|--------|-------------|-----------|---------|
| fods | COMPLIANT | 15 | 15 | 0 |
| fodt | COMPLIANT | 8 | 8 | 0 |
| zst | NO_SPEC_CLASSES | 0 | 0 | 0 |
| csv | NO_SPEC_CLASSES | 0 | 0 | 0 |
| ods | NO_SPEC_CLASSES | 0 | 0 | 0 |
| odt | NO_SPEC_CLASSES | 0 | 0 | 0 |
| abw | NO_SPEC_CLASSES | 0 | 0 | 0 |
| dif | NO_SPEC_CLASSES | 0 | 0 | 0 |
| fodg | NO_SPEC_CLASSES | 0 | 0 | 0 |
| fodp | NO_SPEC_CLASSES | 0 | 0 | 0 |
| Overall (all formats) | COMPLIANT | 23 | 23 | 0 |

Overall compliant because only formats WITH spec/ directories are counted.
The "non_spec_with_spec_qname: 6" represent Compat/ facade classes.

### FODS QName Structure (Python)

spec/ tree: `src/python/fods/spec/`
- office/: document.py, automatic_styles.py, body.py, spreadsheet.py
- table/: table.py, table_cell.py, table_row.py
- text/: (not listed)
- number/, style/ (present)

All 15 spec classes have `spec_qname` attribute. COMPLIANT.

### FODT QName Structure (Python)

spec/ tree: `src/python/fodt/spec/`
- text/: heading.py, list_.py, list_item.py, paragraph.py, span.py
- table/, office/ present

All 8 spec classes have `spec_qname` attribute. COMPLIANT.

### FODS Compat/ Facades (Python, UNTRACKED)

`src/python/fods/Compat/`:
- FodsDocument → inherits Document (spec/office/document.py), spec_qname="office:document"
- FodsSheet → inherits Sheet (spec), spec_qname set
- FodsCell → inherits TableCell (spec/table/table_cell.py), spec_qname="table:table-cell"

STATUS: Created but NOT committed. UNTRACKED. Will be lost if git clean is run.

### .NET QName Structure

`src/net/fods/Spec/`:
- Office/Document.cs — `QName = "office:document"`, GENERATED architecture_only
- Table/Table.cs, TableCell.cs, TableRow.cs — architecture_only stubs

`src/net/fodt/Spec/`:
- Text/Heading.cs, Text/Paragraph.cs etc. — architecture_only stubs
- Office/Body.cs — architecture_only stub

STATUS: These are STATIC placeholder classes with just a QName constant.
NOT real canonical implementation classes. NOT connected to production FodsDocument.cs.

### .NET Production Source (NO QName)

`src/net/fods/FodsDocument.cs`:
- Namespace: `FormatFactory.Fods` (NOT `FormatFactory.Fods.Office`)
- Class: `FodsDocument` (NOT `Office.Document`)
- No spec_qname or QName reference anywhere in production code
- No inheritance from Spec/ classes

### QName Enforcement Gap Analysis

| Enforcement Point | Expected | Actual Status |
|------------------|----------|--------------|
| Spec ingestion | SAL extracts qnames from spec | PARTIAL (auto-seeded) |
| SAL fact extraction | fact_id = FACT-FORMAT-NNN | EXISTS (4987 FODS) |
| Capability derivation | capabilities derive from SAL qnames | NOT CONNECTED |
| Feature planning | features map to qname capabilities | NOT CONNECTED |
| Code generation | skills generate qname-named classes | NOT WIRED |
| Namespace/module layout | src/{format}/spec/{ns}/{element}.py | FODS/FODT only |
| Folder layout | Compat/ for facades | FODS only (untracked) |
| Class naming | `ns:element` → CanonicalClass | FODS/FODT spec/ only |
| Test naming | tests reference spec_qname | NOT ENFORCED |
| Validators | qname_structure_validator active | FODS/FODT pass, others N/A |
| Backfill/migration | migrate existing src/ to qname | NOT BUILT |
| Gate checks | gate validates qname compliance | NOT IN GATE CRITERIA |
| Supervisor stop/go | supervisor blocks non-qname work | NOT IMPLEMENTED |

### Summary

FODS and FODT Python spec/ stubs now exist and pass the QName validator.
This is a MEANINGFUL improvement from the prior audit.
However:
1. The spec/ stubs are THIN scaffolding — no production logic in them
2. Production code (neutral_model.py, parser.py) is NOT qname-structured
3. Compat/ facades exist only for FODS and are untracked
4. All other 18+ formats have NO QName structure
5. .NET has architecture_only stubs, not real spec-shaped classes
6. No automated enforcement prevents new product code from being non-qname
