# Product Contract — Format Factory
**Mission:** MACHINERY-TRUTH-PRODUCT-CONTRACT-20260624
**Generated:** 2026-06-24
**Authority:** Derived from poc-targets.yaml, spec-to-feature-radical-correction-plan.md,
              registry/format-registry.yaml, and current HEAD source inspection.

---

## Python FOSS Product Contract

```yaml
product_contract:
  language: Python
  runtime: Python 3.11+
  license: Apache 2.0
  source_root: src/python/{format}/
  package_or_namespace_rules:
    - Each format is an independent installable package (setup.py or pyproject.toml)
    - Package name: format_factory_{format} (e.g. format_factory_fods)
    - Root package: src.python.{format} (import: from src.python.{format} import ...)
    - egg-info present for all 20 formats confirming installability

  qname_rules:
    - Every public class SHOULD have spec_qname attribute mapping to canonical QName
    - Canonical class naming: Spec QName → namespace:local-name → Namespace.ClassName
      e.g. table:table-cell → Table.TableCell (NOT FodsCell as primary)
    - Facade classes allowed ONLY in Compat/ subdirectory (e.g. FodsCell in Compat/)
    - QName compliance gated by shared/qname-registry/{format}.yaml status field
    - Status must reach 'verified' for continuation_allowed=True in product deepening

  hierarchy_rules:
    - Primary implementation: spec/{namespace}/{element}.py (architecture_only stubs)
    - Functional implementation: {format}_parser.py or {format}_codec.py (main module)
    - Analytics: {format}_analytics.py (arithmetic-heavy functions extracted from main)
    - Document model: {document_type}_document.py or models.py
    - Exceptions: exceptions.py (format-specific exception hierarchy)
    - Compat facades: Compat/{Format}{Element}.py (thin delegation wrappers only)

  file_rules:
    - One primary codec/parser module per format
    - Analytics extraction required when main module exceeds LOC cap (see source-structure-baseline.json)
    - Existing known_violations: baseline_loc_cap is FROZEN (write-once), never increased
    - New files exceeding 800 LOC or 60 functions → added to known_violations automatically

  public_api_rules:
    - __init__.py exports all public functions via explicit __all__ or dynamic discovery
    - Core functions: load_{format}(path), write_{format}(model, path)
    - Analytics: functional utilities returning int/float/bool
    - Model classes exposed for inspection and mutation

  parsing_contract:
    - load_{format}(path: str) → model dict or domain object
    - Raises format-specific exception (e.g. TomlError, SylkParseError) on invalid input
    - No external dependencies beyond stdlib for FOSS parsers

  object_model_contract:
    - Domain model classes (e.g. FodsWorkbook, AbwDocument) for complex formats
    - Simple formats may return dict/list directly
    - Model provides: inspect structure, access elements, enumerate children

  mutation_contract:
    - Set cell values, add/remove sheets, modify paragraphs
    - Mutation on domain model objects (not raw dicts)

  save_contract:
    - write_{format}(model, path: str) → None
    - Same-format save: file written to disk, reload produces equivalent model
    - Roundtrip fidelity: all core content preserved (not style, comments unless specified)

  export_contract:
    - {format}_to_{target}(path, ...) → str or None
    - Dogfood: use Format Factory's own libraries where available
      e.g. FODS → CSV via format-factory-csv; FODT → TXT/Markdown/HTML

  testing_contract:
    - tests/python/{format}/ directory per format
    - Layer 0: health check + smoke test (test_health_check.py)
    - Layer 1: focused unit tests per function/class
    - Layer 2: integration tests (load-edit-save-reload)
    - Arithmetic analytics tests: classified as 'arithmetic-only', skippable via --skip-arithmetic
    - Minimum: focused functionality tests for each public API function
    - POC targets must have: load, inspect, edit, save, reload, export tests

  packaging_contract:
    - setup.py or pyproject.toml per format in src/python/{format}/
    - Installable via pip install -e src/python/{format}/ --user
    - egg-info present after installation
    - All 20 formats currently installed in development mode

  documentation_contract:
    - README.md per format (minimal)
    - Docstrings on all public functions with param/return types
    - examples/ (optional; fods has examples/python/fods/edit_save_export_fods.py)

  quality_contract:
    - No monolithic files: analytics separation required above LOC cap
    - No arithmetic-only functions without GAP-ledger reference (V42 enforcement)
    - No spec_qname-less model classes for PRODUCT_SOURCE items (TC-GUARD-001)
    - py.typed marker encouraged (V-typed validator)

  forbidden_patterns:
    - src/python/{format}/{format}/{format}/... nested duplicate packages
    - Format-prefixed names as PRIMARY implementation (use canonical spec class)
    - Modifying baseline_loc_cap upward (write-once rule)
    - Arithmetic analytics without gap_ledger_ref in evidence
    - mod_{n}_times_{m} naming patterns (deepening suspension)

  allowed_exceptions:
    - architecture_only spec stubs in spec/ subdirectory (labeled with # GENERATED — architecture_only)
    - Compat/ facades as thin wrappers (delegation only, no behavior)
    - known_violations in source-structure-baseline.json (frozen baseline for pre-existing large files)

  poc_completion_criteria:
    - From installed package: load a file from disk
    - Inspect the object model meaningfully
    - Make at least one meaningful edit
    - Save to the same format
    - Reload and verify the edit survived
    - Export to at least one other format using Format Factory libraries
```

