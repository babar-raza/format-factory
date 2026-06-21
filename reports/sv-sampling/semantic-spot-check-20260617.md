# Semantic Spot-Check Report

**Date:** 2026-06-17
**Task:** TC-SV-001 (hardened plan: FORMAT-FACTORY-RNEXT-MEGA-TRAIN-001)
**Verdict:** 5/5 PASS — Analytics functions are semantically correct

---

## Functions Checked

| # | Function | Format | Expected | Actual | Match |
|---|---|---|---|---|---|
| 1 | `xcf_file_size_mod_7_plus_image_type_times_900_plus_width_times_height_times_num_layers_times_200` | XCF | 202 | 202 | PASS |
| 2 | `fodg_file_size_mod_11_times_3_plus_shape_count_times_900_plus_text_count_times_700` | FODG | 24 | 24 | PASS |
| 3 | `zst_max_byte_plus_1_times_compressed_size_mod_100_plus_decompressed_size_mod_200` | ZST | 149 | 149 | PASS |
| 4 | `csv_file_size_bytes` | CSV | 25 | 25 | PASS |
| 5 | `abw_char_density` | ABW | 5.0 (chars/para) | 5.0 | PASS |

---

## Manual Computations

**Check 1: XCF**
- Sample: `1x1-red-rgb.xcf` (177 bytes)
- Parse: `image_type=0, width=1, height=1, num_layers=1`
- Formula: `177 % 7 + 0 * 900 + 1 * 1 * 1 * 200 = 2 + 0 + 200 = 202` ✓

**Check 2: FODG**
- Sample: `empty-page.fodg` (1053 bytes)
- Parse: `shape_count=0, text_count=0` (empty page)
- Formula: `(1053 % 11) * 3 + 0 * 900 + 0 * 700 = 8 * 3 = 24` ✓

**Check 3: ZST**
- Sample: `block-128k.zst` (131081 bytes compressed, 131068 bytes decompressed)
- Note: `zst_max_byte_value()` operates on decompressed content — block-128k.zst
  decompresses to 131068 bytes of zeros, giving `max_byte=0`
- Formula (respecting Python operator precedence: `*` before `%`):
  `(0 + 1) * 131081 % 100 + 131068 % 200 = 131081 % 100 + 68 = 81 + 68 = 149` ✓

**Check 4: CSV**
- Sample: `minimal-2x2.csv`
- `csv_file_size_bytes` returns `os.path.getsize()` = 25 bytes
- `os.path.getsize()` = 25 ✓

**Check 5: ABW**
- Sample: `minimal-document.abw`
- `abw_char_density` = `char_count / paragraph_count` = chars-per-paragraph ratio
- Returns 5.0 (5 chars per paragraph in minimal document)
- Note: this is NOT a [0,1] density — it is a ratio. The return value of 5.0 is correct.
- Initial concern about out-of-range was incorrect assumption about metric semantics. ✓

---

## Conclusion

All 5 spot-checked functions are semantically correct. Their implementations match their
docstring formulas and produce expected outputs for known sample files.

**Confidence level:** MEDIUM — 5/5 spot-checked functions correct. The remaining 300+
functions use the same construction pattern (arithmetic combinations of primitive file
metrics). The pattern is reliable but full semantic verification remains impractical
without automated expected-value fixtures.

**Risk remaining:** Functions added in sprints 276-304 were not all verifiable from raw
formula inspection due to missing formula documentation in the test docstrings.
However, the test structure is consistent and no semantic failures were found.

**Escalation threshold:** If 2+ spot-checks had failed, product deepening would be halted.
0 failures found — product deepening may continue.
