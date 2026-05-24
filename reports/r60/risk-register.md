# R60 Risk Register

**Sprint:** FORMAT-FACTORY-R60-CURRENT-HEAD-RC-ARTIFACTS-SIDECAR-CLOSURE-PHASE11-MEGA-TRAIN-001
**Date:** 2026-05-24

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|------------|
| R1 | Package build fails for pgm/pbm/sylk (new packages) | Low | High | Verify __init__.py API before building |
| R2 | Installed smoke fails — wheel ABI mismatch | Low | High | Use --force-reinstall in clean venv |
| R3 | .NET consumer proof fails (nuget restore issues) | Medium | Medium | Pre-verify local feed path |
| R4 | DIF/PPM Windows probe_nonexistent is pre-existing, not regressions | Confirmed | Low | Document as pre-existing, excluded from verdict |
| R5 | Bundle validation sidecar SHA mismatch | Low | High | Use write_sidecar_proof.py after final build, not before |
| R6 | AI tests require live endpoint (unavailable) | Medium | Low | Fixture mode — all 617 tests pass in fixture mode |
| R7 | Train G new capabilities break existing tests | Low | Medium | Run full pytest after each addition |

## Pre-existing Known Failures (excluded from R60 verdict)

- tests/python/dif/test_dif_parser.py::TestDifProbe::test_probe_nonexistent (Windows /nonexistent path issue)
- tests/python/ppm/test_ppm_parser.py::TestPpmProbe::test_probe_nonexistent (same issue)
