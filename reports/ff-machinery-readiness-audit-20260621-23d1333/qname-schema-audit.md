# QName Schema Audit — Format Factory Machinery Readiness Audit
# Sprint ID: ff-machinery-readiness-audit-20260621-23d1333

## Summary

The QName schema exists as a well-designed **planning document** with no runtime enforcement.
The canonical class hierarchy has been designed and documented but NOT implemented in any
src/ code. All current product code uses format-prefixed flat naming.

## What Exists

### Design Documents (reports/specification-authority-layer-mwp/qname-ontology/)

| File | Content | Status |
|------|---------|--------|
| prefix-namespace-registry.yaml | Maps XML prefix → URI → code module | EXISTS, well-formed |
| namespace-tree.yaml | ODF namespace element hierarchy | EXISTS, covers office/table/text |
| qname-to-code-map.yaml | Maps QName → canonical class → code path | EXISTS, 11 mappings |
| canonical-class-inventory.yaml | All required canonical classes with status | EXISTS, all NOT_IMPLEMENTED or facade_exists_no_canonical |
| migration-plan.yaml | 4-phase plan to migrate to canonical classes | EXISTS, ALL phases NOT_STARTED |
| legacy-alias-map.yaml | Maps legacy names to canonical targets | EXISTS |

### Key QName Mappings Defined (qname-to-code-map.yaml)

| Spec QName | Canonical Class | .NET Path | Python Path | Status |
|------------|----------------|-----------|-------------|--------|
| office:document | Office.Document | src/net/FormatFactory/Office/Document.cs | src/python/{format}/office/document.py | NOT IMPLEMENTED |
| office:body | Office.Body | src/net/FormatFactory/Office/Body.cs | ... | NOT IMPLEMENTED |
| table:table | Table.Table | src/net/FormatFactory/Table/Table.cs | ... | facade_exists_no_canonical |
| table:table-row | Table.TableRow | ... | ... | facade_exists_no_canonical |
| table:table-cell | Table.TableCell | ... | ... | facade_exists_no_canonical |
| text:p | Text.Paragraph | ... | ... | NOT IMPLEMENTED |
| text:h | Text.Heading | ... | ... | NOT IMPLEMENTED |

### Facades That Exist (but are NOT canonical classes)

| Format | Facade Name | File | Delegates to canonical? |
|--------|-------------|------|------------------------|
| .NET FODS | FodsDocument | src/net/fods/FodsDocument.cs | NO — IS the primary class |
| .NET FODS | FodsSheet | src/net/fods/Model/FodsSheet.cs | NO |
| .NET FODS | FodsRow | src/net/fods/Model/FodsRow.cs | NO |
| .NET FODS | FodsCell | src/net/fods/Model/FodsCell.cs | NO |
| .NET FODT | FodtDocument | src/net/fodt/FodtDocument.cs | NO |
| .NET FODT | FodtParagraph | src/net/fodt/Model/FodtParagraph.cs | NO |
| .NET FODT | FodtBody | src/net/fodt/Model/FodtBody.cs | NO |

## What Does NOT Exist

1. `src/net/FormatFactory/` — canonical namespace library (NOT created)
2. `src/net/FormatFactory/Office/` — Office namespace classes (NOT created)
3. `src/net/FormatFactory/Table/` — Table namespace classes (NOT created)
4. `src/python/{format}/office/` — format-specific office subfolder (NOT created)
5. `src/python/{format}/table/` — format-specific table subfolder (NOT created)
6. `tools/supervisor/qname_ontology_generator.py` — referenced in skill but NOT FOUND in tools/supervisor/
7. `spec_qname` attribute on any existing product class
8. Any runtime QName validator that checks product source
9. Any Compat/ subfolder in any format directory

## QName Enforcement Analysis

### At Spec Ingestion
- Status: **PARTIAL** — SAL has spec_normalizer.py, spec_indexer.py, fact_coverage_report.py
- Evidence: 78 real FODS facts with FACT-FODS-NNN IDs exist in spec-cache
- Gap: SAL pipeline does NOT emit facts into the main fact index (sal_master_runner.py bypasses all real tools)

### At SAL Fact Extraction
- Status: **BROKEN** — SAL emits template facts, not spec-derived facts
- Evidence: SAL test failure: `assert 'fods' in sal_index` → AssertionError (ZST is only format)

### At Capability Derivation
- Status: **DISCONNECTED** — Capability map has 3,166 entries but NOT derived from SAL facts
- Evidence: unified-capability-map.json has sal_enrichment field but no proof it was populated by SAL

### At Code Generation / Skills
- Status: **PARTIAL** — Skills declare spec_qname_required: true but QName generator tool is missing
- Evidence: spec-literal-qname-to-code-mapping skill references `qname_ontology_generator.py` which was not found

### At Product Source (src/)
- Status: **NOT IMPLEMENTED** — Zero canonical classes exist
- Evidence: Direct inspection of src/net/fods/, src/net/fodt/, src/python/fods/, etc.

### At Validators
- Status: **NOT WIRED** — Spec parity validator exists as a concept but no runtime gate exists
- Evidence: governance_validators.py has 38 validators, but no validate_qname_compliance validator was found

## Root Cause

The QName design was completed as documentation and ontology files but was NEVER
implemented as:
1. Source code refactoring
2. Generator tooling (qname_ontology_generator.py)
3. Wired validators in governance_validators.py
4. Backfill migration scripts

The migration-plan.yaml states all phases are NOT_STARTED and are "blocked until
system-healing gate passes (Lanes 1, 3, 6 complete)".

## Required Fix

1. Implement `tools/supervisor/qname_ontology_generator.py`
2. Add `validate_qname_compliance` validator to governance_validators.py
3. Create canonical class library (`src/net/FormatFactory/`, `src/python/shared/`)
4. Execute migration phases 1-4 (per migration-plan.yaml)
5. Wire QName enforcement into skills and sprint closeout
