# Production Readiness Standard — Format Factory

**Authority:** This document is the single authoritative code-quality contract for Format Factory.
It is binding on all source code under `src/`. Automated validators enforce these rules.

**Effective:** 2026-06-25 (updated from 2026-06-18; validator suite expanded to V68)
**Enforced by:** `tools/validators/validate_source_architecture.py`, `tools/validators/source_structure_validator.py`, `tools/supervisor/governance_validators.py`, `tools/supervisor/governance_validators_ext.py`, `tools/supervisor/governance_validators_signal.py`, `tools/supervisor/knowledge_freshness_validator.py`

---

## 1. Architecture and Library Design

### 1.1 Package Boundaries (Python)

Every format package under `src/python/{format}/` must be a proper library package with clear module boundaries:

| Module | Purpose | Max LOC | Required? |
|--------|---------|---------|-----------|
| `{format}_parser.py` or `parser.py` | Format bytes → domain model | 800 | Yes |
| `neutral_model.py` or `models.py` | Domain entities (spec-derived) | 800 | Yes |
| `analytics.py` or `analytics/` | All analytics/statistics functions | 800 per file | Yes (if format has analytics) |
| `exceptions.py` | Format-specific exception hierarchy | 50 | Yes |
| `__init__.py` | Re-exports only — no logic | 100 | Yes |
| `writer.py` or `{format}_writer.py` | Domain model → format bytes | 800 | If writable |
| `constants.py` | Namespace URIs, QNames, limits | 200 | If applicable |

**Anti-monolith rule (RULE-AM-003):** No single file may exceed 800 LOC (new files; existing violations frozen at `baseline_loc_cap` in `registry/source-structure-baseline.json`).

**Anti-monolith rule (RULE-AM-004):** No single file may define more than 60 functions (new files; existing violations frozen).

### 1.2 Package Boundaries (.NET)

Every format project under `src/net/{Format}/` must separate concerns:

| File | Purpose | Max LOC |
|------|---------|---------|
| `{Format}Document.cs` | Domain model — pure data, no I/O | 800 |
| `{Format}Parser.cs` | Parsing/deserialization | 800 |
| `{Format}Writer.cs` | Serialization/write | 800 |
| `{Format}*Exporter.cs` | Cross-format export | 800 |
| `Model/*.cs` | Supporting model classes | 800 each |
| `Exceptions/{Format}Exception.cs` | Exception hierarchy | 200 |

### 1.3 Shared Infrastructure

Cross-cutting concerns must use shared modules, not per-format re-implementations:

- **Python:** `src/python/_shared/` contains base classes (`BaseParser`, `BaseCodec`) and shared exception hierarchy (`FormatFactoryError`, `ParseError`, `WriteError`)
- Every format's exception class must inherit from `src.python._shared.exceptions.FormatFactoryError`
- This rule applies to new format packages immediately; existing 20 packages migrate per their individual decomposition taskcard

---

## 2. Object Model Quality

### 2.1 Specification Traceability (ODF formats)

Every class in ODF format packages (FODS, FODT, ODS, ODT, FODP, FODG) must carry a `spec_qname` attribute mapping to the ODF specification concept. Example:

```python
class SpreadsheetCell:
    spec_qname = "table:table-cell"  # ODF spec §9.1.4
```

No product-progress claims for ODF formats without spec parity evidence (at least one class with `spec_qname`).

### 2.2 Specification Traceability (non-ODF formats)

Every parser and model file for non-ODF formats must include a `spec_concept:` tag in the module docstring. Example:

```python
"""
SYLK parser — Symbol Link file format.
spec_concept: SYLK cell record (B;Yrow;Xcol;Kvalue)
"""
```

### 2.3 Canonical Naming

- Canonical class names derive from spec QNames: `Table.TableCell`, not `FodsCell`
- Format-prefixed class names (e.g., `FodsCell`, `FodtParagraph`) are permitted ONLY in `Compat/` facades
- No format-prefixed class names as primary implementation targets in model files

---

