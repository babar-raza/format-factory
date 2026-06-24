# FODP Codec Debt Register

Created: 2026-06-23
Updated: 2026-06-23 (convergence loop — file naming correction)
Source: vivid-napping-kurzweil sprint audit + TC-VNK-H-006
Plan: plans/vivid-napping-kurzweil-hardening-addendum.md

## Current State (post-VNK sprint + convergence)

| File | LOC | Functions | Role |
|------|-----|-----------|------|
| src/python/fodp/fodp_codec.py | 200 | 9 | Parser/loader + re-export |
| src/python/fodp/fodp_analytics.py | 603 | 58 | All analytics functions |

Note: `fodp_analytics.py` was originally created as `presentation_document.py` during
TC-VNK-008. Renamed to `fodp_analytics.py` during convergence loop to follow project
convention (`{format}_analytics.py` — consistent with `fodg_analytics.py`, `xcf_analytics.py`,
`zst_analytics.py`). The codec imports from `.fodp_analytics`.

## Resolved Issues

### Import + File Naming (TC-VNK-H-006 discovery + convergence)
- Original TC-VNK-008 created analytics as `presentation_document.py`
- `fodp_codec.py` imports analytics via `from .fodp_analytics import *`
- File renamed `presentation_document.py` -> `fodp_analytics.py` (convergence loop)
- Tests: 254 passed, 0 failures after rename

### Baseline Stale Values
- Evidence-declaration claims `fodp_codec.py` LOC = 748; actual = 200
- Evidence-declaration claims 4 functions extracted; actual = all ~54 analytics functions extracted

## Remaining Debt Items

### DEBT-FODP-001: RESOLVED (file naming corrected)
- `presentation_document.py` renamed to `fodp_analytics.py` (convergence loop)
- No orphaned file remains

### DEBT-FODP-002: Buggy functions using wrong schema field
- **File:** src/python/fodp/fodp_analytics.py
- **Functions:**
  - `fodp_max_text_length` — uses `doc.get("slides", [])` instead of `doc.get("pages", [])`
  - `fodp_text_length_variance` — uses `doc.get("slides", [])`
  - `fodp_slide_text_lengths` — uses `doc.get("slides", [])`
- **Behavior:** Always return 0/0.0/[] because `"slides"` key does not exist in the model (correct key is `"pages"`)
- **Impact:** Functions appear to work but produce incorrect (always-zero) results
- **Resolution:** Change `doc.get("slides", [])` to `doc.get("pages", [])` and `s.get("text", "")` to correct text accessor

### DEBT-FODP-003: Duplicate function definitions
- **File:** src/python/fodp/fodp_analytics.py
- **Pairs (Python uses the LAST definition):**
  1. `fodp_total_text_length` — defined twice (different implementations)
  2. `fodp_total_shape_count` — defined twice (same logic)
  3. `fodp_empty_slide_count` — defined twice (different criteria)
  4. `fodp_max_title_length` — defined twice (different implementations)
- **Impact:** The later definition wins. Behavior depends on which implementation is "correct"
- **Resolution:** Audit each pair, keep the correct one, remove the duplicate

## Baseline Corrections Needed

| File | Baseline LOC | Actual LOC | Action |
|------|-------------|------------|--------|
| src/python/fodp/fodp_codec.py | 812 (cap) | 200 | Cap is frozen; loc should be 200 |
| src/python/fodp/fodp_analytics.py | (none) | 603 | Add baseline entry |
