# Lane B: QName Schema Audit
# Sprint: ff-machinery-readiness-audit-20260625

## 1. QName Schema Definition

**Location:** shared/qname-registry/schema.yaml
**Coverage:** 20 format YAML files + schema.yaml

### Required Fields
```yaml
qname:          # e.g. "table:table-cell" — prefix:local-name
namespace_uri:  # e.g. "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
local_name:     # e.g. "table-cell"
canonical_class: # e.g. "Table.TableCell" (dot-notation, namespace.Class)
spec_fact_ref:  # e.g. "FACT-FODS-006" — linkage to SAL verified-facts
status:         # seeded | architecture_only | implementing | implemented | stable | deprecated
source_layer:   # Spec | Public | Compat | Reading | Writing | Validation | Conversion | Internal
```

### Optional Fields
```yaml
facade_names:   # list of legacy/format-prefixed class names mapping to canonical
python_file:    # relative path to Python canonical spec class file
dotnet_file:    # relative path to .NET canonical spec class file
```

### Evidence (shared/qname-registry/fods.yaml — most complete, verified 2026-06-25)
FODS has 12 entries, all status=implemented:
```
office:document  → Office.Document  → FodsDocument   — FACT-FODS-001
office:body      → Office.Body      → FodsBody        — FACT-FODS-002
office:spreadsheet → Office.Spreadsheet → FodsSpreadsheet — FACT-FODS-003
table:table      → Table.Table      → FodsSheet       — FACT-FODS-004
table:table-row  → Table.TableRow   → FodsTableRow    — FACT-FODS-005
table:table-cell → Table.TableCell  → FodsCell        — FACT-FODS-006
table:covered-table-cell → Table.CoveredTableCell → FodsCoveredCell — FACT-FODS-023
text:p           → Text.Paragraph   → FodsParagraph   — FACT-FODS-007
text:span        → Text.Span        → FodsSpan        — FACT-FODS-007
office:automatic-styles → Office.AutomaticStyles → FodsAutomaticStyles — FACT-FODS-008
style:style      → Style.Style      → FodsStyle       — FACT-FODS-009
number:date-style → Number.DateStyle → FodsDateStyle   — FACT-FODS-010
```

**Canonical naming rule (BINDING from spec-to-feature-radical-correction-plan.md §1):**
```
Spec QName → Canonical Class → Facade (Compat/ only)

NEVER use format-prefixed names as PRIMARY implementation targets.
ALWAYS implement canonical spec-literal class FIRST, then facade wrapper.

Examples:
  table:table-cell → Table.TableCell → FodsCell (facade)
  text:list        → Text.List       → FodtList (facade)
```

---

## 2. QName Validator Coverage

### Active Validators (tools/supervisor/governance_validators.py)

| Validator | Line | Purpose | Blocking? |
|---|---|---|---|
| V43 validate_canonical_registry_entry_exists | ~2750 | Ensures spec/ class files have spec_qname | YES (for production; WARN during bootstrap) |
| V44 validate_facade_delegates_to_spec | ~2790 | Ensures Compat/ files don't use architecture_only stubs as production facades | WARN-only |
| V49 validate_spec_qname_in_changed_files | ~3028 | Checks spec/ class files in changed_files have spec_qname | WARN-only |
| V36 validate_no_stub_tests | ~2364 | Rejects tests with >80% weak assertions (spec_qname-only) | YES |
| V48 validate_architecture_only_stub_gate | end of file | Blocks RELEASE_GATE items citing architecture_only stubs | YES for RELEASE_GATE |
| V53 validate_spec_qname_classvar | ~3100 | Verifies spec_qname is ClassVar (not instance field) | YES |
| V68 knowledge_freshness_validator.py | separate | Checks VERIFIED_CURRENT contracts vs source_hashes | WARN-only |

**Total active governance validators:** 48 (as of 2026-06-24, governance_validator_runner.py)
**Governance test coverage:** 82 tests pass (tests/supervisor/test_governance_validators.py)

### Enforcement Analysis

| Rule | Code-Enforced | Prompt-Only | Notes |
|---|---|---|---|
| spec_qname required in spec/ classes | YES (V43) | — | Active; blocking in production |
| Canonical class naming (not format-prefixed) | YES (V45) | — | V45 blocks format-prefixed names outside Compat/ |
| Compat/ facade delegates to spec class | WARN (V44) | — | Not blocking yet |
| spec_qname ClassVar (not instance field) | YES (V53) | — | Blocking |
| Tests must not be pure stub assertions | YES (V36) | — | >80% weak = fail |
| Lane DAG (machinery before product) | NO | YES | **GAP: SUP-GAP-001** |
| Capability-to-feature linkage required | YES (TC-GUARD-001) | — | BLOCK mode since 2026-06-18 |
| SAL fact extraction before product work | NO | YES | **GAP: SAL-GAP-001** |

