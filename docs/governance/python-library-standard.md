# Python Library Standard — Format Factory

**Authority:** Binding code-quality contract for all Python source under `src/python/`.
Supplements `docs/code-quality/production-readiness-standard.md` (the root authority).
Automated validators enforce these rules.

**Effective:** 2026-06-24
**Enforced by:**
- `tools/validators/validate_source_architecture.py`
- `tools/validators/source_structure_validator.py`
- `tools/supervisor/governance_validators.py` (V35, V42, V44, V48)

**Companion documents:**
- `docs/code-quality/production-readiness-standard.md` — root architecture contract
- `plans/healing/product-code-healing-plan.md` — decomposition tracker and priority queue
- `plans/strategic/spec-to-feature-radical-correction-plan.md` — canonical naming and spec parity

---

## 1. Target Architecture

Every format is a self-contained Python package under `src/python/{format}/`.
The canonical layout:

```
src/python/{format}/
  __init__.py                 # Re-exports only. No logic. Hard cap: 100 LOC.
  {format}_parser.py          # Parse raw bytes/text into domain model.
      OR parser.py            #   Max 800 LOC. Required.
      OR {format}_codec.py    #   (legacy name; new packages use parser.py)
  models.py                   # Domain entity classes. Max 800 LOC. Required.
      OR neutral_model.py     #   (alternative name)
      OR {format}_model.py
  {format}_analytics.py       # Analytics/statistics functions. Max 800 LOC per file.
      OR analytics/           #   If analytics exceeds 800 LOC, split by category:
        __init__.py            #     Re-exports from sub-modules
        _analytics_file.py     #     File-level stats (size, count)
        _analytics_structure.py #    Structural metrics (depth, nesting)
        _analytics_compound.py  #    Multi-field combinations
        _analytics_scale.py     #    Size/dimension analytics
  writer.py                   # Domain model to format output. Max 800 LOC. Optional.
      OR {format}_writer.py
  exceptions.py               # Format-specific exceptions. Max 50 LOC. Required.
  constants.py                # Namespace URIs, magic bytes, limits. Max 200 LOC. Optional.
  py.typed                    # PEP 561 marker. Required. Empty file.
  Compat/                     # Facade classes for backward-compatible names. Optional.
    __init__.py
    {format}_{entity}.py      # e.g. FodsCell, XcfLayer — architecture markers only
  spec/                       # Canonical spec class hierarchy. Optional.
    {entity}.py               # May be architecture_only stubs with TODO markers
```

**Package rule:** Each `src/python/{format}/` directory must be importable as a
standalone package. No cross-format imports except through `src/python/_shared/`.

---

## 2. Module Separation Rules

### 2.1 Parser / Codec

**File:** `{format}_parser.py`, `parser.py`, or `{format}_codec.py`

Responsibilities:
- Read raw bytes or text from a file path or stream
- Validate format structure (magic bytes, headers, required sections)
- Build and return the domain model
- Raise format-specific parse exceptions on invalid input

Prohibitions:
- No analytics or statistics computation
- No write/serialization logic
- No direct print/logging to stdout (use `logging` module)

Max: 800 LOC, 60 functions (new files). Existing violations frozen at
`baseline_loc_cap` in `registry/source-structure-baseline.json`.

### 2.2 Model

**File:** `models.py`, `neutral_model.py`, or `{format}_model.py`

Responsibilities:
- Define domain entity classes (Document, Sheet, Cell, Layer, Record, etc.)
- Carry `spec_qname` attribute for ODF-derived formats (FODS, FODT, FODG, FODP, ODS, ODT)
- Provide attribute access to parsed data
- Remain format-neutral where possible (no I/O, no file handles)

ODF spec parity requirement:
```python
class TableCell:
    spec_qname = "table:table-cell"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
```

Non-ODF formats use descriptive `spec_qname` values (e.g., `"xcf:layer"`,
`"ndjson:field"`).

Max: 800 LOC, 60 functions.

### 2.3 Analytics

**File:** `{format}_analytics.py` or `analytics/` sub-package

Responsibilities:
- All statistics, metrics, and computed properties
- Pure functions: input is the domain model (or file path), output is a value
- No mutation of the domain model
- No side effects (no file writes, no network calls)

Function naming convention:
```python
def {format}_{metric_name}(model_or_path, ...):
    """Return {metric} for the given {format} document."""
```

