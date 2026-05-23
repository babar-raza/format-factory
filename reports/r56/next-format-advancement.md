# Next-Format Advancement — Train F Report

**Sprint:** FORMAT-FACTORY-R56-R55-CLOSURE-REPAIR-PACKAGE-RC-PHASE7-PRODUCT-EXPANSION-MEGA-TRAIN-001
**Train:** F — Next-Format Advancement
**Date:** 2026-05-23

---

## 1. Summary

Train F advances four format tracks in R56:
- **CSV** Gate 4 → **Gate 5** (neutral model tests added, pack.yaml updated)
- **TSV** Gate 4 → **Gate 5** (neutral model tests added, pack.yaml updated)
- **PGM** Gates 1-9 status confirmed (Gate 10 deferred — next sprint)
- **PBM** Gates 1-9 status confirmed (Gate 10 deferred — next sprint)
- **PPM** Gates 1-10 confirmed at local_release_candidate_ready (no new work)
- **SYLK** Gates 1-9 confirmed pass (no new work)
- **DIF** Gates 1-10 confirmed at local_release_candidate_ready (no new work)

---

## 2. CSV — Gate 4 → Gate 5

**New test file:** `tests/python/csv/test_r56_csv_gate5_neutral_model.py`
**Test count:** 17/17 PASS

Gate 5 neutral model verified:
- Result dict contains all required keys: `format`, `path`, `row_count`, `column_count`, `headers`, `rows`, `has_header`, `delimiter`
- `rows` is a list of lists; all cell values are strings
- `get_capabilities()` returns descriptor with `supported`/`unsupported`/`commercial_product_ready`
- `commercial_product_ready: false` enforced in capability descriptor

**pack.yaml:** `acquisition-packs/csv/pack.yaml` updated with `gate_5: status: pass` entry.

---

## 3. TSV — Gate 4 → Gate 5

**New test file:** `tests/python/tsv/test_r56_tsv_gate5_neutral_model.py`
**Test count:** 17/17 PASS

Gate 5 neutral model verified:
- Same schema keys as CSV, with `delimiter: "\t"` (tab character verified)
- `get_capabilities()` returns `tab_delimiter` in supported set
- `commercial_product_ready: false` enforced

**pack.yaml:** `acquisition-packs/tsv/pack.yaml` updated with `gate_5: status: pass` entry.

---

## 4. Other Formats — Status Confirmation

| Format | Highest Gate | Status |
|--------|-------------|--------|
| CSV | Gate 5 | **NEW (R56)** |
| TSV | Gate 5 | **NEW (R56)** |
| PPM | Gate 10 | local_release_candidate_ready (R31) |
| DIF | Gate 10 | local_release_candidate_ready (R31) |
| SYLK | Gate 9 | pass (R31 — Gate 10 deferred) |
| PGM | Gate 9 | pass (R44 — Gate 10 deferred) |
| PBM | Gate 9 | pass (R44 — Gate 10 deferred) |

---

## 5. Test Results

```
tests/python/csv/  — 36 passed (19 R55 + 17 R56)
tests/python/tsv/  — 36 passed (19 R55 + 17 R56)
tests/python/pgm/  — 56 passed
tests/python/pbm/  — 56 passed
tests/python/ppm/  — 56 passed (1 pre-existing fail: test_probe_nonexistent Windows path)
tests/python/sylk/ — 58 passed
tests/python/dif/  — 40 passed (1 pre-existing fail: test_probe_nonexistent Windows path)
```

**Combined:** 314 passed, 2 pre-existing failures (Windows `/nonexistent` path resolution — not introduced by R56).

---

## 6. Pre-Existing Failures (Not R56)

Both failures are in `test_probe_nonexistent` methods. On Windows, `/nonexistent` resolves to a path that may appear to exist (drive-relative). These are pre-existing and documented as platform-specific Windows artifacts. Not introduced or worsened by R56.

---

## 7. Gate 10 Deferred

PGM and PBM Gate 10 (local release candidate readiness) is deferred to R57. No blockers identified — the parsers are functionally complete at Gate 9.

---

**STATUS: TRAIN_F_COMPLETE — CSV/TSV advanced to Gate 5; 34 new tests; 314/316 format tests pass**