---

## 3. Per-Format QName Status Summary

### Python Formats — QName Compliance Level

| Format | Primary QName | Spec Layer | Compat Layer | Domain Model | Compliance |
|---|---|---|---|---|---|
| FODS | office:document | ✓ implemented (12 entries) | ✓ 10+ facades | ✓ FodsDocument/models.py | FULL |
| FODT | office:document | ✓ implemented (8+ entries) | ✓ 4 facades (list, list_item, table, table_row) | ✓ FodtDocument/models.py | FULL |
| CSV | csv:record | ✓ spec/record/record.py | ✓ csv_record.py | ✓ CsvDocument.models.py | FULL |
| NDJSON | ndjson:record | ✓ spec/record/ | ✓ NdjsonRecord authority-only | ✓ NdjsonDocument.models.py | FULL |
| TSV | tsv:record | ✓ spec/record/ | ✓ tsv_record.py | ✓ TsvDocument.models.py | FULL |
| Gnumeric | gnumeric:workbook | ✓ spec/workbook/ | ✓ GnumericWorkbook/Sheet | ✓ GnumericDocument.models.py | FULL |
| ABW | abiword:document | ✓ spec/document/ | ✓ AbwDocument/Paragraph | ✓ AbwDocument.models.py | FULL |
| TOML | toml:table | ✓ spec/table/ | ✓ TomlKey/Table | ✓ TomlDocument.models.py | FULL |
| ZST | zst:frame | ✓ spec/frame/ | ✓ ZstFrame/Block | ✓ ZstDocument.models.py | FULL |
| ODS | table:table | ✓ spec/table/ | ✓ OdsSheet/Cell/Document | — (no models.py) | IMPLEMENTING |
| ODT | text:paragraph | ✓ spec/text/ | ✓ OdtParagraph/Document | — (no models.py) | IMPLEMENTING |
| SYLK | sylk:format | ✓ spec/row/ | ✓ SylkCell/Row/Header | — (no models.py) | IMPLEMENTING |
| DIF | dif:data | ✓ spec/table/ | ✓ DifVector/Header/Datum | — (no models.py) | IMPLEMENTING |
| FODG | draw:frame | ✓ spec/draw/ | ✓ FodgPage/Document | — (no models.py) | IMPLEMENTING |
| FODP | draw:page | ✓ spec/draw/ | ✓ FodpPage/Document | — (no models.py) | IMPLEMENTING |
| XCF | xcf:image | ✓ spec/layer/ | ✓ XcfLayer/Channel/Header | — (no models.py) | IMPLEMENTING |
| PBM | pbm:bitmap | ✓ spec/bitmap/ | ✓ PbmBitmap/Header | — (no models.py) | IMPLEMENTING |
| PGM | pgm:graymap | ✓ spec/graymap/ | ✓ PgmGraymap/Header | — (no models.py) | IMPLEMENTING |
| PPM | ppm:pixmap | ✓ spec/pixmap/ | ✓ PpmPixmap/Header | — (no models.py) | IMPLEMENTING |
| QOI | qoi:chunk | ✓ spec/chunk/ | ✓ QoiChunk/Header/EndMarker | — (no models.py) | IMPLEMENTING |

### .NET Formats — QName Compliance Level

| Format | Primary QName | Spec Layer | QName in Source | Compliance |
|---|---|---|---|---|
| FODS | office:document | ✓ Spec/Office/Document.cs + Spec/Table/TableCell.cs | ✓ FodsDocument references spec classes | PARTIAL |
| FODT | office:document | ✓ Spec/Office/ stubs | ✓ FodtDocument + FodtDocumentAccessor | PARTIAL |
| Netpbm | pbm:bitmap etc | — (no Spec/ directory) | — (no spec_qname in .NET) | NOT_PROVEN |
| CSV | csv:record | — (no Spec/ directory) | — (no spec_qname in .NET) | NOT_PROVEN |
| NDJSON | ndjson:record | — (no Spec/ directory) | — (no spec_qname in .NET) | NOT_PROVEN |
| TSV | tsv:record | — (no Spec/ directory) | — (no spec_qname in .NET) | NOT_PROVEN |
| ZST | zst:frame | — (no Spec/ directory) | — (no spec_qname in .NET) | NOT_PROVEN |

