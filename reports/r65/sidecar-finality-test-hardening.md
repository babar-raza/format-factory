# R65 Sidecar Finality Test Hardening

## Changes
- R64 sidecar tests had skip-when-not-built behavior; R65 sidecar tests skip only in prebuild mode
- DIF/PPM probe tests fixed: replaced "/nonexistent" with long path that doesn't exist on Windows

## Tests Modified
- tests/python/dif/test_dif_parser.py: "/nonexistent" → "/nonexistent_path_that_does_not_exist_anywhere"
- tests/python/ppm/test_ppm_parser.py: same fix

## Verification
- DIF probe_nonexistent: PASS
- PPM probe_nonexistent: PASS
- Invariant tests: 6/6 PASS (after Train E fix)

SIDECAR_FINALITY_HARDENING_STATUS: COMPLETE
