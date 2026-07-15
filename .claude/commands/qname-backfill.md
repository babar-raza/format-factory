---
version: "1.0"
last-updated: "2026-06-23"
phase-available: "all"
gate-required: null
created-by: TC-SKILL-HARDENING-001
spec_qname_required: "false"
overflow_split_allowed: "false"
product_track: "foss_python_qname"
---

# /qname-backfill

## Purpose

Backfill spec authority classes for a format's QName registry entries.
Resolves `V53 WARN` for entries with `python_file=null`.

## When to Use

Use this skill when:
- `shared/qname-registry/{format}.yaml` has entries with `python_file: null`
- `status` is `seeded` or `architecture_only` and you want to promote to `implementing`
- V53 returns WARN for a format's registry entries

## Pattern

### Step 1: Check registry

Read `shared/qname-registry/{format}.yaml`. Identify entries with `python_file: null`.

### Step 2: Create spec class

Create `src/python/{format}/spec/{domain}/{element}.py`:

```python
"""
{FORMAT} structural element: {format}:{element}

Spec ref: {spec_reference}
Fact ref: {FACT-FORMAT-NNN}
QName: {format}:{element}
Canonical class: {Element}
Facade: {FormatElement}
"""
from __future__ import annotations
from typing import Any, ClassVar


class {Element}:
    """Canonical spec-shaped class for {format}:{element}."""

    spec_qname: ClassVar[str] = "{format}:{element}"
    spec_fact_ref: ClassVar[str] = "{FACT-FORMAT-NNN}"
    namespace_uri: ClassVar[str] = "{urn:format:{format}:1.0}"
    local_name: ClassVar[str] = "{element}"
    facade_names: ClassVar[list] = ["{FormatElement}"]

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data

    def to_dict(self) -> dict[str, Any]:
        return dict(self._data)

    def __repr__(self) -> str:
        return f"{Element}()"
```

### Step 3: Create Compat facade

Create `src/python/{format}/Compat/{format}_{element}.py`:

```python
"""FormatElement — production facade for {format}:{element}."""
from __future__ import annotations
from typing import ClassVar
from ..spec.{domain}.{element} import {Element} as _Spec{Element}


class {FormatElement}(_Spec{Element}):
    """Production facade for {format}:{element}."""
    spec_qname: ClassVar[str] = "{format}:{element}"
    spec_fact_ref: ClassVar[str] = "{FACT-FORMAT-NNN}"
    namespace_uri: ClassVar[str] = "{urn:format:{format}:1.0}"
```

### Step 4: Update registry

Edit `shared/qname-registry/{format}.yaml`:
- Set `python_file: "src/python/{format}/spec/{domain}/{element}.py"` (canonical spec/ path, NOT Compat/)
- Change `status` from `seeded` to `implementing`

### Step 5: Verify

```bash
python tools/validators/qname_structure_validator.py src/python/{format}/ --format {format}
.venv/Scripts/pytest tests/python/{format}/ -x -q
```

V53 should produce 0 warnings for the updated entries.

## Allowed Paths

- `src/python/{format}/spec/{domain}/{element}.py` (new)
- `src/python/{format}/Compat/{format}_{element}.py` (new)
- `shared/qname-registry/{format}.yaml`

## Forbidden Paths

- `src/python/{format}/{format}_codec.py` — no codec changes
- `tools/supervisor/` — no validator changes
- Other format directories

## Required Evidence

- V53 0 warnings for updated entries
- Behavioral instantiation test: `{FormatElement}({'name': 'test'}).spec_qname == '{format}:{element}'`
- Existing format tests still pass

## Declaration Fields

```yaml
spec_fact_refs:
  - {FACT-FORMAT-NNN}
skill_used: qname-backfill
```

## Required Inputs

- `format_id` — format identifier from the format registry
- `spec_qname` — spec QName string to use for backfill (e.g. `table:table-row`)

## Steps

1. Read the target format's source files from `src/python/<format>/`
2. Identify model classes and codec functions lacking `spec_qname` annotations
3. Look up the correct QName for each item in the SAL fact registry
4. Add `spec_qname: ClassVar[str] = "<namespace>:<element>"` to each model class
5. Add QName docstring comments to codec functions where applicable
6. Verify the format's test suite still passes after the additions

## Stop Conditions

- Stop if any gate or release state would be modified
- Stop if spec_qname fields cannot be populated for the target format

## Output Format

- Structured result written to `reports/` in YAML or JSON format
- Human-readable summary printed to stdout
- Verdict: PASS / FAIL with per-item evidence
