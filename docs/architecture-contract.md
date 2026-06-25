# Format Factory Architecture Contract

## Document Authority
- **Status:** AUTHORITATIVE
- **Origin:** TC-FORENSIC-012, source-realization-forensics-20260625-001
- **Derived from:** Forensic inspection of 20 Python packages and 10 .NET projects
- **Governs:** All new format implementations and modifications to existing implementations

---

## 1. Python Package Layout Standard

Every Python format package in `src/python/{format}/` MUST contain these files:

| File | Role | Required |
|------|------|----------|
| `__init__.py` | Public API surface with dynamic `__all__` | YES |
| `spec/{concept}/` | Architecture-only spec authority classes | YES |
| `Compat/` | Format-prefixed facades wrapping spec classes | YES |
| `models.py` | Domain model class(es) for consumers | YES |
| `{format}_parser.py` or `{format}_codec.py` | Parsing logic | YES |
| `{format}_analytics.py` | Derived analytics functions | YES (if analytics exist) |

**Forbidden:** Monolithic files > 800 LOC that combine parsing + analytics + model in one file.
Governance enforcement: `GOV_BLOCK:monolith_detection_validator` fires at 800 LOC.

**One responsibility per file.** If a function neither belongs in the parser nor in analytics,
it belongs in `models.py` or a dedicated writer module.

---

## 2. Spec Authority Naming Rules

### `spec/` Directory (architecture-only)

- Files contain skeleton classes with `# GENERATED — architecture_only` marker
- Every class MUST have `spec_qname: ClassVar[str]` (not instance field `spec_qname: str`)
- Every class MUST have `spec_fact_ref: ClassVar[str]` pointing to a SAL fact ID
- Every class MUST have `authority_only: ClassVar[bool] = True`
- These classes contain NO behavioral methods — they are pure traceability markers

```python
# CORRECT pattern:
class TableCell:
    spec_qname: ClassVar[str] = "table:table-cell"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-042"
    authority_only: ClassVar[bool] = True
```

### `Compat/` Directory (facades)

- Contains format-prefixed names ONLY (e.g., `FodsCell`, `NdjsonField`, `XcfLayer`)
- Inherits from corresponding `spec/` class
- Adds `namespace_uri`, `local_name`, `facade_names` attributes
- Adds NO behavioral implementation — behavior lives in `models.py`
- Every class MUST maintain `spec_qname` ClassVar from parent

```python
# CORRECT pattern:
class FodsCell(TableCell):
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
    local_name: ClassVar[str] = "table-cell"
    facade_names: ClassVar[list] = ["FodsCell"]
```

**Forbidden:** Using format-prefixed names as primary implementation targets. `FodsCell`
is an architecture marker. The consumer-facing domain model is in `models.py`.

---

## 3. `models.py` Domain Model Rules

Every Python package MUST have `models.py` with at least one domain model class satisfying:

1. `spec_qname: ClassVar[str]` set to the primary format element's QName
2. `from_file(path) -> Self` class method as the consumer entry point
3. Typed properties exposing the parsed structure (no raw dict leakage in public API)
4. `to_dict() -> dict` for serialization
5. All public methods documented with docstrings

```python
# Reference pattern (from csv/models.py and tsv/models.py):
class CsvDocument:
    spec_qname: ClassVar[str] = "csv:record"

    @classmethod
    def from_file(cls, path: str) -> "CsvDocument": ...

    @property
    def headers(self) -> list[str]: ...

    @property
    def row_count(self) -> int: ...

    def get_cell(self, row: int, col: int | str) -> str | None: ...

    def to_dict(self) -> dict: ...
```

**Reference implementations:** `src/python/csv/models.py`, `src/python/tsv/models.py`

---

## 4. Public API Surface Rules (`__init__.py`)

Every `__init__.py` MUST use the dynamic `__all__` with exclusion frozenset pattern:

```python
import sys as _sys
import types as _types

_FF_API_EXCLUDE = frozenset({
    'Any', 'ClassVar', 'Dict', 'List', 'Optional', 'Path', 'Set', 'Tuple',
    'Union', 'dataclass', 'field', 'TYPE_CHECKING',
    # add format-specific exclusions
})

_mod = _sys.modules[__name__]
__all__ = [
    k for k in vars(_mod)
    if not k.startswith("_")
    and k not in _FF_API_EXCLUDE
    and not isinstance(getattr(_mod, k), _types.ModuleType)
]
del _sys, _types
```

**Forbidden:** Explicit 600+ line `__all__` lists. These cause maintenance debt and
expose module imports and typing artifacts in the public API.

---

## 5. Error Hierarchy Rules

Each format MUST define per-format typed exceptions in the package:

- Base error: `{Format}Error(Exception)` or `{Format}InputError(Exception)`
- Parse error: `{Format}ParseError({Format}Error)`
- Size error: `{Format}SizeError({Format}Error)` (for formats with size limits)

**Dual-mode parsing:**
- `parse_{format}(path)` — returns error dict `{"error": "...", "is_{format}": False}` on failure
- `parse_{format}_strict(path)` — raises typed exception on failure

