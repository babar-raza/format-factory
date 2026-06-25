# Format Factory — Format Onboarding Guide

**Version:** 1.0 — 2026-06-25
**Authority:** This guide is subordinate to `plans/master-plan.md` and `CLAUDE.md`.
**Purpose:** Step-by-step playbook for adding format 21+ to Format Factory.

A weak agent should be able to add a new format by following this checklist alone.

---

## Prerequisites

Before starting:
- Format has a clear specification (ISO, W3C, vendor, open standard)
- A QName can be assigned: `{namespace}:{element}` (e.g., `csv:row`, `toml:table`)
- At least one sample file exists in `samples/by-format/{format}/valid/`
- Format is not already present in `registry/format-registry.yaml`

---

## Phase A — Registry Entry

### Step A1: QName Registry

Create `shared/qname-registry/{format}.yaml`:

```yaml
format: {FORMAT_UPPERCASE}
namespace_uri: "https://format-factory.io/spec/{format}/1.0"
qnames:
  - qname: "{format}:{primary_element}"
    local_name: "{primary_element}"
    canonical_class: "{PrimaryClass}"
    spec_fact_ref: "FACT-{FORMAT}-001"
    status: seeded
    source_layer: spec
    facade_names: ["{Format}{PrimaryClass}"]
    python_file: "{format}/spec/{primary_element}.py"
    dotnet_file: "src/net/{format}/Spec/{PrimaryClass}.cs"
```

Status lifecycle: `seeded` → `architecture_only` → `implementing` → `implemented` → `stable`

Run skill: `/qname-backfill` (validates registry schema)

### Step A2: Format Registry

Add entry to `registry/format-registry.yaml`:

```yaml
{format}:
  full_name: "{Format Full Name}"
  family: {text|spreadsheet|image|archive|config|binary}
  extensions: [".{ext}"]
  mime_type: "application/{format}"
  spec_url: "https://..."
  gate_level: 0
```

---

## Phase B — Python Parser

### Step B1: Parser Implementation

Create `src/python/{format}/{format}_parser.py`:

```python
"""
{Format} parser — {Format Full Name}
Spec: {FACT-FORMAT-001} — magic bytes, header structure
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import ClassVar, Dict, Any


@dataclass
class {PrimaryClass}:
    spec_qname: ClassVar[str] = "{format}:{primary_element}"
    spec_fact_ref: ClassVar[str] = "FACT-{FORMAT}-001"

    # Core fields
    magic: str = ""
    width: int = 0
    height: int = 0
    # ... format-specific fields


def parse_{format}_strict(path: str) -> {PrimaryClass}:
    """Parse {format} file; raise on any structural violation."""
    ...

def parse_{format}(path: str) -> Dict[str, Any]:
    """Parse {format} file; return neutral model dict."""
    ...

def probe_{format}(path: str) -> Dict[str, Any]:
    """Return header metadata without loading full content."""
    ...

def get_capabilities() -> Dict[str, Any]:
    """Return format capability dict."""
    return {{
        "format": "{format}",
        "read": True,
        "write": False,  # update when writer added
        "spec_qname": "{format}:{primary_element}",
    }}
```

Run skill: `/add-python-api` with `format={format}`

### Step B2: Parser Tests

Minimum tests required for Gate 1-7:

```python
# tests/python/{format}/test_{format}_spec_qname.py
def test_spec_qname_class_level():
    assert {PrimaryClass}.spec_qname == "{format}:{primary_element}"

def test_spec_fact_ref_class_level():
    assert {PrimaryClass}.spec_fact_ref == "FACT-{FORMAT}-001"

# tests/python/{format}/test_{format}_malformed_and_security.py
# Class A: wrong/missing magic
# Class B: invalid header
# Class C: data decode failure
# Security: size guard, injection guard
```

Run skill: `/add-roundtrip-test` with `format={format}`

---

## Phase C — Writer (if format is writable)

### Step C1: Writer Implementation

Create `src/python/{format}/{format}_writer.py`:

```python
def write_{format}(model: Dict[str, Any], dest: str) -> None:
    """Write neutral model dict to {format} file."""
    ...
```

Run skill: `/add-same-format-writer-feature` with `format={format}`

### Step C2: Round-trip Tests

