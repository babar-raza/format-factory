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

As of 2026-06-17, 4 files have ACTIVELY EXCEEDED their caps (detected by proven machinery):
- `src/python/fodg/fodg_codec.py` — 4300 LOC (cap 3920), 617 functions (cap 573)
- `src/python/xcf/xcf_parser.py` — 3944 LOC (cap 3610), 569 functions (cap 531)
- `src/python/zst/zst_codec.py` — 4178 LOC (cap 3873), 557 functions (cap 516)
- `tools/capability_layer/capability_map_generator.py` — 1364 LOC (cap 1204), 24 functions (cap 23)

Additionally, 3 `__init__.py` files newly detected as oversized (added to known_violations):
- `src/python/fodg/__init__.py` — 992 LOC (cap 992)
- `src/python/xcf/__init__.py` — 882 LOC (cap 882)
- `src/python/zst/__init__.py` — 855 LOC (cap 855)

**These 7 files are PRIORITY 0** — they must be the FIRST targets of decomposition.

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

### Priority 0 — Files Actively Exceeding Caps (HARD BLOCK)

These files are currently detected as WORSENED violations by the governance machinery.
They must be decomposed FIRST. No new analytics may be added until the cap is respected.

| Module | Current LOC | Cap | Overage | Action |
|--------|------------|-----|---------|--------|
| `fodg/fodg_codec.py` | ~4300 | 3920 | +380 | Split into fodg_codec.py + analytics/ |
| `xcf/xcf_parser.py` | ~3944 | 3610 | +334 | Split into xcf_parser.py + analytics/ |
| `zst/zst_codec.py` | ~4178 | 3873 | +305 | Split into zst_codec.py + analytics/ |
| `fodg/__init__.py` | 992 | 992 | at cap | Refactor to re-exports only (≤100 lines) |
| `xcf/__init__.py` | 882 | 882 | at cap | Refactor to re-exports only (≤100 lines) |
| `zst/__init__.py` | 855 | 855 | at cap | Refactor to re-exports only (≤100 lines) |
| `tools/capability_layer/capability_map_generator.py` | ~1364 | 1204 | +160 | Split into generator + helpers |

### Priority 1 — Largest Violations (P1-P6)

| Priority | Module | Current LOC | Functions | Decomposition Target |
|----------|--------|------------|-----------|---------------------|
| P1 | `fods/neutral_model.py` | ~4127 | 358 | Split: fods_model.py + analytics/ |
| P2 | `fodt/neutral_model.py` | ~4097 | 358 | Split: fodt_model.py + analytics/ |
| P3 | `gnumeric/gnumeric_codec.py` | ~3706 | 382 | Split: gnumeric_parser.py + analytics/ |
| P4 | `ods/ods_parser.py` | ~3584 | 369 | Split: ods_parser.py + analytics/ |
| P5 | `ndjson/ndjson_codec.py` | ~3396 | 349 | Split: ndjson_codec.py + analytics/ |
| P6 | `dif/dif_parser.py` | ~3382 | 361 | Split: dif_parser.py + analytics/ |

### Priority 2 — Mid-Size Violations (P7-P14)

| Priority | Module | Current LOC | Functions | Decomposition Target |
|----------|--------|------------|-----------|---------------------|
| P7 | `tsv/tsv_parser.py` | ~3351 | 367 | Split: tsv_parser.py + analytics/ |
| P8 | `sylk/sylk_parser.py` | ~3276 | 367 | Split: sylk_parser.py + analytics/ |
| P9 | `abw/abw_codec.py` | ~3215 | 371 | Split: abw_codec.py + analytics/ |
| P10 | `csv/csv_parser.py` | ~3026 | 350 | Split: csv_parser.py + analytics/ |
| P11 | `pbm/pbm_parser.py` | ~2902 | 347 | Split: pbm_parser.py + analytics/ |
| P12 | `pgm/pgm_parser.py` | ~2831 | 344 | Split: pgm_parser.py + analytics/ |
| P13 | `ppm/ppm_parser.py` | ~2802 | 347 | Split: ppm_parser.py + analytics/ |
| P14 | `toml/toml_codec.py` | ~2641 | 370 | Split: toml_codec.py + analytics/ |

### Priority 3 — Smaller Violations (P15-P20)

| Priority | Module | Current LOC | Functions | Decomposition Target |
|----------|--------|------------|-----------|---------------------|
| P15 | `qoi/qoi_parser.py` | ~2610 | 345 | Split: qoi_parser.py + analytics/ |
| P16 | `fodp/fodp_codec.py` | ~2365 | 327 | Split: fodp_codec.py + analytics/ |
| P17 | `odt/odt_parser.py` | ~2179 | 314 | Split: odt_parser.py + analytics/ |
| P18 | `src/net/netpbm/Model/NetpbmImage.cs` | ~1914 | n/a | Split by format: PbmImage.cs, PgmImage.cs, PpmImage.cs |
| P19 | `src/net/fods/FodsDocument.cs` | ~1386 | n/a | Split: FodsDocument.cs (model) + FodsAnalytics.cs |
| P20 | `src/net/fodt/FodtDocument.cs` | ~977 | n/a | Split: FodtDocument.cs (model) + FodtAnalytics.cs |

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