Consumers choose between graceful degradation and exception-based error handling.

---

## 6. .NET Project Layout Standard

Every .NET format project in `src/net/{format}/` MUST follow the four-layer separation:

| Layer | File(s) | Responsibility |
|-------|---------|----------------|
| 1. Parser | `{Format}Parser.cs` | File I/O → validation → DOM. Size guard FIRST. |
| 2. Object Model | `{Format}Document.cs`, `{Format}Sheet.cs`, etc. | Typed DOM wrappers |
| 3. Serializer | `{Format}Writer.cs` | DOM → file serialization |
| 4. Exporter | `{Format}DocumentExporter.cs` | Pure static export functions |

**Security requirements (enforced at parser layer, before any XML processing):**
- `DtdProcessing = DtdProcessing.Prohibit` — prevents DTD parsing
- `XmlResolver = null` — prevents external entity resolution (XXE)
- File-size guard at parser entry point (default 50 MB for XML formats)

**Object model requirements:**
- Named C# types for all major spec concepts (no `Dictionary<string, object>` bags)
- Collections typed as `IReadOnlyList<T>` (immutable from consumer perspective)
- Factory methods only: `{Format}Document.Load(path)`, `{Format}Document.CreateNew()`
- No public constructors

---

## 7. .NET Error Hierarchy Rules

Each .NET format MUST define:

- `{Format}DocumentException : Exception` in `Exceptions/` subdirectory
- Exception messages include: actual/limit values, format context, inner exception chain
- Parser CATCHES `XmlException` and wraps with `{Format}DocumentException`
- No format-specific exceptions should inherit from generic `IOException`

---

## 8. Round-Trip Fidelity Contract

**Python:** Content-preserving round-trip.
- Known content (cells, paragraphs, metadata) preserved exactly
- Formulas and styles preserved where mapped
- Unknown/unmapped XML attributes MAY be lost in dict-based parsing

**`.NET`:** Bit-perfect round-trip via DOM.
- `XDocument` DOM preserves ALL XML including unknown nodes and attributes
- Save → reload produces structurally identical document
- Third-party FODS/FODT extensions preserved

Both platforms MUST document their round-trip fidelity level in the package README.

---

## 9. Generated vs. Maintained Boundaries

| File type | Generator | Overwrite-safe? | Human-editable? |
|-----------|-----------|-----------------|-----------------|
| `spec/{concept}/*.py` | `generate_canonical_stubs.py` | YES (status-gated) | ONLY after status > "seeded" |
| `Compat/*.py` | `generate_canonical_stubs.py` | NO after "implementing" | YES |
| `models.py` | Manual / FeatureFactory | NO | YES |
| `*_parser.py`, `*_codec.py` | Manual / FeatureFactory | NO | YES |
| `*_analytics.py` | FeatureFactory | Append-only | YES |

**Rule:** `generate_canonical_stubs.py` checks `status` field in `shared/qname-registry/*.yaml`
before writing. Files with status > "seeded" are never overwritten. This is the ONLY safe path
to add new spec skeleton classes — do NOT hand-write `spec/` classes.

---

## 10. Idempotency Requirements

- `generate_canonical_stubs.py`: IDEMPOTENT within "seeded" scope. Re-running produces identical output.
- `FeatureFactory`: NOT IDEMPOTENT (running twice duplicates functions). Caller must check
  whether the target function already exists before invoking FeatureFactory. (TC-SRFA-015)
- `build_declaration_review_package.py`: IDEMPOTENT (same declaration → same bundle SHA-256).
- Test generation (test_drivers.py templates): IDEMPOTENT (template + inputs → same output).

---

## 11. Governance Enforcement Summary

| Rule | Validator | Mode |
|------|-----------|------|
| No format-prefixed primary classes | V49 | WARN |
| spec_qname as ClassVar (not instance) | V53 | WARN (runtime: FAIL) |
| No monolith files > 800 LOC | monolith_detection_validator | BLOCK |
| No forbidden module names (`*_extra.py`, `*_misc.py`) | V50 | FAIL |
| PRODUCT_SOURCE requires gap_ledger_ref + spec_fact_refs | TC-GUARD-001 | BLOCK |
| No architecture_only stubs in RELEASE_GATE evidence | V48 | FAIL |
| Analytics skill required for analytics.py changes | V41 | WARN→FAIL |

---

## Known Intentional Deviations

1. **FODS Python is read-only:** Python FODS exposes no mutation API. This is intentional
   for the FOSS tier. .NET FODS is the full editing platform. (TC-SRFA-024 tracks the gap.)

2. **FODP Python is read-only:** No `write_fodp()` function exists. FODP presentations are
   inspected but not written from Python.

3. **ZST Python is metadata-only:** ZstDocument reads frame metadata but does not decompress.
   Decompression is a caller responsibility (use the `zstandard` library directly).

4. **SYLK flat model:** SylkDocument has `.rows` (int) and `.cells` (flat list) — NOT `.sheets`.
   Mutation is file-based (`set_cell_value(src, dest, row, col, value)`), not object-based.