## 3. Python Best Practices

### 3.1 Analytics Separation (RULE-AM-001 — binding effective immediately)

Analytics functions — functions that compute statistics, metadata summaries, or formula-based values from parsed file data — **MUST reside in `analytics.py`**, never in parser, codec, model, or `__init__.py` files.

**Detection pattern:** Functions with names matching `{format}_.+_(?:mod_\d+|times_\d+|plus_|minus_|div_)` are analytics functions and must be in `analytics.py`.

**Enforcement:** `validate_source_architecture.py` scans ALL Python files via AST on every `autonomous-cycle`. Analytics functions found outside `analytics.py` in non-grandfathered files are `FAIL` (blocks sprint).

### 3.2 `__init__.py` Size Limit (RULE-AM-002 — binding)

No `__init__.py` may exceed **100 LOC** (new files: no grandfathering). Existing files exceeding this limit are tracked in `source-structure-baseline.json` as `known_violations`.

Permitted content in `__init__.py`:
- Module docstring
- Imports from submodules (`from .analytics import ...`)
- `__all__` declaration

Functions must not be implemented in `__init__.py`. Pattern:
```python
from .{format}_analytics import {format}_word_count, {format}_char_count
from .{format}_parser import parse_{format}, parse_{format}_strict
__all__ = ["parse_{format}", "{format}_word_count", ...]
```

**Dynamic `__all__` pattern (RULE-AM-005 — binding for `__init__.py` > 60 exports):**

When a package has more than 60 public exports, use the dynamic `__all__` pattern instead of a static list:
```python
import sys as _sys
import types as _types
_FF_API_EXCLUDE = frozenset({"Any", "ClassVar", "Dict", "List", "Optional", "Path", "Set",
    "Tuple", "Union", "dataclass", "field", "TYPE_CHECKING"})  # typing + stdlib re-imports
__all__ = [
    k for k in vars(_sys.modules[__name__])
    if not k.startswith("_")
    and not isinstance(getattr(_sys.modules[__name__], k), _types.ModuleType)
    and k not in _FF_API_EXCLUDE
]
del _sys, _types, _FF_API_EXCLUDE
```

This pattern prevents module re-export pollution while keeping `__init__.py` under 100 LOC.
Star imports on the consumer side must add `# noqa: F401, F403, F405` when the exported names
are referenced in `__all__` string lists (ruff cannot trace star import contents).

### 3.3 Import Stability

- All public functions must be re-exported via `__all__` in `__init__.py`
- Moving a function between submodules must not change the public API surface
- Add backward-compatible re-exports if a function moves between submodules

### 3.4 No Orphan Files

Every `.py` file under `src/` must have a recognized owning purpose: parser, writer, model, analytics, constants, exceptions, encoder, exporter, converter, or codec. Unrecognized files are flagged by `check_orphan_files`.

### 3.5 Production Readiness

- No hardcoded local paths in library code
- No global mutable state in library modules
- No debug/agent runtime dependencies in production code
- No script-style code (guard required: `if __name__ == "__main__"`)
- Error handling via format-specific exception hierarchy
- Input validation at system boundaries (file I/O entry points)
- Deterministic behavior — same input produces same output

---

## 4. .NET Best Practices

### 4.1 Structure

- No `.cs` file exceeds 800 LOC (existing violations frozen at `baseline_loc_cap`)
- XML documentation required on all public APIs
- No single class exceeds 60 public methods
- Separate parser/model/writer/exporter/exception files per format

### 4.2 Model Purity

`{Format}Document.cs` must be a pure domain model:
- No I/O in the document model
- No business logic that belongs in parser or writer
- Spec-derived field names (traceability via XML doc comment referencing spec section)

---

## 5. Naming and Organization

### 5.1 Analytics Functions

Analytics functions must follow the naming convention: `{format_id}_{property}_{formula}`.

Examples: `csv_row_count`, `fodg_file_size_mod_293_times_19_plus_shape_count_times_3400`

### 5.2 Parse Functions

