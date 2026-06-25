# Machinery Repair Plan

**Sprint/Run ID:** ff-archaeology-20260625
**Verdict:** READY_AFTER_TARGETED_MACHINERY_REPAIRS

---

## Summary

Three immediate blockers prevent clean autonomous continuation for all formats:
1. **QNAME-BACKFILL-001**: DIF spec_qname gap (dif:data, dif:cell) — 2 ClassVar injections
2. **QNAME-BACKFILL-002**: FODG spec_qname gap (draw:frame) — 1 ClassVar injection
3. **CAP-REPAIR-001**: gap_ledger_to_work_items.py not wired into supervisor task loop

These three can be fixed in a single focused session (< 2 hours total). All other repairs are deferrable.

---

## Immediate Repairs (This Session or Next Sprint)

### QNAME-BACKFILL-001 — DIF spec_qname Gap

**File:** `src/python/dif/dif_parser.py`

**Root cause:** `DifData` and `DifCell` classes use instance-field `spec_qname: str = "..."` (not ClassVar).
V53 validator requires `spec_qname: ClassVar[str]` accessible at class level.

**Fix:**
```python
# Add to imports
from typing import ClassVar

# In DifData class:
spec_qname: ClassVar[str] = "dif:data"

# In DifCell class:
spec_qname: ClassVar[str] = "dif:cell"
```

**Tests required:**
- `tests/python/dif/test_dif_spec_qname.py` — assert `DifData.spec_qname == "dif:data"`, `DifCell.spec_qname == "dif:cell"`
- V53 compliance: `assert isinstance(DifData.spec_qname, str)` (class-level access, not instance)

**Evidence path:** `src/python/dif/dif_parser.py`
**Risk:** LOW — additive ClassVar injection, no behavioral change
**Time estimate:** 15 minutes

---

### QNAME-BACKFILL-002 — FODG spec_qname Gap

**File:** `src/python/fodg/fodg_codec.py`

**Root cause:** `FodgFrame` class missing `spec_qname` ClassVar entirely.
Registry entry `draw:frame` has `python_file: src/python/fodg/fodg_codec.py` but the class has no spec_qname attribute.

**Fix:**
```python
# Add to imports
from typing import ClassVar

# In FodgFrame class:
spec_qname: ClassVar[str] = "draw:frame"
spec_fact_ref: ClassVar[str] = "FACT-FODG-001"
```

**Tests required:**
- `tests/python/fodg/test_fodg_spec_qname.py` — assert `FodgFrame.spec_qname == "draw:frame"`

**Evidence path:** `src/python/fodg/fodg_codec.py`
**Risk:** LOW — additive ClassVar injection, no behavioral change
**Time estimate:** 10 minutes

---

### CAP-REPAIR-001 — Wire Capability Compiler into Supervisor Loop

**Files:**
- `tools/supervisor/gap_ledger_to_work_items.py` (standalone compiler — needs wiring)
- `tools/supervisor/autonomous_cycle.py` (Step 3a — task selection entry point)

**Root cause:** Two capability compilers exist:
- `capability_feature_compiler.py` — active, wired into autonomous_cycle Step 3a-pre
- `gap_ledger_to_work_items.py` — standalone, produces work items but not consumed by loop

**Fix (Step 3a injection):**
```python
# In autonomous_cycle.py Step 3a, after capability_feature_compiler call:
gap_items_path = repo_root / ".local" / "supervisor" / "product" / "gap-work-items.json"
try:
    from gap_ledger_to_work_items import build_work_items_from_gap_ledger
    gap_items = build_work_items_from_gap_ledger(gap_ledger_path)
    gap_items_path.write_text(json.dumps(gap_items, indent=2))
    logger.info(f"Gap ledger compiler produced {len(gap_items)} work items")
except Exception as e:
    logger.warning(f"Gap ledger compiler failed (non-blocking): {e}")
```

**Tests required:**
- `tests/supervisor/test_tc_cap_repair_001.py` — verify gap-work-items.json is written when gap_ledger.json has open entries
- Integration: verify autonomous_cycle.py Step 3a-pre includes gap_ledger_ref on emitted items

**Risk:** LOW — non-blocking try/except wrapper; compiler failure does not stop cycle
**Time estimate:** 45 minutes (including tests)

---

## Short-Term Repairs (1-2 Sprints)

### SRC-STD-001 through SRC-STD-007 — Domain Models for 7 Gen3 Python Formats

**Purpose:** Upgrade ODS, ODT, PBM, PGM, PPM, QOI, SYLK from Gen3 (no domain model) to Gen4 (models.py + from_file() + typed properties).

**Pattern (identical for each format):**
1. Create `src/python/{format}/models.py`
2. Define `{Format}Document` class with `spec_qname: ClassVar[str]` matching registry
3. Implement `from_file(path)` factory using existing `load()` or `parse_*()` function
4. Add typed properties: `.rows`, `.headers`, `.width`, `.height`, `.cells` etc. from neutral model dict
5. Implement `to_dict()` returning serializable representation
6. Export from `__init__.py` (avoid API pollution — use explicit export names)
7. Write 20+ tests in `tests/python/{format}/test_{format}_document_model.py`

**Per-format spec_qname mapping:**
| Format | Class Name | spec_qname |
|--------|-----------|------------|
| ODS | OdsDocument | office:document |
| ODT | OdtDocument | office:document |
| PBM | PbmImage | pbm:bitmap |
| PGM | PgmImage | pgm:graymap |
| PPM | PpmImage | ppm:pixmap |
| QOI | QoiImage | qoi:chunk |
| SYLK | SylkDocument | sylk:format |

**Skill to use:** `add-python-object-model-feature` (registered, per-format execution)
**Time estimate per format:** 30-45 minutes
**Total:** 3.5-5 hours across 7 formats

