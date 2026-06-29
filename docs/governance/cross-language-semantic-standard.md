# Cross-Language Semantic Standard — Format Factory

**Authority:** This document defines the semantic alignment contract between Python and .NET
implementations of the same format.

**Scope:** Commercial formats with both Python and .NET implementations.

**Effective:** 2026-06-24

**Cross-references:**
- `docs/code-quality/production-readiness-standard.md` — root code-quality contract
- `registry/gate11-criteria.yaml` — Gate 11 thresholds
- `plans/strategic/spec-to-feature-radical-correction-plan.md` — criteria C1-C20 (.NET), P1-P11 (Python)

---

## 1. Covered Formats

| Format | Python Package | .NET Project | Gate 11 Eligible |
|--------|---------------|--------------|------------------|
| FODS | `src/python/fods/` | `src/net/fods/` | Yes |
| FODT | `src/python/fodt/` | `src/net/fodt/` | Yes |
| CSV | `src/python/csv/` | `src/net/csv/` | Yes |
| TSV | `src/python/tsv/` | `src/net/tsv/` | Yes |
| NDJSON | `src/python/ndjson/` | `src/net/ndjson/` | Yes |
| ZST | `src/python/zst/` | `src/net/zst/` | Yes |

Formats with Python-only implementations (ABW, DIF, FODG, FODP, GNUMERIC, ODS, ODT,
PBM, PGM, PPM, QOI, SYLK, TOML, XCF) are not subject to cross-language parity rules.
.NET-only formats (HTML, Markdown, Txt) are likewise exempt.

---

## 2. Type Mapping: .NET to Python

For each commercial format, the following table defines the canonical type equivalences.
Language-idiomatic differences are expected; semantic divergence is not.

### 2.1 Core Types

| .NET Type | Python Equivalent | Notes |
|-----------|------------------|-------|
| `string` | `str` | Direct equivalence |
| `int` | `int` | Python int is unbounded; .NET uses Int32/Int64 |
| `double` | `float` | IEEE 754 in both languages |
| `decimal` | `decimal.Decimal` | Use when exact precision is required |
| `bool` | `bool` | Direct equivalence |
| `byte[]` | `bytes` | Direct equivalence |
| `DateTime` | `datetime.datetime` | Timezone handling may differ |
| `TimeSpan` | `datetime.timedelta` | Direct equivalence |
| `List<T>` | `list[T]` | Direct equivalence |
| `Dictionary<K,V>` | `dict[K,V]` | Direct equivalence |
| `T?` (nullable) | `T | None` | .NET nullable reference vs Python Optional |
| `IReadOnlyList<T>` | `tuple[T, ...]` or `Sequence[T]` | Immutable collection |

### 2.2 Format-Specific Type Mapping

| Format | .NET Root Type | Python Root Type | Structural Note |
|--------|---------------|-----------------|-----------------|
| FODS | `FodsDocument` (typed object) | `dict` (model dict) | Python returns dict with typed accessors |
| FODT | `FodtDocument` (typed object) | `dict` (model dict) | Same pattern as FODS |
| CSV | `CsvDocument` (typed object) | `dict` (model dict) | Python `rows` is `list[list[str]]` |
| TSV | `TsvDocument` (typed object) | `dict` (model dict) | Same structure as CSV |
| NDJSON | `NdjsonDocument` (typed object) | `list[dict]` | Python returns list of record dicts |
| ZST | `ZstDocument` (typed object) | `dict` (model dict) | Python wraps decompressed content |

### 2.3 Collection Semantics

| .NET Pattern | Python Pattern | Semantic Contract |
|-------------|---------------|-------------------|
| `doc.Sheets` (IReadOnlyList) | `model["sheets"]` (list) | Ordered, zero-indexed |
| `doc.Sheets[0].Rows` | `model["sheets"][0]["rows"]` | Nested access |
| `doc.Sheets[0].Rows[0].Cells` | row as `list` | Cell-level access |
| `doc.Metadata` (Dictionary) | `model["metadata"]` (dict) | Key-value pairs |

---

## 3. Semantic Equivalence Rules

### 3.1 Capability Parity

For each format, the same core capabilities must exist in both languages:

| Capability | Python API Pattern | .NET API Pattern |
|-----------|-------------------|-----------------|
| Load | `parse_{format}(path) -> model` | `{Format}Parser.Parse(path) -> {Format}Document` |
| Save | `write_{format}(model, path)` | `{Format}Writer.Write(doc, path)` |
| Inspect | `model['field']` or `model.field` | `doc.Property` |
| Mutate | `set_cell_value(model, ...)` | `doc.Cell.Value = x` |
| Round-trip | load -> mutate -> save -> reload | Parse -> mutate -> Write -> Parse |
| Export | `export_{format}_to_{target}(...)` | `{Format}{Target}Exporter.Export(...)` |

### 3.2 Intentional API Differences (Allowed)

These differences are by design and do not violate parity:

| Aspect | Python Convention | .NET Convention | Reason |
|--------|------------------|----------------|--------|
| Return type | `dict` model | Typed `{Format}Document` | Language idiom |
| Naming | `snake_case` | `PascalCase` | Language convention |
| Visibility | `__all__` in `__init__.py` | Namespace-based | Packaging model |
| Analytics | `{format}_analytics.py` functions | No equivalent | Analytics are FOSS Python-only |
| Async | Not provided (sync-only) | `ParseAsync()`, `WriteAsync()` | .NET async/await pattern |
| Exceptions | `{Format}Error(FormatFactoryError)` | `{Format}DocumentException(Exception)` | Hierarchy roots differ |
| Null handling | `None` / `KeyError` | Nullable reference types | Language design |