`parse_{format}` — standard parse; `parse_{format}_strict` — strict (raises on ambiguity); `probe_{format}` — probe without full parse.

### 5.3 Prohibited Names

No vague module names: `utils.py`, `helpers.py`, `manager.py`, `processor.py`, `handler.py`.

---

## 6. Testing and Verification

### 6.1 Test Layer Structure

| Layer | Scope | Location |
|-------|-------|----------|
| Layer 0 | Domain model unit tests (instantiation, field access) | `tests/python/{format}/` |
| Layer 1 | Parser tests (parse returns correct model for sample files) | `tests/python/{format}/` |
| Layer 2 | Roundtrip tests (load → save → reload → compare) | `tests/python/{format}/` |
| Layer 3 | Analytics tests (individual analytics function tests) | `tests/python/{format}/` |
| Layer 4 | Integration tests (cross-format conversion) | `tests/python/integration/` |

### 6.2 Test Requirements

- Unit tests for all analytics functions (at least one assertion per function)
- Parser tests with real sample files from `samples/by-format/{format}/`
- Roundtrip tests (parse → write → re-parse) for all writable formats
- Regression tests before any refactor involving moving functions between submodules
- Architecture tests in `tests/test_source_structure.py` run on every pytest invocation

### 6.3 No Production Logic in Tests

Tests must not contain production logic. Tests validate behavior; they do not implement format parsing or serialization.

---

## 7. Governance and Automation

### 7.1 Validator Suite

**68 validators** (V1-V68) run on every `autonomous-cycle` via `governance_validators.py` + extensions.
Complete list: `tools/supervisor/governance_validator_runner.py` (docstring). Key blocking validators:

| Validator | What it checks | Blocks sprint? |
|-----------|---------------|----------------|
| V1 `validate_monolith_detection` | LOC vs `baseline_loc_cap` (now using cap, not stale `loc`) | Yes (FAIL) |
| V2 `validate_source_architecture` | Analytics-in-parser (RULE-AM-001), `__init__.py` size (RULE-AM-002), new file LOC (RULE-AM-003), new file function count (RULE-AM-004) | Yes (FAIL for new violations) |
| V40 `validate_source_architecture_v40` | Anti-monolith separation check (updated RULE-AM-001/AM-003) | Yes (GOV_BLOCK) |
| V50 `validate_forbidden_module_names` | Blocks `*_analytics_extra.py`, `*_extra.py`, `*_misc.py` | Yes (FAIL) |
| V61 `validate_error_fallback_safety` | `write_plan_lock.py` must write ITERATION_REQUIRED correctly | Yes (FAIL on regression) |
| V62 `validate_spec_fact_refs_density` | PRODUCT_SOURCE items need ≥1 spec_fact_ref | Rework required |
| V67 `validate_maturity_signal_schema` | Maturity signal schema correctness | Yes (FAIL if malformed) |
| `run_full_scan` (source_structure_validator) | Proactive scan of all `src/python/` files vs `baseline_loc_cap` | Yes (WORSENED = FAIL) |

**WARN-only validators (V59-V66, V68):** cross-language parity, terminal closure completeness, public API surface ratio, py.typed markers, `__all__` declarations, multi-responsibility file detection, knowledge freshness. These do not block sprints but appear in rework_items.

### 7.2 Anti-Monolith Rules (Validator-Enforced)

- **RULE-AM-001:** Analytics functions MUST NOT exist in parser/model/codec files
- **RULE-AM-002:** `__init__.py` MUST NOT exceed 100 LOC (new files)
- **RULE-AM-003:** No new file may exceed 800 LOC
- **RULE-AM-004:** No new file may have > 60 functions

Existing violations with `baseline_loc_cap` entries are WARN (not FAIL) until their decomposition taskcard runs. New violations are always FAIL.

### 7.3 Baseline Monotonicity

`registry/source-structure-baseline.json` `known_violations` entries have:
- `loc` — current live value (informational only)
- `baseline_loc_cap` — **write-once ceiling**, never increase
- `baseline_functions_cap` — write-once function count ceiling