---

## 4. SAL Chain Status

Per reports/machinery-truth/ and reports/spec-authority-machinery/ evidence:

### CHAIN_INTACT (10 formats)
ODS, ODT, FODS, FODT, FODG, FODP, PBM, PGM, PPM, QOI
- Evidence: SAL spec parser exists for ODF/image spec layers
- Spec facts flow from verified-facts.yaml → capability map → gap-ledger
- QName registries seeded from actual spec section references

### CHAIN_BROKEN_AT_SAL (10 formats)
ABW, CSV, DIF, GNUMERIC, NDJSON, SYLK, TOML, TSV, XCF, ZST
- Evidence: SAL parser does not cover RFC/schema-based specs
- spec_fact_refs are provisional (e.g., FACT-CSV-001, FACT-CSV-002 — manually created)
- QName registries seeded from schema documentation, not SAL extraction
- 10 GAP-CHAIN-*-SAL entries in gap-ledger.json (P3/LOW priority per MEMORY.md)
- **Assessment:** EXPECTED state, not a regression. Non-ODF formats require different SAL strategy.

---

## 5. Backfill Scope Assessment

### Current Backfill Inventory
- **Location:** docs/audits/python-qname-backfill-inventory.csv
- **Coverage:** ABW format ONLY (170+ symbols)
- **Columns:** format, file_path, symbol_name, current_location, inferred_domain, inferred_qname, source_fact_ref, public_api_impact, tests_existing, tests_needed, migration_status, reviewer_verdict, notes
- **Status values:** PENDING (most), ANALYTICS_SUSPENDED_ROTATION, NO_QNAME_MAPPING

### Gap: 19 formats lack backfill inventory
- No automated scan-and-map tool exists for the remaining 19 Python formats
- Compat/ facades for FODS (10 facades) and FODT (4 facades) were created manually
- No qname-backfill skill found in .claude/commands/ (checked)
- Skill-registry.yaml does not list a qname-backfill skill
- **Verdict: BACKFILL FACILITY EXISTS FOR 1/20 FORMATS ONLY**

---

## 6. Qname Enforcement Design Assessment

### What is enforced at each layer

| Layer | Enforced? | How | Gaps |
|---|---|---|---|
| Spec ingestion | NO | SAL dormant; manual facts only | SAL-REPAIR-001 needed |
| SAL fact extraction | PARTIAL | 3/20 tools active; 17 dormant | SAL-REPAIR-001 |
| Capability derivation | PARTIAL | capability_map_generator.py reads facts | Never auto-triggered |
| Feature planning | NO | _EXPANSION_GOALS hardcoded | CAPABILITY-REPAIR-001 |
| Code generation | PARTIAL | FeatureFactory patterns exist | Never called by loops |
| Namespace/module layout | YES | V43, V45 validators active | — |
| Folder layout | YES | spec/{namespace}/{element}.py convention | Manual only |
| Class naming | YES | V45 blocks format-prefixed outside Compat/ | — |
| Test naming | WARN | V36 checks stub tests | Not spec-naming specific |
| Documentation refs | NO | No validator checks spec § references | Gap |
| Backfill/migration | MINIMAL | ABW only; no automated tool | QNAME-BACKFILL-001 needed |
| Gate checks | YES (partial) | V48 blocks arch-only stubs in RELEASE_GATE | V43 WARN not FAIL for implementing |
| Supervisor stop/go | NO | Prompt-only; no code-enforced gate | SUPERVISOR-LANES-001 needed |

---

## 7. Findings Summary (Lane B)

**Strengths:**
- Schema is well-defined with clear lifecycle (seeded→stable)
- 20 format registries complete with canonical_class in dot-notation
- V43/V44/V45/V48/V49/V53 validators active and tested
- FODS is the gold standard: 12 qnames, all implemented, 45/45 V53 tests PASS

**Gaps:**
- .NET formats lack spec_qname attributes in source code (no equivalent validators)
- Backfill covers ABW only; 19 formats need automated inventory scan
- V43 is WARN (not FAIL) for formats at "implementing" status — allows accumulation without pressure
- No automated backfill/migration script; all Compat/ migrations were manual
- Folder structure (spec/{namespace}/{element}.py) exists for 20 Python formats but is NOT enforced
  by any validator — it's convention-only
- CHAIN_BROKEN_AT_SAL for 10 non-ODF formats means their qnames are unverifiable against spec text
