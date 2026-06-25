# Next Agent Execution Prompt

**Sprint/Run ID:** ff-archaeology-20260625
**Generated:** 2026-06-25
**Use this prompt:** At the start of the next autonomous sprint session following this forensic audit.

---

## Context

A forensic audit was completed (run ID: `ff-archaeology-20260625`). Verdict: **READY_AFTER_TARGETED_MACHINERY_REPAIRS**.

The system has strong machinery with 3 targeted gaps. Fix these gaps before continuing broad product deepening.

Full audit bundle: `reports/forensic-audit-20260625/`

---

## Priority Work Items (Top 5)

Execute in this order. Items 1-2 can be parallelized. Item 3 depends on nothing. Items 4-5 are independent.

---

### Item 1: QNAME-BACKFILL-001 — Fix DIF spec_qname

**Priority:** HIGH (blocks V53 for DIF format)
**Estimated time:** 15 minutes
**Skill:** `qname-backfill`

**Files to modify:**
- `src/python/dif/dif_parser.py`

**Exact change:**
```python
# 1. Add ClassVar to imports:
from typing import ClassVar, ...  # (add to existing import)

# 2. In DifData class, change:
spec_qname: str = "dif:data"
# TO:
spec_qname: ClassVar[str] = "dif:data"

# 3. In DifCell class, change:
spec_qname: str = "dif:cell"
# TO:
spec_qname: ClassVar[str] = "dif:cell"
```

**Tests to write:** `tests/python/dif/test_dif_spec_qname.py`
```python
from src.python.dif.dif_parser import DifData, DifCell

def test_dif_data_spec_qname_is_classvar():
    assert DifData.spec_qname == "dif:data"

def test_dif_cell_spec_qname_is_classvar():
    assert DifCell.spec_qname == "dif:cell"

def test_dif_data_spec_qname_class_level_access():
    assert isinstance(DifData.__dict__.get("spec_qname"), str)

def test_dif_cell_spec_qname_class_level_access():
    assert isinstance(DifCell.__dict__.get("spec_qname"), str)
```

**Verification command:**
```
.venv/Scripts/pytest tests/python/dif/test_dif_spec_qname.py -v
```

**Evidence to produce:**
- `tests/python/dif/test_dif_spec_qname.py` (the test file)
- Test run output showing 4+ tests PASS

---

### Item 2: QNAME-BACKFILL-002 — Fix FODG spec_qname

**Priority:** HIGH (blocks V53 for FODG format)
**Estimated time:** 10 minutes
**Skill:** `qname-backfill`

**Files to modify:**
- `src/python/fodg/fodg_codec.py`

**Exact change:**
Find `FodgFrame` class (search for `class FodgFrame`). Add:
```python
# At class body start:
spec_qname: ClassVar[str] = "draw:frame"
spec_fact_ref: ClassVar[str] = "FACT-FODG-001"
```

If `FodgFrame` does not exist as a named class, check if a frame-representation dict is used instead.
In that case, create an authority-only class:
```python
class FodgFrame:
    """Authority-only marker for draw:frame elements in FODG documents."""
    spec_qname: ClassVar[str] = "draw:frame"
    spec_fact_ref: ClassVar[str] = "FACT-FODG-001"
    authority_only: ClassVar[bool] = True
```

**Tests to write:** `tests/python/fodg/test_fodg_spec_qname.py`
```python
from src.python.fodg.fodg_codec import FodgFrame

def test_fodg_frame_spec_qname():
    assert FodgFrame.spec_qname == "draw:frame"

def test_fodg_frame_spec_qname_is_class_level():
    assert "spec_qname" in FodgFrame.__dict__
```

**Verification command:**
```
.venv/Scripts/pytest tests/python/fodg/test_fodg_spec_qname.py -v
```

---

### Item 3: CAP-REPAIR-001 — Wire gap_ledger_to_work_items.py into Supervisor Loop

**Priority:** HIGH (open gaps invisible to automated task selection)
**Estimated time:** 45 minutes
**Skill:** None (direct code modification)

**Files to modify:**
- `tools/supervisor/autonomous_cycle.py` (Step 3a task selection section)

**Locate insertion point:**
Search for `Step 3a` in autonomous_cycle.py. The insertion should be after the existing
`capability_feature_compiler.py` call (around line 900-950, near `next-work-items.json` write).

**Change to make:**
```python
# --- CAP-REPAIR-001: Wire gap ledger compiler ---
_gap_ledger_path = repo_root / "reports" / "capability-layer" / "gap-ledger.json"
_gap_items_out = repo_root / ".local" / "supervisor" / "product" / "gap-work-items.json"
try:
    import sys as _sys_cap
    _tools_dir = str(repo_root / "tools" / "supervisor")
    if _tools_dir not in _sys_cap.path:
        _sys_cap.path.insert(0, _tools_dir)
    from gap_ledger_to_work_items import build_work_items_from_gap_ledger
    _gap_items = build_work_items_from_gap_ledger(str(_gap_ledger_path))
    _gap_items_out.parent.mkdir(parents=True, exist_ok=True)
    _gap_items_out.write_text(json.dumps(_gap_items, indent=2))
    print(f"[CAP-REPAIR-001] Gap ledger compiler: {len(_gap_items)} work items written")
except Exception as _cap_e:
    print(f"[CAP-REPAIR-001] Gap ledger compiler failed (non-blocking): {_cap_e}")
# --- end CAP-REPAIR-001 ---
```

