# Production Library Checklist — Format Factory

Binding checklist for all source code under `src/`. Enforced by
`tools/validators/source_structure_validator.py` and `tests/test_source_structure.py`.

## 1. File Size and Complexity Limits

- **Max 800 LOC** per `.py` or `.cs` file under `src/`.
- **Max 60 top-level function definitions** per file.
- Pre-existing violations tracked in `registry/source-structure-baseline.json`.
- Baseline violations must decrease over time, never increase.
- New violations block the sprint.

## 2. Module Structure (Python)

Every format package under `src/python/{format}/` must have at minimum:

| File | Purpose | Required? |
|------|---------|-----------|
| `__init__.py` | Public API re-exports only; no logic | Yes |
| `parser.py` or `{format}_parser.py` | Core parsing: `parse_{format}`, `parse_{format}_strict` | Yes |
| `analytics/` or `analytics.py` | All `{format}_*` analytics functions | Yes (if format has analytics) |
| `writer.py` or `{format}_writer.py` | Write/export functions | If applicable |
| `constants.py` | Namespace URIs, QNames, limits | If applicable |
| `models.py` | Dataclasses, domain objects | If applicable |
| `exceptions.py` | Custom exceptions | If applicable |

If `analytics.py` exceeds 800 LOC, split into `analytics/` subpackage with
categorized submodules (`_numeric.py`, `_structural.py`, `_text.py`, `_flags.py`).

## 3. Module Structure (.NET)

Each format gets its own project (`FormatFactory.{Format}.csproj`) with:

| File | Purpose |
|------|---------|
| `{Format}Document.cs` | Domain model (max 800 LOC) |
| `{Format}Parser.cs` | Parsing logic |
| `{Format}Writer.cs` | Serialization |
| `{Format}*Exporter.cs` | Cross-format export |
| `Model/*.cs` | Supporting model classes |

## 4. Layer Separation

| Layer | Purpose | Allowed Dependencies |
|-------|---------|---------------------|
| Parser | Format bytes -> domain model | Constants, Models |
| Model | Domain entities (spec-derived) | Constants only |
| Analytics | Computed properties from model | Parser (for load), Models |
| Writer | Domain model -> format bytes | Constants, Models |
| Export | Cross-format conversion | Parser, Models, target Writer |
| Compat | Facade aliases for backward compat | All layers (thin wrappers) |

Prohibited:
- Model depending on Parser internals
- Analytics depending on Writer
- Circular imports between layers
- Production logic in tests, scripts, or orchestration

## 5. Naming and Domain Mapping

- Analytics functions prefixed `{format_id}_` (e.g., `csv_row_count`)
- Parse functions: `parse_{format}` / `parse_{format}_strict` / `probe_{format}`
- No duplicate function definitions (grep before adding)
- No vague names: Utils, Helpers, Manager, Processor, Handler

## 6. Specification Traceability (ALL formats)

Every format module — ODF and non-ODF — must trace its domain model to specification concepts. The traceability mechanism differs by format family, but the requirement is universal.

### ODF formats (FODS, FODT, ODS, ODT, FODP, FODG)
- Classes must trace to spec QNames per `registry/odf-ontology/qname-to-code-map.yaml`
- Canonical naming: `Table.TableCell` (canonical) -> `FodsCell` (facade in Compat/ only)
- Constants must define ODF namespace URIs and QName constants
- Format-prefixed class names (FodsCell, FodtParagraph) only in Compat/

### Non-ODF formats (CSV, TSV, DIF, SYLK, NDJSON, TOML, PBM, PGM, PPM, QOI, XCF, ZST, Gnumeric, ABW)
- Domain model derived from format spec concepts (e.g., RFC 4180 fields, DIF vectors, SYLK cells)
- File-level or class-level docstrings must cite spec concepts (`spec_concept:` tag)
- Same structural rules apply: parser/model/analytics separation, 800 LOC limit, no orphan files

## 7. Import Stability

- `__init__.py` must re-export all public functions via `__all__`
- Moving a function between submodules must not change the public API surface
- Backward-compatible re-exports in original file after splitting

## 8. No Orphan Files

- Every `.py`/`.cs` under `src/` must have an owning purpose
- Recognized purposes: parser, writer, model, analytics, constants, exceptions, encoder, exporter, converter
- Unrecognized files flagged by `check_orphan_files`

## 9. Production Readiness

- No hardcoded local paths
- No global mutable state in library modules
- No debug/agent runtime dependencies
- No script-style code in library modules
- Error handling with format-specific exception hierarchy
- Input validation at system boundaries
- Deterministic behavior

## 10. Testing Requirements

- Unit tests for analytics functions
- Parser tests with sample files
- Round-trip tests (parse -> write -> re-parse) where applicable
- Regression tests before risky refactors
- No test may break when functions move between submodules
- Architecture tests in `tests/test_source_structure.py`

## 11. Governance Enforcement