Examples: `fods_row_count(model)`, `xcf_layer_count(model)`, `ndjson_record_count(records)`.

Re-export pattern (at the bottom of the parser/codec file):
```python
try:
    from .{format}_analytics import *
except ImportError:
    pass
```

This ensures analytics functions are accessible from the parser module without
requiring changes to `__init__.py`. The `ImportError` guard allows the package to
function without the analytics module installed.

**Splitting large analytics files:**
When a single analytics file exceeds 800 LOC, split by category:

| Sub-module | Content |
|------------|---------|
| `_analytics_file.py` | File-level stats (size, byte count, encoding) |
| `_analytics_structure.py` | Structural metrics (depth, nesting, counts) |
| `_analytics_compound.py` | Multi-field combinations, cross-entity stats |
| `_analytics_scale.py` | Size/dimension analytics, range calculations |

The parent `{format}_analytics.py` then becomes a re-export hub:
```python
from ._analytics_file import *
from ._analytics_structure import *
from ._analytics_compound import *
from ._analytics_scale import *
```

**V42 enforcement:** Analytics functions without spec backing are rejected by
`validate_deepening_suspension()` (governance validator V42). Every analytics
function must trace to a GAP-* entry in `reports/capability-layer/gap-ledger.json`
or a spec fact (FACT-{FORMAT}-*).

Max per file: 800 LOC, 60 functions.

### 2.4 Exceptions

**File:** `exceptions.py`

Every format package must define its own exception hierarchy inheriting from the
shared base:

```python
from src.python._shared.exceptions import FormatFactoryError, ParseError, WriteError

class FodsError(FormatFactoryError):
    """Base exception for FODS format operations."""

class FodsParseError(ParseError):
    """Raised when FODS parsing fails."""

class FodsWriteError(WriteError):
    """Raised when FODS writing fails."""
```

Hard cap: 50 LOC. Exception files must contain only class definitions and
docstrings. No logic, no utility functions.

### 2.5 Constants

**File:** `constants.py`

Content:
- Namespace URIs for ODF formats
- Magic byte sequences for binary formats
- Format version strings
- Structural limits (max rows, max columns, max layers)

```python
# Example: FODS constants
FODS_NAMESPACE_TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
FODS_NAMESPACE_OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
FODS_MAX_COLUMNS = 1024
```

Max: 200 LOC.

### 2.6 Writer

**File:** `writer.py` or `{format}_writer.py`

Responsibilities:
- Accept a domain model and serialize to the target format
- Validate model completeness before writing
- Raise `WriteError` on serialization failures

Prohibitions:
- No parsing logic
- No analytics computation

Max: 800 LOC, 60 functions.

### 2.7 `__init__.py`

**File:** `__init__.py`

Rules:
- Re-exports only. No business logic.
- Must expose the public API surface of the package.
- Hard cap: 100 LOC.

For small packages (fewer than 30 exports), explicit `__all__` is acceptable:
```python
from .fods_parser import load_fods, save_fods
from .models import FodsDocument, FodsSheet, FodsCell

__all__ = ["load_fods", "save_fods", "FodsDocument", "FodsSheet", "FodsCell"]
```

For large packages (30+ exports), use the dynamic pattern:
```python
from .{format}_parser import *
from .models import *

import sys as _sys
__all__ = [k for k in vars(_sys.modules[__name__]) if not k.startswith("_")]
del _sys
```

This avoids maintaining a manual list of 100+ export names.

---

## 3. Compat/ Facade Layer

**Directory:** `{format}/Compat/`

Purpose: Provide backward-compatible, format-prefixed class names that wrap the
canonical spec-derived classes.

Rules:
- Facades inherit from the canonical class in `spec/` or `models.py`
- Facades add NO behavioral implementation — they are architecture markers only
- Facades set `spec_qname`, `spec_fact_ref`, and `namespace_uri` attributes
- Real behavior lives in the model or parser, never in Compat/

Example:
```python
# src/python/fods/Compat/fods_cell.py
from ..spec.table.table_cell import TableCell

class FodsCell(TableCell):
    spec_qname = "table:table-cell"
    spec_fact_ref = "FACT-FODS-TABLE-CELL"
    namespace_uri = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
```