```python
# tests/python/{format}/test_{format}_roundtrip.py
def test_roundtrip_preserves_content(tmp_path):
    original = parse_{format}_strict(str(VALID_SAMPLE))
    dest = tmp_path / "rt.{ext}"
    write_{format}(original.__dict__, str(dest))
    reloaded = parse_{format}_strict(str(dest))
    assert reloaded.{primary_field} == original.{primary_field}
```

---

## Phase D — Domain Model

### Step D1: models.py

Create `src/python/{format}/models.py`:

```python
from __future__ import annotations
from typing import ClassVar, Dict, Any


class {Format}Document:
    spec_qname: ClassVar[str] = "{format}:{primary_element}"
    spec_fact_ref: ClassVar[str] = "FACT-{FORMAT}-001"

    def __init__(self, model: Dict[str, Any]):
        self._model = model

    @classmethod
    def from_file(cls, path: str) -> "{Format}Document":
        from .{format}_parser import parse_{format}
        return cls(parse_{format}(path))

    @property
    def {primary_property}(self):
        return self._model.get("{primary_key}")

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._model)
```

**CRITICAL:** Use `ClassVar[str]` for `spec_qname` in dataclasses. Plain `str` creates an instance field that V53 cannot validate at class level.

---

## Phase E — __init__.py

### Step E1: Public API

`src/python/{format}/__init__.py`:

```python
"""
{Format Full Name} — Format Factory Python package.
Spec: https://...
"""
from .{format}_parser import parse_{format}_strict, parse_{format}, probe_{format}, get_capabilities
from .models import {Format}Document

try:
    from .{format}_analytics import *  # noqa: F401,F403
except ImportError:
    pass

import sys as _sys
import types as _types

_FF_API_EXCLUDE = frozenset({
    'Any', 'ClassVar', 'Dict', 'List', 'Optional', 'Path', 'Set', 'Tuple', 'Union',
    'dataclass', 'field', 'TYPE_CHECKING',
})

__all__ = [
    k for k in vars(_sys.modules[__name__])
    if not k.startswith('_')
    and k not in _FF_API_EXCLUDE
    and not isinstance(getattr(_sys.modules[__name__], k), _types.ModuleType)
]
del _sys, _types

__version__ = "0.1.0"
```

**CRITICAL:** `__version__` must be `"0.1.0"` (not `"0.1.0.dev0"`) to pass customer readiness criterion 8.

---

## Phase F — Packaging

### Step F1: Package Manifest

Add to `packaging/python/package-matrix.yaml`:

```yaml
- name: aspose-format-factory-{format}
  format: {format}
  source: src/python/{format}
  description: "{Format Full Name} — Format Factory Python package"
  gate_target: 7
  capability_level: alpha-foss-preview
  publish_status: local_only_not_published
```

Add to `packaging/python/build-local-packages.py`:
- `PACKAGE_DESCRIPTIONS["{format}"]`
- `PACKAGE_DEPS["{format}"]` (if dependencies needed)

### Step F2: Build and Install

```bash
python packaging/python/build-local-packages.py
.venv/Scripts/pip install --user --force-reinstall \
  .local/package-builds/python-foss/aspose_format_factory_{format}-*.whl
```

### Step F3: Install-Workflow Proof

Create `examples/python/{format}/consumer_roundtrip.py`:

```python
import sys
from pathlib import Path
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import {format}

# Load sample
sample = _REPO / "samples" / "by-format" / "{format}" / "valid" / "sample.{ext}"
model = {format}.parse_{format}_strict(str(sample))
print(f"CONSUMER_PROOF: {format} loaded — {model.{primary_field}}")

# Write (if writable)
from pathlib import Path
dest = Path("/tmp/{format}-proof.{ext}")
{format}.write_{format}(model.__dict__, str(dest))
print("CONSUMER_PROOF: PASS")
```

Update `product-capability-matrix/poc-targets.yaml`:
```yaml
python_foss_status:
  installed_workflow: PASS
```

---

## Phase G — Gate Progression

| Gate | Requirements | Skill |
|------|-------------|-------|
| 1 | Parser exists, 1 test passes | `/add-python-api` |
| 2 | `__init__.py` exports public API cleanly | manual check |
| 3 | Spec_qname ClassVar on primary class | `/qname-backfill` |
| 4 | Round-trip test passes (5+ assertions) | `/add-roundtrip-test` |
| 5 | Malformed input tests (3 classes × 4 tests) | manual |
| 6 | Security guard tests (size + injection) | manual |
| 7 | Install-workflow proof (consumer_roundtrip.py) | `/package-install-proof` |
| 8 | API reference doc created | manual |
| 9 | Release notes created | manual |
| 10 | Domain model class (models.py) | `/add-python-object-model-feature` |
| 11 | All 8 customer-readiness criteria PASS | `/check-gate {format} 11` |

