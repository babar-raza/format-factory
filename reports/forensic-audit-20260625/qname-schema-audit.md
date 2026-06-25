# QName Schema Audit

**Sprint/Run ID:** ff-archaeology-20260625

---

## Summary

QName schema compliance is **84.5%** across 20 Python formats. The compliance pattern
is strong. The schema is correctly implemented for 18/20 formats. Two formats (DIF, FODG)
have high-severity gaps on production codec classes. The enforcement machinery (V53 validator,
shared/qname-registry/ YAML files) is operational.

---

## QName Schema Definition (Current Implementation)

### Schema Location
`shared/qname-registry/schema.yaml` — enforced by `tools/spec/validate_spec_registry.py`

### Required Fields per Registry Entry
```yaml
qname: "ns:localName"           # Canonical qualified name (REQUIRED)
namespace_uri: "http://..."     # Full namespace URI (REQUIRED)
local_name: "localName"         # Element local name (REQUIRED)
canonical_class: "Ns.LocalName" # Spec-hierarchy canonical class name (REQUIRED)
spec_fact_ref: "FACT-FORMAT-NNN" # SAL fact reference (REQUIRED)
status: implementing            # Lifecycle status (REQUIRED)
source_layer: Spec              # Source layer (REQUIRED)
```

### Optional Fields
```yaml
facade_names: [FormatLocalName] # Compat/ facade class name(s)
python_file: src/python/...     # Python implementation path
dotnet_file: src/net/...        # .NET implementation path
```

### Status Lifecycle
`seeded → architecture_only → implementing → implemented → stable → deprecated`

---

## V53 Validator (spec_qname ClassVar Enforcement)

**Validator name:** `validate_spec_qname_refs` (V53)
**Location:** `tools/supervisor/governance_validators.py`
**Purpose:** Verify that authority classes expose `spec_qname` as a class-level `ClassVar[str]`

**What it checks:**
1. All classes in `spec/` hierarchy have `spec_qname: ClassVar[str] = "ns:element"`
2. All domain model classes (models.py) have `spec_qname: ClassVar[str]`
3. All Compat/ facades have `spec_qname` set in class body
4. NO instance-level `spec_qname: str = "..."` (must be ClassVar)

**Enforcement frequency:** Runs at sprint submission time (autonomous_cycle.py validation phase)

**Known violations as of 2026-06-25:**
- DIF: `dif_parser.py:DifData` and `dif_parser.py:DifCell` — missing ClassVar
- FODG: `fodg_codec.py:FodgFrame` — missing ClassVar

---

## Compliance Evidence by Namespace Type

### ODF Formats (FODS, FODT, ODS, ODT)

**Namespace hierarchy:** `office:`, `table:`, `text:`, `style:`, `number:`, `draw:`

**Compliance pattern:**
```python
# Correct — spec class in spec/office/document.py
class Document:
    spec_qname: ClassVar[str] = "office:document"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
    local_name: ClassVar[str] = "document"
    spec_fact_ref: ClassVar[str] = "FACT-FODS-001"
    authority_only: ClassVar[bool] = True
```

**Compat/ facade:**
```python
# Correct — in fods/Compat/fods_body.py
class FodsBody(SpecBody):
    spec_qname = "office:body"
    spec_fact_ref = "FACT-FODS-042"
```

**Status:** FODS 100%, FODT 88.9%, ODS 90%, ODT 90%

### Binary Image Formats (PBM, PGM, PPM, QOI, XCF)

**Namespace pattern:** `pbm:`, `pgm:`, `ppm:`, `qoi:`, `xcf:`

**Compliance pattern:**
```python
# Correct — xcf_parser.py:XcfImage
class XcfImage:
    spec_qname: ClassVar[str] = "xcf:image"
```

**Status:** PBM 100%, PGM 100%, PPM 100%, QOI 95%, XCF 100%

### Text/Table Formats (CSV, DIF, NDJSON, ODS, SYLK, TOML, TSV)

**Namespace pattern:** `csv:`, `dif:`, `ndjson:`, `sylk:`, `toml:`, `tsv:`

**Compliance pattern:**
```python
# Correct — ndjson_codec.py:NdjsonRecord
class NdjsonRecord:
    spec_qname: ClassVar[str] = "ndjson:record"
    authority_only: ClassVar[bool] = True
```