---

## .NET Commercial Product Contract

```yaml
product_contract:
  language: C# / .NET
  runtime: net10.0 (target; net8.0 compatible)
  license: Commercial (DEC-033 Option B — .NET Commercial Only)
  source_root: src/net/{format}/
  note: NOT src/dotnet/ — that is a Phase 0 placeholder only

  package_or_namespace_rules:
    - Project file: FormatFactory.{Format}.csproj
    - Root namespace: FormatFactory.{Format} (e.g. FormatFactory.Fods)
    - Shared libraries: src/net/csv/, src/net/html/, src/net/markdown/, src/net/txt/
    - Dogfood: exporters delegate to Format Factory's own .NET libraries

  qname_rules:
    - Spec/ subdirectory contains C# spec classes mirroring QName hierarchy
    - Canonical class: FormatFactory.{Format}.Spec.{Namespace}.{ClassName}
    - Model/ subdirectory: functional domain model classes (FodsSheet, FodsCell, etc.)
    - Compat facades may appear at format root (thin delegation to Model/ classes)

  hierarchy_rules:
    - {Format}Parser.cs — parsing entry point
    - {Format}Document.cs — root domain object
    - {Format}Writer.cs — serialization
    - {Format}*Exporter.cs — format export (CSV, HTML, JSON, Markdown, PDF, PNG, etc.)
    - Model/ — domain model classes (Sheet, Cell, Row, etc.)
    - Spec/ — architecture_only spec skeleton stubs
    - Exceptions/ — format-specific exceptions

  public_api_rules:
    - {Format}Parser.Parse(path) → {Format}Document
    - {Format}Writer.Write({Format}Document, path) → void
    - {Format}Document.{Operation}() — inspect, edit, enumerate
    - Exporter pattern: {Format}{Target}Exporter.Export({Format}Document, ...) → string/stream

  parsing_contract:
    - {Format}Parser.Parse(string path) → {Format}Document
    - {Format}Parser.ParseFromStream(Stream) → {Format}Document
    - Throws FormatFactory.{Format}.Exceptions.{Format}ParseException on error

  object_model_contract:
    - {Format}Document: root; enumerates sheets/pages/records
    - Sheet/page: contains rows/cells/paragraphs
    - Cell/element: value, type, formula (where applicable)
    - All operations tested in dotnet_status matrix (618 tests for FODS)

  mutation_contract:
    - AddSheet, RenameSheet, RemoveSheet, CopySheet
    - SetCellValue, InsertRow, DeleteRows, MergeCells, SetCellFormula
    - ClearSheet, GetUsedRange, SortRows

  save_contract:
    - {Format}Writer.Write({Format}Document, path) → void
    - Same-format roundtrip: save_after_edit_roundtrip = PASS (verified for FODS, FODT)

  export_contract:
    - {Format}CsvExporter — delegates to FormatFactory.Csv.CsvWriter (dogfood)
    - {Format}HtmlExporter — delegates to FormatFactory.Html.HtmlWriter (dogfood)
    - {Format}JsonExporter, {Format}MarkdownExporter, {Format}TxtExporter
    - All export operations in dotnet_status matrix = PASS for FODS and FODT

  testing_contract:
    - Minimum: all dotnet_status matrix operations covered (load, inspect, edit, save, export)
    - FODS: 618 .NET tests pass (as of last verified run)
    - Roundtrip tests with XML verification required (Gate 11 criterion C6: >= 3 roundtrip tests)

  packaging_contract:
    - FormatFactory.{Format}.csproj targets net10.0
    - Build: dotnet build FormatFactory.{Format}.csproj
    - NuGet publication: TRUE_EXTERNAL_GATE (credentials + Babar Raza authorization required)

  quality_contract:
    - Gate 11 criteria C1-C20 must pass before commercial release
    - C1: implementation_depth_score >= 4/5
    - C3: Every public method has >= 1 spec_fact_ref
    - C4: class_count >= 15 for complex formats
    - C5: .NET CI passes (build + test)
    - C6: >= 3 roundtrip tests with XML verification

  forbidden_patterns:
    - src/dotnet/ as a target path (obsolete; use src/net/)
    - Commercial-tier source before Gate 10 passed + DEC-033 resolved + Babar Raza authorization
    - Gate 11 self-approval (Babar Raza only)

  gate_11_status:
    - G11-G sub-gate: APPROVED by Babar Raza 2026-06-05 (FODS, FODT, Netpbm)
    - Full Gate 11 (commercial release): NOT APPROVED — requires Babar Raza final sign-off
    - Remaining criteria: customer-readiness-checklist.md (docs/governance/)
    - NuGet publication: TRUE_EXTERNAL_GATE
```

