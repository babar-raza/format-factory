# Comment, Documentation, Tags, and Markers Contract

**Mission:** PQLM-001 | **Taskcard:** TC-PQLM-009 | **Generated:** 2026-07-03 | **Version:** 1.0

This document defines the authoritative policy for all comments, docstrings, XML doc comments,
TODO/FIXME/HACK markers, and code-history residue in Format Factory product source files.

Validators V87–V89 enforce this contract mechanically.

---

## 1. Python: Docstring Policy

### 1.1 Public API Docstrings (REQUIRED)

Every `def` that is exported from the package (`__all__` or default public) MUST have a docstring.

**Required docstring content:**
- One-line summary of **intent** (what the caller gets, not how it works)
- `Args:` block if the function takes parameters
- `Returns:` block if the function returns a value
- `Raises:` block if the function raises exceptions
- **Spec reference** for any ODF-backed property: `ODF 1.3 §9.3.2` or `spec_qname: table:table-cell`

**Prohibited docstring content:**
- Sprint/wave/train/requirement identifiers: "R290", "Wave 1", "Train B", "GI-FODS-NET-001 Phase 3"
- Implementation history: "Added in sprint 5", "Previously returned None"
- Stale behavioral claims: "Returns None when not set" (if behavior has changed)
- "Production-grade stub" or "placeholder" or "to be implemented"
- Commented-out code inside docstrings

**Example (GOOD):**
```python
def parse_fods(path: str | Path) -> FodsDocument:
    """Parse a Flat ODF Spreadsheet file and return the document model.

    Args:
        path: Path to the .fods file. Must be a valid ODF 1.3 document.

    Returns:
        FodsDocument with sheets, cells, and metadata populated from XML.

    Raises:
        FodsParseError: If the file is not a valid FODS document.

    ODF ref: office:document (ODF 1.3 §3.1)
    """
```

**Example (BAD — prohibited):**
```python
def parse_fods(path):
    """Parse FODS. Added in Sprint R290 Wave 1 per GI-FODS-NET-001.
    Previously returned None for missing sheets (fixed in R304).
    Production-grade stub pending full implementation."""
```

### 1.2 Module-Level Docstrings

Every product module MUST have a module docstring.
- First line: module purpose (e.g., "FODS parser: converts ODF flat spreadsheet XML to FodsDocument")
- Must NOT say "analytics" if the file is a domain model
- Must NOT say "domain model" if the file is an analytics file
- Must NOT contain sprint/wave/requirement IDs

### 1.3 `__all__` Declaration (REQUIRED in all `__init__.py`)

Every package `__init__.py` MUST declare `__all__` as an explicit list.

```python
__all__ = [
    "FodsDocument",
    "FodsSheet",
    "FodsRow",
    "FodsCell",
    "FodsMetadata",
    "parse_fods",
    "write_fods",
    "FodsParseError",
    "FodsWriteError",
]
```

**Prohibited:** `from .X import *` anywhere in product source.
**Prohibited:** `__all__` defined as a dynamic comprehension over all names in the module.

### 1.4 TODO / FIXME / HACK Markers

All TODO/FIXME/HACK markers MUST:
1. Reference a governed gap ID: `# TODO(GAP-PCG-007): implement XML write path for sheet protection`
2. OR reference a governed taskcard: `# TODO(TC-PQLM-015): replace detached state with XML backing`
3. Have an expiration sprint or gap closure condition

**Prohibited formats:**
```python
# TODO: implement this later
# FIXME: broken since Sprint 5
# HACK: workaround for GI-FODS-NET-001 Phase 3
# TODO(R290): add sheet protection
```

**Permitted format:**
```python
# TODO(GAP-PCG-007): SetSheetProtection — implement ODF XML write path
#   Spec: ODF 1.3 §9.1.6 table:table-source/@table:protect
#   Resolution: TC-PQLM-015 FODS rebuild sprint
```

### 1.5 Commented-Out Code (PROHIBITED)

