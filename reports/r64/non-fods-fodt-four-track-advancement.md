# R64 Train I — Non-FODS/FODT Four-Track Advancement

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## Track 1: ODS — ods_sheet_name_list()

New function: `ods_sheet_name_list(data)` — returns list of sheet names from ODS data dict.

- Implementation: `src/python/ods/ods_stats.py`
- Tests: `tests/python/ods/test_r64_ods_advancement.py`

## Track 2: CSV — csv_field_type_summary()

New function: `csv_field_type_summary(rows)` — returns dict with counts of numeric, empty, and text fields.

- Implementation: `src/python/csv/csv_stats.py`
- Tests: `tests/python/csv/test_r64_csv_advancement.py`

## Track 3: DIF — dif_numeric_range()

New function: `dif_numeric_range(data)` — returns dict with min/max across all numeric tuples.

- Implementation: `src/python/dif/dif_stats.py`
- Tests: `tests/python/dif/test_r64_dif_advancement.py`

## Track 4: PPM — ppm_brightness_histogram()

New function: `ppm_brightness_histogram(data, bins=4)` — returns dict mapping bin labels to pixel counts.

- Implementation: `src/python/ppm/ppm_stats.py`
- Tests: `tests/python/ppm/test_r64_ppm_advancement.py`

---

NON_FODS_FODT_ADVANCEMENT_STATUS: COMPLETE
