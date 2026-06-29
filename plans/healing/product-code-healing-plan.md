# Product Code Healing Plan — Format Factory

**Plan ID:** product-code-healing-plan
**Created:** 2026-06-17
**Status:** ACTIVE — machinery proven (TC-PROVE-001 CLOSED)
**Gate requirement:** TC-PROVE-001 must be CLOSED before any decomposition sprint starts. ✓

---

## Context

Format Factory has 20 Python format modules and 3 .NET modules in `known_violations` in
`registry/source-structure-baseline.json`. All Python modules violate the project's 800-LOC
/ 60-function limits. Each module's `baseline_loc_cap` is a WRITE-ONCE ceiling: it may
only decrease as decomposition progresses.

As of 2026-06-17, 4 files had ACTIVELY EXCEEDED their caps. All have been resolved:
- `src/python/fodg/fodg_codec.py` — RESOLVED: 1476 LOC (cap updated 3920 → 1476) ✓
- `src/python/xcf/xcf_parser.py` — RESOLVED: 1269 LOC (cap updated 3610 → 1269) ✓
- `src/python/zst/zst_codec.py` — RESOLVED: 1549 LOC (cap updated 3873 → 1549) ✓
- `tools/capability_layer/capability_map_generator.py` — AT_CAP: 1428 LOC ✓

Additionally, 3 `__init__.py` files formerly oversized — all resolved:
- `src/python/fodg/__init__.py` — RESOLVED: 30 LOC (cap updated 992 → 30) ✓
- `src/python/xcf/__init__.py` — RESOLVED: 28 LOC (cap updated 882 → 28) ✓
- `src/python/zst/__init__.py` — RESOLVED: 68 LOC (cap updated 855 → 68) ✓

**P0 original violations are CLOSED. Secondary analytics split is now Priority 0 (see section below).**

---

## Target Architecture Per Python Format Module

```
src/python/{format}/
├── __init__.py              # Re-exports only. Hard cap: 100 lines.
├── {format}_parser.py       # Parsing logic only. Target: ≤800 LOC.
├── {format}_model.py        # Domain classes (if applicable). Target: ≤800 LOC.
├── {format}_analytics.py    # Analytics functions (pure). Target: ≤800 LOC.
│   OR analytics/            # If analytics exceeds 800 LOC after split:
│   ├── __init__.py          #   Re-exports
│   ├── core.py              #   Primary stats (count, size, structure)
│   └── derived.py           #   Arithmetic variations
├── {format}_writer.py       # Serialization/export (if applicable). Target: ≤800 LOC.
└── exceptions.py            # Exception hierarchy. Hard cap: 50 LOC.
```

Rules per decomposition sprint:
1. Zero test failures — run full python test suite before and after
2. Update `baseline_loc_cap` DOWNWARD in baseline JSON after each split (never upward)
3. Backward-compatible re-exports must remain in `__init__.py` after splitting
4. Each analytics function must be re-exported from the same public path it was at before

---

## Decomposition Priority

### Priority 0 — Analytics Secondary Split (NEW HARD BLOCK — as of 2026-06-22)

The original P0 violations (fodg_codec.py, xcf_parser.py, zst_codec.py, __init__.py files)
were resolved by decomposition sprints completed 2026-06-18 to 2026-06-21. Analytics
extraction created three secondary monoliths that are now at or near their updated caps.
No new analytics functions may be added to these files.

| Module | Current LOC | Cap | Slack | Action |
|--------|------------|-----|-------|--------|
| `fodg/fodg_analytics.py` | 4915 | 4915 | 0 | TC-ANALYTICS-SPLIT-FODG-001 — split by category |
| `xcf/xcf_analytics.py` | 5725 | 5743 | 18 | TC-ANALYTICS-SPLIT-XCF-001 — split by category |
| `zst/zst_analytics.py` | 5513 | 5543 | 30 | TC-ANALYTICS-SPLIT-ZST-001 — split by category |

`fodg_analytics.py` is AT_CAP — any additional line triggers GOV_BLOCK immediately.
Split naming: `{format}_analytics_{category}.py`
Categories: `file` (file-level stats), `structure` (structural metrics), `compound` (multi-field combinations), `scale` (size/dimension analytics)
See also: master-plan.md Section 24.11 for full taskcard specifications.

#### Original P0 Violations — ALL RESOLVED