Run `/check-gate {format} {N}` after each phase to verify gate state.

---

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| `spec_qname` as instance field | V53 test `SomeClass.spec_qname` fails with `AttributeError` | Use `spec_qname: ClassVar[str] = "..."` |
| Import conflict (CSV/TSV) | `import csv` picks up stdlib | Add `sys.path.insert(0, str(_REPO))` before import |
| Non-editable install stale | New `models.py` not visible after install | Copy to `.venv/Lib/site-packages/{pkg}/` or reinstall |
| `write_*` returns None | `result.keys()` fails | Don't capture return value of write functions |
| Read-only formats | `write_{format}` does not exist | Mark as read-only in `poc-targets.yaml`; proof = inspect-only |
| `__version__` = "0.1.0.dev0" | Customer readiness criterion 8 fails | Change to `"0.1.0"` before Gate 11 |
| File-based SYLK API | `set_cell_value(doc, ...)` fails | API is `set_cell_value(src_path, dest_path, row, col, val)` |
| FODP read-only | `get_page_count(model)` fails | API takes file path, not model dict |
| ABW mutation | `model = append_paragraph(model, text)` looks wrong | Correct — returns NEW dict, not in-place |
| ZST no write function | `write_zst(...)` not found | Use `open(dest, "wb").write(compress_string(text))` |
| DIF flat model | `doc.rows[0].rows` not found | `DifDocument.rows` is a flat list of `DifCell` objects |
| Unicode output on Windows | `UnicodeEncodeError: cp1252` | Replace Unicode arrows `→` with ASCII `->` |

---

## Format-Specific API Patterns

| Format | Load | Write | Notes |
|--------|------|-------|-------|
| ODS | `set_cell_value / add_row / rename_sheet` + `write_ods` | `write_ods(model, dest)` | ODS uses neutral dict |
| TOML | dict mutation + `write_toml` | `write_toml(model, dest)` | model is dict |
| SYLK | `set_cell_value(src,dest,row,col,val)` | file-based | `SylkDocument.rows=count, .cells=flat list` |
| NDJSON | `append list` + `write_ndjson` | `write_ndjson(records, path)` | records is list of dicts |
| TSV | `write_tsv(rows, dest, headers=headers_list)` | rows are `list[list[str]]` | NOT list-of-dicts |
| CSV | `write_csv_to_file(rows, path, headers=None)` | | Add `sys.path.insert` before import |
| GNUMERIC | `dict cell_grid` + `write_gnumeric` | `export_to_json(dict)` vs `export_to_csv(path)` | Asymmetric export APIs |
| ABW | `append_paragraph(model, text) -> NEW dict` | `write_abw(model, dest)` | Returns NEW dict |
| ZST | `compress_string(text) -> bytes` | `open(dest,"wb").write(bytes)` | No write_zst |
| DIF | `DifCell append to rows[0]` + `write_dif(doc, path)` | | Flat model |
| FODG | `model['pages'][0]['text_content'].append(text)` | `write_fodg(model, dest)` | Dict mutation |
| FODP | read-only inspect | N/A | `get_page_count(path)` takes path NOT model |

---

## Skill Command Reference

| Stage | Skill | Purpose |
|-------|-------|---------|
| QName registry | `/qname-backfill` | Validate and populate qname registry |
| Parser | `/add-python-api` | Scaffold parser + __init__ + basic tests |
| Writer | `/add-same-format-writer-feature` | Scaffold writer + write tests |
| Round-trip | `/add-roundtrip-test` | Add 5+ round-trip test assertions |
| Object model | `/add-python-object-model-feature` | Add domain model class (models.py) |
| Package proof | `/package-install-proof` | Build wheel + install + consumer proof |
| Gate check | `/check-gate {format} {N}` | Evaluate gate N readiness |
| Analytics | `/add-analytics-function` | Add spec-backed analytics (must have GAP entry) |
| Spec parity | `/spec-parity-verification` | Verify spec parity status |

---

*Generated by immutable-percolating-forest TC-INF-002 — 2026-06-25*