- `source_structure_validator.py` runs on every autonomous-cycle
- `test_source_structure.py` runs on every pytest invocation
- V35 (hardened) blocks new monolithic files
- Gate 4 requires module structure compliance
- Gate 5 requires spec_qname/spec_concept traceability for ODF formats
- Canonical class inventory must improve monotonically

## 12. Baseline Monotonicity (write-once ceilings)

- `known_violations` entries in `registry/source-structure-baseline.json` have two fields:
  - `loc` — current live value (may be updated by detection scripts)
  - `baseline_loc_cap` — **write-once ceiling** set at grandfathering time; NEVER increase this
- Any sprint where a known_violation file grows beyond `baseline_loc_cap` is a **HARD BLOCK**
- The sprint closeout Step 0 script must NEVER update `loc` or `functions` for files already in `known_violations`
- It may only add NEW entries for files exceeding limits that are not yet tracked
- `source_structure_validator.py --check-baseline-growth` exits 1 if any violation exceeds its cap
- Enforcement: TC-MACH-001 (caps), TC-MACH-002 (validator), TC-MACH-006 (Step 0 fix)

## 13. New Module Structure Gate

Any new Python format module added to `src/python/` must contain at minimum:
- `__init__.py` — re-exports only, max 100 lines, no function implementations
- `{format}_parser.py` or `{format}_codec.py` — parsing logic
- `exceptions.py` — exception hierarchy, max 50 LOC
- `{format}_analytics.py` or `analytics/` subpackage — analytics functions

A monolithic single-file new module (all logic in one file) is rejected by
`source_structure_validator.py`. This rule applies to all new modules created after
2026-06-17. Existing 20 modules are grandfathered (see baseline).

## 14. `__init__.py` Size Cap

- All `__init__.py` files in `src/python/` are capped at **100 lines**
- Functions must not be implemented in `__init__.py` — only re-exports allowed
- Pattern: `from .{format}_analytics import {format}_word_count, ...`
- Large `__init__.py` files (17 of 20 modules currently exceed 100 lines) are grandfathered
  in `source-structure-baseline.json` and must decrease over time
- New format modules must comply immediately (no grandfathering for new modules)

## 15. Shared Core Required (new modules)

Cross-cutting concerns must NOT be re-implemented per format module:
- Exception base classes → `src/python/core/exceptions.py`
- File I/O and size guards → `src/python/core/io.py`
- Encoding constants and helpers → `src/python/core/encoding.py`

This rule is enforced starting from the first new format module added after
`src/python/core/` is created. Existing 20 modules are grandfathered until their
individual decomposition sprints. Creating `src/python/core/` is tracked in
`plans/healing/product-code-healing-plan.md`.

## 16. Cross-Language Architecture (RULE-CHECKLIST-CL-001 — added 2026-06-25)

Any format implemented in both .NET and Python must have equivalent conceptual architecture:
- Both must have a parser class, domain model class, and (where applicable) an exporter
- Public API surface ratio must not exceed 20% difference between .NET and Python implementations
- Naming must follow the same spec-QName-derived conventions in both languages

Enforcement: V59 `validate_cross_language_parity` (currently WARN-only). Upgraded to FAIL
for RELEASE_GATE items where the public API surface count differs >20% (see TC-GH-003, 2026-06-25).

Status: PARTIAL — V59 is WARN-only for non-RELEASE_GATE items until parity is achieved.

## 17. Import Direction (RULE-LIB-003 — added 2026-06-25)

Import direction within a format package MUST follow the dependency chain:

    Parser/Codec → Models → Analytics → Compat ← __init__.py

Forbidden patterns:
- `models.py` importing from `*_parser.py` or `*_codec.py`
- `Compat/*.py` importing from `*_analytics.py`
- `*_parser.py` importing from `Compat/`
- `__init__.py` importing from `spec/` (use Compat/ instead)

Enforcement: V75 `validate_dependency_direction` (WARN for existing grandfathered files; FAIL for new).
Status: WARN-only for existing 20 packages (grandfathered).

## 18. Error Handling Hierarchy (RULE-LIB-006 — added 2026-06-25)

Each format package under `src/python/{format}/` MUST define a format-specific exception:
- `exceptions.py` must exist in every format package
- At minimum one exception class derived from `Exception` (or `FormatFactoryError` when available)
- Parsers and codecs MUST NOT raise bare `ValueError` or `KeyError` for format errors

Enforcement: V76 `validate_error_handling_hierarchy` (WARN for existing; FAIL for new format packages).
Status: WARN-only for existing 20 packages (grandfathered).

## Validator Reference

```
python tools/validators/source_structure_validator.py                  # Human-readable full scan
python tools/validators/source_structure_validator.py --json           # Machine-readable
python tools/validators/source_structure_validator.py --check-baseline-growth  # Cap violation check
```

Baseline: `registry/source-structure-baseline.json`
Ontology: `registry/odf-ontology/qname-to-code-map.yaml`
Gap inventory: `docs/code-quality/src-architecture-gap-inventory.md`
Root cause analysis: `docs/code-quality/root-cause-analysis.md`