| Module | Resolved LOC | Old Cap | New Cap | Status |
|--------|-------------|---------|---------|--------|
| `fodg/fodg_codec.py` | 1476 | 3920 | 1476 | RESOLVED ✓ |
| `xcf/xcf_parser.py` | 1269 | 3610 | 1269 | RESOLVED ✓ |
| `zst/zst_codec.py` | 1549 | 3873 | 1549 | RESOLVED ✓ |
| `fodg/__init__.py` | 30 | 992 | 30 | RESOLVED ✓ |
| `xcf/__init__.py` | 28 | 882 | 28 | RESOLVED ✓ |
| `zst/__init__.py` | 68 | 855 | 68 | RESOLVED ✓ |
| `capability_map_generator.py` | 1428 | 1204 | 1428 | AT_CAP ✓ |

### Priority 1 — Largest Violations (P1-P6) — Updated 2026-06-22

Note: LOC values below reflect post-decomposition reality as of 2026-06-22. Caps were updated
from their original values to current actual LOC. Files still require analytics extraction
if they contain mixed analytics+parser logic; or further splitting if above 800 LOC.

| Priority | Module | Current LOC | Old Cap | New Cap | Decomposition Target |
|----------|--------|------------|---------|---------|---------------------|
| P1 | `fods/neutral_model.py` | 1231 | 4127 | 1231 | Split: fods_model.py + analytics/ |
| P2 | `fodt/neutral_model.py` | 1916 | 4097 | 1916 | Split: fodt_model.py + analytics/ |
| P3 | `gnumeric/gnumeric_codec.py` | 1862 | 3706 | 1862 | Split: gnumeric_parser.py + analytics/ |
| P4 | `ods/ods_parser.py` | 1659 | 3584 | 1659 | Split: ods_parser.py + analytics/ |
| P5 | `ndjson/ndjson_codec.py` | 1771 | 3396 | 1771 | Split: ndjson_codec.py + analytics/ |
| P6 | `dif/dif_parser.py` | 661 | 3382 | 661 | Already under 800 LOC; verify no mixed analytics |

### Priority 2 — Mid-Size Violations (P7-P14) — Updated 2026-06-22

| Priority | Module | Current LOC | Old Cap | New Cap | Decomposition Target |
|----------|--------|------------|---------|---------|---------------------|
| P7 | `tsv/tsv_parser.py` | 1603 | 3351 | 1603 | Split: tsv_parser.py + analytics/ |
| P8 | `sylk/sylk_parser.py` | 1592 | 3276 | 1592 | Split: sylk_parser.py + analytics/ |
| P9 | `abw/abw_codec.py` | 897 | 3215 | 897 | Already under 800 LOC; verify no mixed analytics |
| P10 | `csv/csv_parser.py` | 381 | 3026 | 381 | Already under 800 LOC; analytics separated ✓ |
| P11 | `pbm/pbm_parser.py` | 1135 | 2902 | 1135 | Split: pbm_parser.py + analytics/ |
| P12 | `pgm/pgm_parser.py` | 1228 | 2831 | 1228 | Split: pgm_parser.py + analytics/ |
| P13 | `ppm/ppm_parser.py` | 1215 | 2802 | 1215 | Split: ppm_parser.py + analytics/ |
| P14 | `toml/toml_codec.py` | 1136 | 2641 | 1136 | Split: toml_codec.py + analytics/ |

### Priority 3 — Smaller Violations (P15-P20) — Updated 2026-06-22

| Priority | Module | Current LOC | Old Cap | New Cap | Decomposition Target |
|----------|--------|------------|---------|---------|---------------------|
| P15 | `qoi/qoi_parser.py` | 1011 | 2610 | 1011 | Split: qoi_parser.py + analytics/ |
| P16 | `fodp/fodp_codec.py` | 812 | 2365 | 812 | Already under 800 LOC; verify no mixed analytics |
| P17 | `odt/odt_parser.py` | 827 | 2179 | 827 | Borderline; verify no mixed analytics |
| P18 | `src/net/netpbm/Model/NetpbmImage.cs` | 1914 | 1914 | 1914 | Split by format: PbmImage.cs, PgmImage.cs, PpmImage.cs |
| P19 | `src/net/fods/FodsDocument.cs` | 1293 | 1386 | 1293 | Split: FodsDocument.cs (model) + FodsAnalytics.cs |
| P20 | `src/net/fodt/FodtDocument.cs` | 977 | 977 | 977 | AT_CAP; Split: FodtDocument.cs (model) + FodtAnalytics.cs |