Blocks of commented-out Python code are prohibited in product source.
- If code should be removed: delete it
- If code is temporarily disabled: open a gap entry and add a governing TODO marker

---

## 2. .NET: XML Doc Comment Policy

### 2.1 Required XML Docs (ALL PUBLIC TYPES AND MEMBERS)

Every `public` class, interface, method, and property MUST have an XML doc comment.
The `<GenerateDocumentationFile>true</GenerateDocumentationFile>` project setting is required
and enforced by the build.

**Required elements:**
- `<summary>`: describes intent, NOT implementation history; SHOULD cite ODF QName
- `<param>` for every method parameter
- `<returns>` for non-void methods
- `<exception cref="X">` when the method throws a declared exception

**`<summary>` MUST include:**
- What the member does from the caller's perspective
- ODF spec reference for ODF-backed members: `/// ODF 1.3 §9.3.2 — table:table-cell/@office:value`

**`<summary>` MUST NOT include:**
- Requirement IDs: "R290", "R300-R341"
- Sprint/wave/train labels: "Wave 1", "Train B", "R100 Train B"
- GI-FODS-NET-001 phase references
- "minimal implementation", "stub", "placeholder"
- Implementation history: "Previously read from cache (Sprint 5)"

**Example (GOOD):**
```csharp
/// <summary>
/// Gets the protection password for a named sheet, or null if the sheet is not protected.
/// ODF 1.3 §9.1.6 — table:table-source/@table:protect
/// </summary>
/// <param name="sheetName">The sheet name as it appears in the ODF document.</param>
/// <returns>Protection password string, or null if not protected.</returns>
public string? GetSheetProtection(string sheetName)
```

**Example (BAD — prohibited):**
```csharp
/// <summary>
/// Gets sheet protection. R100 Train B — governs GI-FODS-NET-001 Phase 3 requirements.
/// Minimal implementation suitable for governed test coverage.
/// </summary>
public string? GetSheetProtection(string sheetName)
```

### 2.2 TODO Comments in .NET

All TODO comments MUST follow the governed format:
```csharp
// TODO(GAP-PCG-007): implement XML read path for sheet protection
//   ODF: table:table-source/@table:protect (ODF 1.3 §9.1.6)
//   Resolution: TC-PQLM-015 FODS rebuild sprint
```

**Prohibited:**
```csharp
// TODO: GI-FODS-NET-001 Phase 3b/3c — replace each getter with ODF XML read
// TODO: implement R290 requirements
// HACK: wave 1 stopgap
```

### 2.3 Phase/Sprint Reference Comments (PROHIBITED)

Any comment containing the following patterns in product `.cs` files is prohibited:
- `GI-FODS-NET-001 Phase`
- `R[0-9]+ Train [A-Z]`
- `Wave [0-9]+`
- `Sprint [0-9]+`
- `R[0-9][0-9][0-9]` in isolation (i.e., not part of a valid gap ref or test name)

Existing violations must be replaced with governed gap references or removed.

---

## 3. Cross-Language Policy: Sprint History Residue (PROHIBITED)

Sprint/wave/train/gate implementation history must NOT appear in:
- Comments
- XML doc `<summary>` blocks
- Python docstrings
- Module-level variable names
- Constant values (string literals that contain sprint IDs)
- File headers

**Where sprint history BELONGS:** `.local/evidences/` evidence declarations, git commit messages, plan files.
**Where sprint history does NOT belong:** product source code.

---

## 4. Validator Coverage

| Validator | What It Checks |
|---|---|
| V87 | Product .py/.cs files for sprint/wave/train/run identifiers in comments |
| V88 | Public `def` in Python without docstring |
| V89 | TODO/FIXME/HACK without recognized GAP-*/TC-* reference |

These validators block sprint closeout when triggered (GOV_BLOCK severity).

---

## 5. Enforcement Points

- Pre-commit hook: V87, V88, V89
- Sprint closeout (autonomous_cycle.py): V87, V88, V89
- Reviewer rubric: scores documentation quality per file
- Certification requirement: all public APIs must have complete documentation