---

## Medium-Term Repairs (3-5 Sprints)

### BACKFILL-001 — scan_qname_gaps.py Tool

**Purpose:** Automated inventory of all Python classes missing spec_qname ClassVar.

**Implementation:**
```python
# tools/backfill/scan_qname_gaps.py
# 1. Load all shared/qname-registry/{format}.yaml
# 2. For each registry entry with python_file populated:
#    a. Import the module
#    b. Find the class named by canonical_class
#    c. Check: hasattr(cls, 'spec_qname') and isinstance(cls.__dict__.get('spec_qname'), ...)
#    d. If missing or instance-field: add to gap report
# 3. Output: gaps.json with format, class, file, qname, severity
```

**Output format:** `reports/backfill/qname-gaps-{date}.json`
**Estimated LOC:** ~150 (under 800-LOC cap)
**Tests:** 10 tests verifying gap detection for known-missing classes

---

### BACKFILL-002 — inject_spec_qname.py Tool

**Purpose:** Auto-inject `spec_qname: ClassVar[str]` into classes identified by scan_qname_gaps.py.

**Implementation:**
```python
# tools/backfill/inject_spec_qname.py
# 1. Read gaps.json from scan_qname_gaps.py
# 2. For each gap:
#    a. Read target .py file
#    b. Find class definition via AST
#    c. Inject ClassVar[str] = "ns:localname" after class body opening
#    d. Add ClassVar import if missing
#    e. Write patched file
# 3. Run V53 validator to confirm fix
# 4. Write injection-report.json
```

**Guard:** Dry-run mode (`--dry-run`) produces diff without writing.
**Rollback:** `git revert` (no in-tool rollback needed — git is authoritative).
**Tests:** 8 tests on synthetic .py file with missing ClassVar

---

### PARITY-001 — Extend .NET spec_qname to CSV and NetPBM

**Files:**
- `src/net/csv/CsvDocument.cs` — add `public const string SpecQName = "csv:record";`
- `src/net/netpbm/NetpbmDocument.cs` — add `public const string SpecQName = "netpbm:image";`

**Tests:** Verify constant accessible at class level in existing test files.
**Risk:** LOW — additive constant, no behavior change.

---

### PARITY-002 — Cross-Language Gap Ledger

**Purpose:** Map 10 Python formats without .NET equivalents to the gap ledger.

**Formats lacking .NET:** ABW, DIF, FODG, FODP, GNUMERIC, NDJSON (partial), ODS, ODT, QOI, SYLK, TOML, TSV (partial), XCF

**Action:** Add GAP-PARITY-{FORMAT}-NET-001 entries to gap-ledger.json for each format missing a .NET package.
Each entry: `priority: P5 (LOW)`, `required_for_gate: false`, `can_defer: true`.

---

## Long-Term Repairs (5+ Sprints)

### SAL Auto-Extraction

**Current state:** SAL facts are manually workbench-verified. CHAIN_BROKEN_AT_SAL for 10 text/table/compression formats.

**Required:** A spec-document ingestion pipeline that:
1. Downloads or reads format specification documents (RFC, OASIS spec, etc.)
2. Extracts structured capability claims (FACT-NNN tuples)
3. Populates `.local/spec-cache/{format}/sal-facts-{format}.json`
4. Outputs confidence scores and requires human verification before CHAIN_INTACT status

**Estimated effort:** 3-5 sprints (novel NLP/extraction work, one format at a time)

---

### Durable Failure Memory

**Current state:** No `failure-memory.json` exists. All decision rules are static. Corrections do not auto-propagate.

**Required:**
1. `tools/supervisor/failure_memory.py` — structured failure record writer
2. `failure-memory.json` in `.local/supervisor/` — list of {error_pattern, root_cause, fix_applied, date}
3. `check_continuation.py` reads failure-memory before selecting next work (avoids known failures)

---

### Template Library for Code Generation

**Current state:** Generation is programmatic Python scripts only. No Jinja2 or T4 templates.

**Benefit:** A template library would allow spec-driven generation of:
- `models.py` from qname-registry.yaml
- `Compat/` facades from spec/ classes
- `.NET` project structure from Python equivalents

**Risk:** Over-engineering if only 7 Gen3 formats remain. Evaluate after SRC-STD-001..007 complete.

---

## Repair Roadmap Timeline

| Phase | Timeframe | Items | Effort |
|-------|-----------|-------|--------|
| Immediate | Session 1 | QNAME-BACKFILL-001, 002, CAP-REPAIR-001 | < 2 hours |
| Short-term | Sprints 1-2 | SRC-STD-001..007 (7 domain models) | 4-6 hours |
| Medium-term | Sprints 3-5 | BACKFILL-001/002, PARITY-001/002 | 8-12 hours |
| Long-term | Sprints 5+ | SAL auto-extraction, failure memory, template library | 20+ hours |

**Immediate goal:** Fix 3 immediate blockers → autonomous loop can run cleanly for all 30 products.
**Short-term goal:** All 20 Python formats at Gen4 → consistent `from_file()` factory + domain model contract.
**Medium-term goal:** Automated backfill eliminates manual per-format work.
**Long-term goal:** True spec-driven generation pipeline requiring no human per-format effort.

---

## Go/No-Go Decision

**Do NOT start SRC-STD-001..007 before:**
1. QNAME-BACKFILL-001/002 are fixed (prevents V53 from blocking new domain model classes for DIF/FODG)
2. CAP-REPAIR-001 is wired (ensures new domain model work items are generated from gap ledger)

**Safe to start immediately:** Any of the 10 Green Gen4 Python formats (FODS, FODT, NDJSON, CSV, TSV, ZST, ABW, XCF, TOML, GNUMERIC) may continue product deepening now. No blockers.
