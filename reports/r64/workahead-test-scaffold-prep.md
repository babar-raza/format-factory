# R64 W3 — Test Scaffold Preparation

**Sprint:** FORMAT-FACTORY-R64-DELIVERED-SIDECAR-PACKAGING-REPLAY-AI-LIVE-REVIEW-WORKAHEAD-MEGA-TRAIN-001
**Date:** 2026-05-25

---

## Test Scaffolds

R64 test files serve as templates for future sprints:

| Test File | Pattern | Reusable For |
|---|---|---|
| test_r64_delivered_external_sidecar_required.py | Contract + validation logic | R65+ sidecar tests |
| test_r64_final_proof_no_placeholders.py | Forbidden token scanning | R65+ proof tests |
| test_r64_final_zip_sha_matches_sidecar.py | SHA/size/entries matching | R65+ consistency tests |
| test_r64_artifact_discovery_run_awareness.py | Discovery + env var tests | R65+ packaging tests |
| test_r64_fods_advancement.py | Inline XML fixture pattern | Future FODS tests |
| test_r64_fodt_advancement.py | Inline XML fixture pattern | Future FODT tests |
| test_r64_{ods,csv,dif,ppm}_advancement.py | Format stats pattern | Future format tests |

## Candidate Scaffolds (not implemented — test plans only)

| Scaffold | Implementation Status | R65/R66 Action |
|---|---|---|
| XPM parser prototype tests | Plan only | Create after parser exists |
| PAM parser prototype tests | Plan only | Create after parser exists |
| QOI encoder corpus tests | Plan only | Add when encoder implemented |
| ODT stats/export tests | Plan only | Add when stats functions exist |
| DIF/PPM Windows path repair tests | Plan only | Add after probe fix |

---

W3_TEST_SCAFFOLD_STATUS: COMPLETE