---

## Expected Proof Levels by Format (Python)

| Format | Current Status | Required for POC | Proof Level |
|--------|---------------|------------------|-------------|
| FODS | All POC ops PASS, installed, G11-G approved | POC_COMPLETE | PROOF_LEVEL_4 |
| FODT | All POC ops PASS, installed, G11-G approved | POC_COMPLETE | PROOF_LEVEL_4 |
| ZST | compress/decompress/probe PASS, installed | POC_COMPLETE | PROOF_LEVEL_4 |
| PBM | parse+write PASS, installed | POC_COMPLETE | PROOF_LEVEL_4 |
| PGM | parse+write PASS, installed | POC_COMPLETE | PROOF_LEVEL_4 |
| PPM | parse PASS, installed | POC_COMPLETE | PROOF_LEVEL_4 |
| SYLK | parse+sylk_to_csv PASS, installed | POC_COMPLETE | PROOF_LEVEL_4 |
| TSV | parse+write+export PASS, installed | POC_COMPLETE | PROOF_LEVEL_4 |
| ABW | parse+write+export PASS, installed | POC_COMPLETE | PROOF_LEVEL_4 |
| Gnumeric | parse+write+export PASS, installed | POC_COMPLETE | PROOF_LEVEL_4 |
| CSV | parse+write PASS, installed | POC_IN_PROGRESS | PROOF_LEVEL_3 |
| NDJSON | parse+write+analytics PASS, installed | POC_IN_PROGRESS | PROOF_LEVEL_3 |
| DIF | parse+write PASS (on hold) | HOLD | PROOF_LEVEL_2 |
| QOI | parse PASS (on hold) | HOLD | PROOF_LEVEL_2 |
| FODG | parse+write+export PASS | POC_IN_PROGRESS | PROOF_LEVEL_3 |
| ODS | parse+write PASS | POC_IN_PROGRESS | PROOF_LEVEL_3 |
| ODT | parse+write PASS | POC_IN_PROGRESS | PROOF_LEVEL_3 |
| XCF | parse+probe PASS | POC_IN_PROGRESS | PROOF_LEVEL_3 |
| FODP | parse PASS | POC_IN_PROGRESS | PROOF_LEVEL_2 |
| TOML | parse+write+config PASS | POC_IN_PROGRESS | PROOF_LEVEL_3 |

---

## Product Grading Gate

Product grading may proceed for:
- **Immediate** (continuation_allowed=True): ABW, FODS, FODT
- **With QName advancement**: all 17 remaining formats (require qname_compliance_status=verified)
- **On hold**: DIF, QOI (explicit policy decision — not blocked by machinery)

Product grading MUST NOT claim:
- POC_COMPLETE without verifying load→inspect→edit→save→reload→export from installed package
- architecture_only spec stubs as product progress
- Compat/ facades as behavioral implementations (they are empty shells)
- Arithmetic analytics without GAP-ledger references as spec-parity work