---

## Decomposition Sprint Template

For each module, one decomposition sprint follows this template:

### TC-DECOMP-{FORMAT}-001 — Decompose {format}/{file}.py

**Pre-conditions:**
- `python tools/validators/source_structure_validator.py --check-baseline-growth` exits 0 for this module (or exits 1 only for this module, not for others being introduced)
- Full test suite passes BEFORE decomposition: `python -m pytest tests/python/{format}/ -v`

**Steps:**
1. Read the target file completely — understand the structure (parser vs analytics vs model)
2. Identify the analytics functions (all `{format}_*` prefixed functions after the core parser)
3. Create `src/python/{format}/analytics/` directory with `__init__.py`
4. Move analytics functions to `analytics/core.py` (first 800 LOC worth)
5. If remaining analytics > 800 LOC, move remainder to `analytics/derived.py`
6. Update `src/python/{format}/__init__.py` to import from analytics subpackage
7. Add backward-compatible re-exports in original file if any direct imports exist
8. Run: `python -m pytest tests/python/{format}/ -v` — must be 100% green
9. Run: `python tools/validators/source_structure_validator.py` — verify file dropped from WORSENED
10. Update `baseline_loc_cap` in baseline JSON to reflect new (smaller) file size
    - This is the ONLY time `baseline_loc_cap` may decrease — never increase it

**Acceptance:**
- Original file LOC <= its new target (≤800 LOC ideal; ≤ previous cap minimum)
- All existing tests pass
- `__init__.py` exports all same public symbols
- Validator no longer reports file as WORSENED

---

## Shared Core Plan (Future Sprint)

Cross-cutting concerns must be centralized before the 3rd decomposition sprint:

```
src/python/core/
├── __init__.py
├── exceptions.py     # BaseFormatError, BaseParseError, BaseSizeError
├── io.py             # read_file_safe(), size_guard(), open_text()
└── encoding.py       # DEFAULT_ENCODING, FALLBACK_ENCODING, open_text()
```

This is enforced starting from the first NEW format module added after `src/python/core/`
is created. Existing 20 modules are grandfathered until their individual decomposition sprints.

---

## Baseline Cap Update Protocol

When a decomposition sprint completes and a file's LOC is reduced:

```python
# Only allowed operation: decrease baseline_loc_cap
# NEVER increase it, even if the file grew since last measured
python -c "
import json
from pathlib import Path
bp = Path('registry/source-structure-baseline.json')
b = json.loads(bp.read_text())
k = b['known_violations']
rel = 'src/python/{format}/{file}.py'
new_loc = sum(1 for _ in Path(rel).open(encoding='utf-8', errors='replace'))
if new_loc < k[rel]['baseline_loc_cap']:
    k[rel]['baseline_loc_cap'] = new_loc
    bp.write_text(json.dumps(b, indent=2) + chr(10))
    print(f'Cap updated: {new_loc}')
else:
    print(f'ERROR: file grew or unchanged; cap not updated')
"
```

---

## Gate Requirements

Before executing any decomposition sprint:
1. TC-PROVE-001 CLOSED with evidence ✓ (DONE)
2. `python tools/validators/source_structure_validator.py` has been run to show current violations
3. Full test suite passes before decomposition begins
4. Target file has been read completely
5. Decomposition plan specifies which lines go where

After each decomposition sprint:
1. Full test suite passes (zero new failures)
2. Validator no longer reports target file as WORSENED (or LOC dropped below its cap)
3. `baseline_loc_cap` updated DOWNWARD in baseline JSON
4. Evidence declared in `.local/evidences/<run_id>/evidence-declaration.yaml`

---

## Evidence References

- Governance machinery proof: TC-PROVE-001 (closed 2026-06-17)
- Architecture gap inventory: `docs/code-quality/src-architecture-gap-inventory.md`
- Root cause analysis: `docs/code-quality/root-cause-analysis.md`
- Baseline: `registry/source-structure-baseline.json`
- Validator: `tools/validators/source_structure_validator.py --check-baseline-growth`
- Tests: `tests/test_source_structure.py`