**Status:** CSV 100%, DIF 60% (GAP), NDJSON 100%, SYLK 95%, TOML 100%, TSV 100%

### Compression Formats (ZST)

**Namespace pattern:** `zst:`

**Compliance pattern:**
```python
# Correct — zst_codec.py:ZstFrame (or equivalent)
class ZstDocument:
    spec_qname: ClassVar[str] = "zst:frame"
```

**Status:** ZST 100%

### Presentation / Graphics Formats (FODG, FODP)

**Namespace pattern:** `draw:`, `presentation:`

**Status:** FODP 100%, FODG 66.7% (GAP — `draw:frame` missing on codec class)

### Document Formats (ABW, GNUMERIC)

**Namespace pattern:** `abiword:`, `gnumeric:`

**Status:** ABW 100%, GNUMERIC 100%

---

## Non-Compliant Patterns Found

### Pattern 1: Missing ClassVar on Production Codec Class (HIGH)
**Where:** `src/python/dif/dif_parser.py`, `src/python/fodg/fodg_codec.py`
**Problem:** The production-facing codec classes lack `spec_qname: ClassVar[str]`
even though the Compat/ facades and spec/ skeleton classes have it.
**Root cause:** spec_qname was injected into spec/ and Compat/ but not backfilled
to the original codec classes.
**Fix:** Inject `spec_qname: ClassVar[str] = "..."` and `from typing import ClassVar`
import into the affected classes.

### Pattern 2: Instance Field Instead of ClassVar (FIXED)
**Was in:** `src/python/ods/ods_parser.py:OdsRow`
**Problem:** `spec_qname: str = "table:table-row"` (instance field, not ClassVar)
**Fix applied:** Changed to `spec_qname: ClassVar[str] = "table:table-row"`
**Status:** RESOLVED as of 2026-06-24

### Pattern 3: Wrong Namespace Prefix (FIXED)
**Was in:** ABW (used `abw:` prefix instead of `abiword:`)
**Fix applied:** Corrected to `abiword:` matching ODF/AbiWord spec namespace
**Status:** RESOLVED

---

## Auto-Enforcement Gaps

**What IS automated:**
- V53 runs at submission time and blocks items with missing spec_qname ClassVars
- `validate_spec_registry.py` validates YAML files against schema
- Knowledge freshness validator (V68) detects drift in spec compliance

**What is NOT automated:**
- No script auto-scans all codec/parser classes and reports missing spec_qname
- No auto-inject script that reads registry → adds ClassVar to codec file
- No CI gate that runs V53 on every commit (runs only during sprint submission)
- No backfill pipeline for new files

**Gap:** If a developer adds a new class to a codec file, V53 will only catch it at the
next sprint submission. There is no pre-commit or CI hook enforcing spec_qname.

---

## Namespace Hierarchy Depth Analysis

All formats follow consistent namespace hierarchy:

| Format Type | Spec Depth | Example |
|-------------|-----------|---------|
| ODF (complex) | 3-4 levels | `spec/office/table/table_cell.py` |
| Document | 2-3 levels | `spec/document/paragraph.py` |
| Image | 2 levels | `spec/bitmap/row.py` |
| Table/Text | 1-2 levels | `spec/record/field.py` |
| Compression | 1-2 levels | `spec/frame/block.py` |

**Standard:** All correct. No format violates the hierarchy rule.

---

## Registry Completeness Summary

| Field | Populated | Not Populated | Population Rate |
|-------|----------|--------------|----------------|
| qname | 71/71 | 0 | 100% |
| namespace_uri | 71/71 | 0 | 100% |
| local_name | 71/71 | 0 | 100% |
| canonical_class | 71/71 | 0 | 100% |
| spec_fact_ref | 67/71 | 4 | 94.4% |
| status | 71/71 | 0 | 100% |
| python_file | 64/71 | 7 | 90.1% |
| dotnet_file | 28/71 | 43 | 39.4% |
| facade_names | 55/71 | 16 | 77.5% |

**dotnet_file low population (39.4%):** Expected. Most Python formats have no .NET equivalent.
Only FODS, FODT, NDJSON, TSV, ZST, CSV, NetPBM have .NET projects. Others correctly null.