A file growing past its `baseline_loc_cap` is a `WORSENED` violation → FAIL → blocks sprint.

### 7.4 GOV_BLOCK Handling (BINDING — carve-out from Supreme Directive)

`GOV_BLOCK:monolith_detection_validator` and `GOV_BLOCK:validate_source_architecture` are **structural failures**, not transient closeout failures.

When a structural GOV_BLOCK fires:
1. Do NOT proceed to the next product deepening sprint
2. The NEXT sprint must be the analytics separation refactor for the blocking format
3. Only after the GOV_BLOCK is resolved may product deepening resume for that format
4. This is enforced by `check_continuation.py` returning STOP with `reason: structural_govblock_must_be_resolved_first`

### 7.5 Pre-Commit Gate

`.pre-commit-config.yaml` includes a hook that runs `validate_source_architecture.py --check-new-files` before every commit. New file violations are caught before they enter git history.

---

## 8. Refactoring Safety

### 8.1 Analytics Separation Protocol

When moving analytics functions from a codec file to `analytics.py`:

1. Run all format tests before any edit: `python -m pytest tests/python/{format}/ --tb=short`
2. Record exact passing test count as baseline
3. Create `src/python/{format}/analytics.py` (empty except docstring)
4. Move functions verbatim — no logic changes
5. In the codec file, temporarily add `from .analytics import *` for backward compat
6. In `__init__.py`, add `from .analytics import *`
7. Run all tests — must equal baseline (zero regressions)
8. Remove `from .analytics import *` from codec file; replace with explicit imports of non-analytics functions
9. Run tests again — must still equal baseline

### 8.2 Regression Safety

- No refactor may reduce passing test count
- `python -m pytest tests/ --tb=short` must pass before and after
- Run architecture validator before and after: `python tools/validators/validate_source_architecture.py src/python/{format}/`

---

## Enforcement Summary

| Rule | Enforcer | Severity |
|------|---------|---------|
| RULE-AM-001 (no analytics in codec) | `validate_source_architecture.py` AST scan | FAIL (blocks) |
| RULE-AM-002 (`__init__.py` ≤ 100 LOC) | `validate_source_architecture.py` | FAIL (new files) / WARN (existing) |
| RULE-AM-003 (no new file > 800 LOC) | `validate_source_architecture.py` + `source_structure_validator.py` | FAIL |
| RULE-AM-004 (no new file > 60 functions) | `validate_source_architecture.py` | FAIL |
| RULE-AM-005 (dynamic `__all__` for > 60 exports) | `governance_validators.py:validate_all_exports_declared` (V65) | WARN |
| Baseline monotonicity | `source_structure_validator.py` + `governance_validators.py` | FAIL (worsened) |
| Spec traceability (ODF) | `governance_validators.py:validate_spec_qname_coverage` (V51) | WARN |
| Spec traceability (non-ODF) | `governance_validators.py:validate_spec_concept_tags` | WARN |
| Forbidden module names | `governance_validators.py:validate_forbidden_module_names` (V50) | FAIL |
| Spec fact refs density | `governance_validators.py:validate_spec_fact_refs_density` (V62) | REWORK_REQUIRED |
| Multi-responsibility file | `governance_validators.py:validate_multi_responsibility_file` (V66) | WARN |
| Lint (ruff check) | CI `governance-check` + `lint` jobs | FAIL (CI red) |
| Security scan | CI `security` job (bandit) | FAIL (CI red) |

---

## Reference Documents

- Implementation checklist (per-file rules): [production-library-checklist.md](production-library-checklist.md)
- Root cause analysis (governance bypass): [root-cause-analysis.md](root-cause-analysis.md)
- Gap inventory (current violations): [src-architecture-gap-inventory.md](src-architecture-gap-inventory.md)
- Validator: `tools/validators/source_structure_validator.py`
- Anti-monolith validator: `tools/validators/validate_source_architecture.py`
- Baseline: `registry/source-structure-baseline.json`
