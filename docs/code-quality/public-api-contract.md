# Public API Governance Contract

**Mission:** PQLM-001 | **Taskcard:** TC-PQLM-010 | **Generated:** 2026-07-03 | **Version:** 1.0

This document defines authority requirements for every public API in Format Factory product libraries.
Validators V90–V94 enforce mechanical checks. The code-writing skill forbidden_patterns enforce
pre-implementation rejection.

---

## 1. Authority Requirement

Every public API (class, method, property, function) requires:

| Authority Field | Requirement |
|---|---|
| Specification authority | An ODF QName (`table:table-cell`) or spec fact reference (`FACT-FODS-001`) OR explicit "derived analytics" label |
| Capability ID | One or more capability IDs from `.governance/capabilities/registry.yaml` |
| Owning type | The correct domain type (NOT root document if it is a cell/row/column property) |
| Persistence behavior | Documented: does this survive `Save()` + `Load()`? |

**An API may NOT be created because:**
- A test file references it
- Compilation requires a method body
- Another language already exposes it
- A requirement ID (R-NNN) references it
- It increases a capability count or test count

---

## 2. Setter / Getter Requirements

### 2.1 Getter Requirements

Every public getter that claims to read a persistent document property MUST:
1. Read from the parsed XML/XDocument/XElement, NOT from a private field or dictionary
2. Have a test that verifies the getter reads correct data from a REAL file input
3. Have a documented fallback behavior (returns null, returns default, raises) when attribute is absent from XML

**FAIL pattern:**
```csharp
// PROHIBITED — getter reads private dict, not XML
public string? GetSheetProtection(string sheetName) =>
    _sheetProtection.TryGetValue(sheetName, out var p) ? p : null;
```

**PASS pattern:**
```csharp
// CORRECT — getter reads from ODF XML
public string? GetSheetProtection(string sheetName)
{
    var table = GetSheetElement(sheetName);
    return table?.Element(FodsNamespaces.Table + "table-source")
                 ?.Attribute(FodsNamespaces.Table + "protect")?.Value;
}
```

### 2.2 Setter Requirements

Every public setter that claims to persist a document property MUST:
1. Write to the XML/XDocument/XElement directly via `SetAttributeValue()` or equivalent
2. Have a Type 4 roundtrip test: `Set(v) → Save() → Load() → Assert.Equal(v, Get())`
3. Be connected to the writer path (the writer serializes the XDocument which contains the mutation)

**FAIL pattern:**
```csharp
// PROHIBITED — setter writes to dict with no XML path
public void SetSheetProtection(string sheetName, string? password)
    => _sheetProtection[sheetName] = password;
```

**PASS pattern:**
```csharp
// CORRECT — setter writes to ODF XML
public void SetSheetProtection(string sheetName, string? password)
{
    var table = GetOrCreateSheetElement(sheetName);
    var source = table.GetOrCreateElement(FodsNamespaces.Table + "table-source");
    if (password is null)
        source.Attribute(FodsNamespaces.Table + "protect")?.Remove();
    else
        source.SetAttributeValue(FodsNamespaces.Table + "protect", password);
}
```

---

## 3. Domain Ownership Rules

### 3.1 Root Document Must Not Own Nested-Domain Behavior

The root document type (`FodsDocument`) must NOT own methods for nested domain concepts.

**PROHIBITED on FodsDocument:**
```csharp
// Cell-level behavior does not belong on root document
public string? GetCellFont(string sheetName, int row, int col) { ... }
public void SetCellBackground(string sheetName, int row, int col, string color) { ... }
```

**CORRECT — nested behavior belongs on the nested type:**
```csharp
// On FodsCell:
public FodsStyle? ResolveStyle() { ... }
// On FodsSheet:
public bool IsProtected { get; private set; }
```

### 3.2 Export Operations Do Not Belong in Domain Types

HTML/CSV/Markdown export operations must NOT be on domain types.
Use `FodsExporter` (or equivalent `*Exporter` class) for all export concerns.

---

## 4. Typed Values for Closed Vocabularies

Closed vocabularies MUST be typed, not stringly typed.

**PROHIBITED:**
```csharp
public string CellValueType { get; }  // "string", "float", "boolean" — no type safety
```

**REQUIRED:**
```csharp
public enum CellValueType { String, Float, Boolean, Date, Time, Currency, Percentage, Void }
public CellValueType ValueType { get; }
```

Python equivalent:
```python
class CellValueType(str, Enum):
    STRING = "string"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    TIME = "time"
    VOID = "void"
```

---

## 5. Analytics Separation Rule

Analytics functions (pure read-only computations over a parsed model) MUST be:
- In a separate `*_analytics.py` file (Python)
- Not on any domain type (Python or .NET)
- NOT exported from the package root by default (opt-in import)
- NOT on the domain model class (returning computed aggregates from class methods
  with no ODF spec backing is analytics, not domain behavior)

---

## 6. No Fabricated Defaults

Public methods MUST NOT return fabricated defaults that claim to represent document state.

**PROHIBITED:**
```csharp
// Returns 0 regardless of document content — fabricated default
public int GetColumnCount(string sheetName) => 0;
```

**PROHIBITED:**
```python
# Always returns empty list — fabricated success
def get_sheet_filters(self) -> list:
    return []
```

**Resolution:** Either implement the XML read path, or raise `NotSupportedOdfFeatureException`
with the ODF QName and a reference to the gap ledger entry.

---

## 7. Validator Coverage

| Validator | What It Checks |
|---|---|
| V90 | Public methods that always return a literal constant (0, false, null, "", []) |
| V91 | Public getters with no XML/parser backing (reads only from private field or dict) |
| V92 | Public setters with no XML write path (writes only to private field or dict) |
| V93 | Public APIs referenced only in test files (no production consumer) |
| V94 | Private `Dictionary<string, X?>` fields used as persistent state backing |

---

## 8. Enforcement Points

- `add-dotnet-api.md` MANDATORY PRE-CHECK ZERO: work-shape rejection
- `add-python-api.md` MANDATORY PRE-CHECK ZERO: analytics masquerade rejection
- Pre-commit hook: V90-V94
- Sprint closeout: V90-V94
- Certification requirement: all persistent features must have roundtrip test
