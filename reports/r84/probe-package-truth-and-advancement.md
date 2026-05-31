# R84 Train O: Probe Package Truth and Advancement

**Sprint:** FORMAT-FACTORY-R84
**Train:** O
**Date:** 2026-05-31
**Status:** COMPLETE

## Installed API Verification

### FODP
- `probe_fodp(path)` — returns {exists, valid_header, encoding, element_count} — VERIFIED
- `parse_fodp(path)` — returns result dict — VERIFIED
- Gate status: Gates 1-9 PASSED; Gate 10 local_release_candidate_ready

### FODG
- `probe_fodg(path)` — returns {exists, valid_header, encoding, element_count} — VERIFIED
- `parse_fodg(path)` — returns result dict — VERIFIED
- Gate status: Gates 1-9 PASSED; Gate 10 local_release_candidate_ready

### Gnumeric
- `probe_gnumeric(path)` — returns {exists, valid_header, compressed, sheet_count} — VERIFIED
- `parse_gnumeric(path)` — returns result dict — VERIFIED
- Gate status: Gates 1-9 PASSED; Gate 10 local_release_candidate_ready

### ABW
- `probe_abw(path)` — returns {exists, valid_header, encoding} — VERIFIED
- `parse_abw(path)` — returns result dict — VERIFIED
- Gate status: Gates 1-9 PASSED; Gate 10 local_release_candidate_ready

## Safe Probe Improvement

Improved `probe_fodg` to return `element_count` from the root SVG element (was missing).
Source: `src/python/fodg/fodg_codec.py`

## Overclaim Status

All four packages (FODP/FODG/Gnumeric/ABW) correctly set:
- `commercial_product_ready: false`
- `__capability_level__: "alpha-foss-preview"`

No overclaims detected. R78 corrections remain in place.

## Result

PASS — all four packages verified from installed state; one minor probe improvement made.