### 3.3 Prohibited Divergences

The following divergences are structural violations and must be resolved:

- A capability present in .NET must have a Python equivalent (and vice versa) for
  commercial formats.
- Round-trip preservation behavior must be semantically equivalent: if .NET preserves
  a field through round-trip, Python must also preserve it.
- Parse output must represent the same logical structure (same fields, same nesting).
- Error conditions must trigger equivalent exceptions (not silently swallowed in one
  language while thrown in the other).

---

## 4. QName Registry as Truth Source

The shared QName registry at `shared/qname-registry/` defines the canonical concept mapping:

- Each QName entry maps to both `python_file` and `dotnet_file`.
- If one is `null`, the concept lacks cross-language coverage.
- `status` tracks maturity: `seeded` -> `architecture_only` -> `implementing` ->
  `implemented` -> `stable`.
- Both implementations of the same QName must use the same `spec_qname` string value.

---

## 5. Shared Test Vectors

### 5.1 Fixture Files

Shared test fixture files live in `samples/by-format/{format}/` and are used by both
Python and .NET test suites. These files are the canonical test inputs.

| Format | Fixture Location | Example Files |
|--------|-----------------|---------------|
| FODS | `samples/by-format/fods/` | `sample.fods`, `multi-sheet.fods` |
| FODT | `samples/by-format/fodt/` | `sample.fodt`, `styled.fodt` |
| CSV | `samples/by-format/csv/` | `simple.csv`, `quoted.csv` |
| TSV | `samples/by-format/tsv/` | `simple.tsv`, `multi-col.tsv` |
| NDJSON | `samples/by-format/ndjson/` | `records.ndjson`, `nested.ndjson` |
| ZST | `samples/by-format/zst/` | `compressed.zst` |

### 5.2 Test Vector Contract

For each shared fixture, both language implementations must produce:

1. **Same field count** — number of fields/columns/keys must match.
2. **Same row/record count** — number of data rows or records must match.
3. **Same string values** — text content must be byte-identical (after encoding
   normalization to UTF-8).
4. **Same numeric values** — within IEEE 754 tolerance (`1e-10` relative error).
5. **Same structural depth** — nesting levels must match.

### 5.3 Cross-Language Test Pattern

```python
# Python test
def test_csv_shared_fixture():
    model = parse_csv("samples/by-format/csv/simple.csv")
    assert model["row_count"] == 3
    assert model["headers"] == ["name", "age", "city"]
```

```csharp
// .NET test
[Fact]
public void Parse_SharedFixture_MatchesPythonOutput()
{
    var doc = CsvParser.Parse("samples/by-format/csv/simple.csv");
    Assert.Equal(3, doc.RowCount);
    Assert.Equal(new[] { "name", "age", "city" }, doc.Headers);
}
```

Both tests use the same fixture file and assert equivalent structural properties.

---

## 6. Parity Verification Process

### 6.1 Automated Checks

Cross-language parity is tracked through:

1. **QName registry completeness** — both `python_file` and `dotnet_file` must be
   non-null for each concept in commercial formats.
2. **Capability matrices** in `reports/capability-layer/` — list operations available
   per language per format.
3. **Shared fixture results** — test output compared across languages.

### 6.2 Manual Review Triggers

Parity review is required when:

- A new public API is added to either language implementation.
- A model field is renamed or restructured in either language.
- Round-trip behavior changes in either language.
- A new format is added to the commercial track.

### 6.3 Parity Status Tracking

Cross-language parity status is tracked per format in `registry/format-registry.yaml`
under the `cross_language_parity` field:

| Value | Meaning |
|-------|---------|
| `full` | All core capabilities present and tested in both languages |
| `partial` | Some capabilities missing or untested in one language |
| `python_only` | No .NET implementation exists |
| `dotnet_only` | No Python implementation exists |

---

## 7. Gate 11 Parity Requirements

Gate 11 (commercial release) requires Babar Raza's approval. Parity criteria include:

- All core capabilities (load, save, inspect, round-trip) present in both languages.
- Round-trip preservation verified with shared fixtures.
- Shared fixtures produce equivalent outputs (per Section 5.2 contract).
- No unintentional API divergence documented.
- QName registry entries have both `python_file` and `dotnet_file` populated.
- Criteria C1-C20 (.NET) and P1-P11 (Python) from
  `plans/strategic/spec-to-feature-radical-correction-plan.md` are satisfied.

---

## 8. Exception Parity

### 8.1 Exception Mapping

| Scenario | Python Exception | .NET Exception |
|----------|-----------------|---------------|
| File not found | `FileNotFoundError` | `FileNotFoundException` |
| Malformed input | `{Format}ParseError` | `{Format}DocumentException` |
| Write failure | `{Format}WriteError` | `{Format}DocumentException` |
| Invalid argument | `ValueError` | `ArgumentException` |
| Null/None input | `TypeError` | `ArgumentNullException` |

### 8.2 Error Behavior Contract

- Both implementations must raise on the same input conditions.
- Neither implementation may silently swallow errors that the other raises.
- Error messages need not be identical but must convey the same failure reason.

---

**Cross-references:**
- Gate 11 criteria: `registry/gate11-criteria.yaml`
- QName registry: `shared/qname-registry/`
- Production readiness: `docs/code-quality/production-readiness-standard.md`
- Python library standard: `docs/governance/python-library-standard.md`
- .NET library standard: `docs/governance/dotnet-library-standard.md`