**Tests to write:** `tests/supervisor/test_tc_cap_repair_001.py`
```python
def test_gap_ledger_compiler_produces_output():
    """Verify gap-work-items.json is written when gap_ledger.json has open entries."""
    gap_items_path = REPO_ROOT / ".local/supervisor/product/gap-work-items.json"
    assert gap_items_path.exists(), "gap-work-items.json should be written"
    items = json.loads(gap_items_path.read_text())
    assert isinstance(items, list)
    assert len(items) > 0

def test_gap_work_items_have_gap_ledger_ref():
    """Verify each work item from gap compiler has gap_ledger_ref field."""
    gap_items_path = REPO_ROOT / ".local/supervisor/product/gap-work-items.json"
    items = json.loads(gap_items_path.read_text())
    for item in items:
        assert "gap_ledger_ref" in item, f"Missing gap_ledger_ref in {item.get('item_id', '?')}"
```

**Verification:** After modifying autonomous_cycle.py, run:
```
python tools/supervisor/autonomous_cycle.py --dry-run 2>&1 | grep CAP-REPAIR-001
```
Expected output: `[CAP-REPAIR-001] Gap ledger compiler: N work items written`

**Update baseline cap** after modification:
```
python tools/supervisor/update_source_baseline.py --path tools/supervisor/autonomous_cycle.py
```

---

### Item 4: SRC-STD-001 — Create ODS Domain Model

**Priority:** MEDIUM (Gen3 → Gen4 upgrade; enables typed access for ODS)
**Estimated time:** 45 minutes
**Skill:** `add-python-object-model-feature`

**Files to create:**
- `src/python/ods/models.py`

**Template:**
```python
from __future__ import annotations
from typing import ClassVar, List, Optional
from pathlib import Path

class OdsDocument:
    """Domain model for OpenDocument Spreadsheet (.ods) files."""

    spec_qname: ClassVar[str] = "office:document"
    spec_fact_ref: ClassVar[str] = "FACT-ODS-001"
    namespace_uri: ClassVar[str] = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"

    def __init__(self, model: dict):
        self._model = model

    @classmethod
    def from_file(cls, path) -> "OdsDocument":
        from .ods_parser import parse_ods
        return cls(parse_ods(str(path)))

    @property
    def sheet_count(self) -> int:
        return len(self._model.get("sheets", []))

    @property
    def sheets(self) -> list:
        return self._model.get("sheets", [])

    def get_cell(self, sheet_idx: int, row: int, col: int):
        sheets = self._model.get("sheets", [])
        if sheet_idx >= len(sheets):
            return None
        rows = sheets[sheet_idx].get("rows", [])
        if row >= len(rows):
            return None
        cells = rows[row]
        if col >= len(cells):
            return None
        return cells[col]

    def to_dict(self) -> dict:
        return self._model.copy()
```

**Export from `src/python/ods/__init__.py`:**
```python
from .models import OdsDocument
```

**Tests to write:** `tests/python/ods/test_ods_document_model.py`
- 20+ tests covering `from_file()`, `.sheet_count`, `.sheets`, `.get_cell()`, `.to_dict()`, `spec_qname`

**Verification:**
```
.venv/Scripts/pytest tests/python/ods/test_ods_document_model.py -v
```

---

### Item 5: G11-001 — Prepare Gate 11 Sign-Off Packet for FODS/FODT

**Priority:** HIGH (commercial release gating)
**Estimated time:** 30 minutes
**Skill:** `check-gate`

**Files to create:**
- `reports/gate11/fods-fodt-sign-off-packet.md`

**Content to include:**
1. Gate 11 criteria checklist (C1-C20 .NET, P1-P11 Python) with evidence for each criterion
2. Sub-gate G11-G approval confirmation (2026-06-05)
3. V48 confirmation: no architecture_only stubs in RELEASE_GATE evidence
4. Test summary: 638 FODS .NET tests PASS, 93 FODS Python tests PASS, 131 FODT Python PASS
5. Package evidence: aspose-format-factory-fods and aspose-format-factory-fodt wheels built+installed
6. Request section: "Awaiting Babar Raza commercial sign-off for Gate 11 execution"

**Note on authority:** Gate 11 EXECUTION (commercial release) is a TRUE_EXTERNAL_GATE — Babar Raza is the sole approver. The packet preparation is agent-owned; the sign-off is not.

---

## Pre-Sprint Checklist

Before starting, verify:
- [ ] `check_continuation.py` returns CONTINUE (not STOP)
- [ ] `reports/supervisor/approval-gates.md` shows AUTONOMOUS_CONTINUE: YES
- [ ] No active plan lock files from prior session blocking continuation
- [ ] `src/python/dif/dif_parser.py` — confirm DifData and DifCell classes exist
- [ ] `src/python/fodg/fodg_codec.py` — confirm FodgFrame class (or identify dict-based approach)
- [ ] `tools/supervisor/gap_ledger_to_work_items.py` — confirm `build_work_items_from_gap_ledger()` function signature

## Post-Sprint Evidence Declaration

After completing items 1-3, declare in evidence-declaration.yaml:
```yaml
declared_scope: "QName backfill + capability compiler wiring"
completed_work_items:
  - "QNAME-BACKFILL-001"
  - "QNAME-BACKFILL-002"
  - "CAP-REPAIR-001"
evidence_artifacts:
  - path: "tests/python/dif/test_dif_spec_qname.py"
    type: test_file
    description: "V53 compliance tests for DIF spec_qname ClassVar"
    related_work_items: ["QNAME-BACKFILL-001"]
  - path: "tests/python/fodg/test_fodg_spec_qname.py"
    type: test_file
    description: "V53 compliance test for FodgFrame spec_qname"
    related_work_items: ["QNAME-BACKFILL-002"]
  - path: "tools/supervisor/autonomous_cycle.py"
    type: source_file
    description: "CAP-REPAIR-001 gap ledger compiler wiring in Step 3a"
    related_work_items: ["CAP-REPAIR-001"]
```