Governance: V48 (`validate_architecture_only_stub_gate`) blocks RELEASE_GATE items
from citing Compat/ facades or architecture_only stubs as implementation evidence.

---

## 4. spec/ Canonical Hierarchy

**Directory:** `{format}/spec/`

Purpose: Mirror the format specification's element hierarchy as Python classes.

Rules:
- File names match the spec element local name (e.g., `table_cell.py` for
  `table:table-cell`)
- Classes carry `spec_qname` matching the spec element QName
- May be `architecture_only` stubs generated by `tools/spec/generate_canonical_stubs.py`
- Stubs contain `# GENERATED -- architecture_only` markers and `# TODO: implement`
- Stubs are NOT behavioral implementations and must NOT be cited as product evidence

Status lifecycle for spec classes: `seeded` -> `architecture_only` -> `implementing`
-> `implemented` -> `stable`. Tracked in `shared/qname-registry/{format}.yaml`.

---

## 5. LOC and Function Caps

### 5.1 New Files

| Metric | Hard Limit |
|--------|-----------|
| Lines of code | 800 |
| Function definitions | 60 |

Enforced by `tools/validators/source_structure_validator.py` on every sprint.

### 5.2 Existing Violations

Files exceeding limits are tracked in `registry/source-structure-baseline.json`
under `known_violations`:

```json
{
  "src/python/zst/zst_analytics.py": {
    "loc": 5513,
    "baseline_loc_cap": 5543,
    "functions": 287,
    "baseline_functions_cap": 287,
    "category": "analytics_extraction_secondary"
  }
}
```

Rules:
- `baseline_loc_cap` is **write-once** — it may only decrease, never increase
- `loc` is updated to reflect the current actual line count
- Adding lines beyond `baseline_loc_cap` triggers GOV_BLOCK
- The only path forward for capped files is decomposition (splitting)

### 5.3 LOC Measurement Method

Always measure LOC using V35's exact method:
```python
loc = sum(1 for _ in Path(filepath).open(encoding='utf-8', errors='replace'))
```

Do not use `wc -l`, `len(text.splitlines())`, or other methods. They produce
different counts. Consistency with the validator is mandatory.

---

## 6. PEP 561 Compliance

Every package must contain a `py.typed` marker file:

```
src/python/{format}/py.typed
```

This is an empty file. Its presence signals to type checkers (mypy, pyright) that
the package supports inline type annotations.

---

## 7. Import and Dependency Rules

### 7.1 Internal Imports

- Use relative imports within a format package:
  ```python
  from .models import FodsDocument
  from .exceptions import FodsParseError
  ```
- Use absolute imports for shared infrastructure:
  ```python
  from src.python._shared.exceptions import FormatFactoryError
  ```

### 7.2 Cross-Format Imports

Cross-format imports are prohibited. Format packages must not import from each
other. Shared logic belongs in `src/python/_shared/`.

### 7.3 External Dependencies

- Standard library only for core parser/model/writer modules
- Third-party dependencies (lxml, PIL) must be optional and guarded:
  ```python
  try:
      from lxml import etree
  except ImportError:
      etree = None  # Graceful degradation
  ```

### 7.4 CSV Import Conflict

Python's built-in `csv` module conflicts with `src/python/csv/`. When importing
the format package, use path manipulation:
```python
import sys
_REPO = Path(__file__).resolve().parents[3]  # adjust depth as needed
sys.path.insert(0, str(_REPO))
from src.python.csv.csv_parser import load_csv
```

---

## 8. Testing Requirements

### 8.1 Test Location

Tests live under `tests/python/{format}/`. Mirror the source structure:

```
tests/python/{format}/
  test_{format}_parser.py
  test_{format}_model.py
  test_{format}_analytics.py
  test_{format}_writer.py
  test_{format}_exceptions.py
```

### 8.2 Test Runner

Always use the project venv:
```bash
.venv/Scripts/pytest tests/python/{format}/ -v
```

Never use `python -m pytest` (system Python lacks pytest).

### 8.3 Test Quality

- V36 enforcement: tests with >80% weak assertions (e.g., only `assert x.spec_qname == ...`)
  receive WARN status
- Tests must exercise actual behavior, not just attribute existence
- Analytics tests must verify computed values against known inputs

### 8.4 Decomposition Sprints

When splitting a file during decomposition:
1. Run full format test suite BEFORE the split
2. Perform the split (move functions, update imports, add re-exports)
3. Run full format test suite AFTER the split — zero failures required
4. Update `baseline_loc_cap` DOWNWARD in baseline JSON
5. Verify backward-compatible re-exports remain accessible

---

## 9. Packaging and Distribution

### 9.1 Wheel Build

Build wheels using the project build script:
```bash
python packaging/python/build-local-packages.py
```

Output location: `.local/package-builds/python-foss/`

### 9.2 Install Verification

On Windows, install with the `--user` flag:
```bash
pip install --user .local/package-builds/python-foss/{format}-*.whl
```

### 9.3 Consumer Proof Protocol

Every packaged format must pass the consumer proof sequence:

```python
# 1. Import
from format_factory.{format} import load_{format}

# 2. Load
model = load_{format}("sample.{ext}")

# 3. Inspect
assert model is not None
assert hasattr(model, 'expected_attribute')

# 4. Save (if writer exists)
from format_factory.{format} import save_{format}
save_{format}(model, "output.{ext}")

# 5. Reload
model2 = load_{format}("output.{ext}")
assert model2 is not None
```

### 9.4 Package Matrix

Registered formats are tracked in `packaging/python/package-matrix.yaml`.
A format must be added to this matrix before wheel builds include it.

---

## 10. Governance Validators

The following validators enforce this standard automatically:

| ID | Validator | What It Checks |
|----|-----------|---------------|
| V35 | `validate_source_structure` | LOC and function count against baseline caps |
| V36 | `validate_no_stub_tests` | Weak assertion ratio in tests |
| V42 | `validate_deepening_suspension` | Blocks analytics without spec backing |
| V44 | `validate_import_hygiene` | Verifies imports are functional (not stubs) |
| V48 | `validate_architecture_only_stub_gate` | Blocks release evidence citing stubs |

Validator source: `tools/supervisor/governance_validators.py`

When a validator fires GOV_BLOCK, the next sprint must resolve the violation before
product deepening can resume. This is enforced by `check_continuation.py` returning
STOP with `reason: structural_govblock_must_be_resolved_first`.

---

## 11. Anti-Patterns

The following patterns are prohibited and will be flagged by governance:

1. **Monolith parser** — All logic in a single file. Split into parser + model +
   analytics + exceptions.

2. **Analytics in parser** — Statistics functions mixed with parsing logic. Extract
   to `{format}_analytics.py`.

3. **Format-prefixed primary classes** — Using `FodsCell` as the implementation
   class. The primary class must be canonical (`TableCell`); `FodsCell` is a
   Compat/ facade only.

4. **Skeleton-as-progress** — Claiming product progress for architecture_only
   stubs that contain no behavioral implementation.

5. **Upward cap adjustment** — Increasing `baseline_loc_cap` to accommodate
   growth. The cap is write-once and may only decrease.

6. **Cross-format coupling** — Importing from one format package into another.
   Use `_shared/` for common logic.

7. **Unsourced analytics** — Adding analytics functions without a GAP-* ledger
   entry or spec fact reference. V42 blocks these.

8. **Manual __all__ bloat** — Maintaining a 500+ line `__all__` list in
   `__init__.py`. Use the dynamic `__all__` pattern for large packages.

---

## 12. Quick Reference Checklist

For each format package, verify:

- [ ] Package directory exists at `src/python/{format}/`
- [ ] `__init__.py` present, re-exports only, under 100 LOC
- [ ] `exceptions.py` present, inherits from `FormatFactoryError`, under 50 LOC
- [ ] Parser/codec file present, under 800 LOC
- [ ] Model file present (if format has structured data), under 800 LOC
- [ ] Analytics file present (if format has analytics), under 800 LOC per file
- [ ] `py.typed` marker file present
- [ ] No cross-format imports
- [ ] All public functions re-exported through `__init__.py`
- [ ] Tests exist at `tests/python/{format}/`
- [ ] Baseline entry in `registry/source-structure-baseline.json` (if in known_violations)
- [ ] QName registry entry in `shared/qname-registry/{format}.yaml`
- [ ] Package matrix entry in `packaging/python/package-matrix.yaml` (if distributable)

---

*End of standard. For .NET library rules, see Section 1.2 of
`docs/code-quality/production-readiness-standard.md`.*
