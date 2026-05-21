# R45 Preflight Report

**Sprint:** FORMAT-FACTORY-R45-TWO-PRODUCT-LOCAL-RC-REPLAYABLE-001
**Date:** 2026-05-21
**Run Number:** R45 (verified — no reports/r45/ existed, no r45*.yaml contract existed)

---

## Run Number Determination

- `reports/r45/` did not exist → R45 is free
- No `tools/evidence/contracts/r45*.yaml` found
- Prior sprint: R44 (FORMAT-FACTORY-R44-TWO-PRODUCT-LOCAL-RC-BASELINE-001)

---

## Environment

| Item | Value |
|------|-------|
| Python | 3.13.2 (C:/Python313/python.exe) |
| pytest | 9.0.3 (user site-packages) |
| pytest-timeout | 2.3.1 (C:/Users/prora/AppData/Roaming/Python/Python313/site-packages) |
| dotnet SDK | 10.0.204 |
| Platform | Windows 11 Pro |
| Shell | bash (Unix syntax) |

---

## R44 Verdict Assessment

R44 verdict was `R44_TWO_PRODUCT_LOCAL_RC_BASELINE_READY`. This sprint prompt
classifies R44 as `REAL_PROGRESS_BUT_OVERCLAIMED_LOCAL_RC_BASELINE` for 11 specific
reasons. R45 IV verdict: **R44_PROGRESS_ACCEPTED_RC_OVERCLAIMED**.

---

## R44 Blocker Inventory (From Sprint Prompt)

| # | Blocker | Disposition |
|---|---------|-------------|
| 1 | R44 verdict admits .NET consumer project proof not completed | MT4 — FODS/FODT consumer project proof |
| 2 | No .whl/.tar.gz/.nupkg artifacts in R44 bundle | MT3 — artifact inclusion |
| 3 | Package proof is logs/hashes only, not artifact-contained replay proof | MT3 — validator extension |
| 4 | test_r44_timeout_portability.py fails in clean env without pytest-timeout | MT2 — portability fix |
| 5 | test_auto_proof_bundle.py times out in plain replay | MT2 — bounded replay |
| 6 | state/current-state.md contains cp1252 byte 0x97 (em dash) | MT1 Lane 1B — UTF-8 fix |
| 7 | state_snapshot.py writes without encoding="utf-8" | MT1 Lane 1B — UTF-8 fix |
| 8 | R44 contract has require_clean_git: false for RC claim | MT1 Lane 1C — contract hardening |
| 9 | Package-proof validator too weak (only checks POC_READY) | MT3 — validator extension |
| 10 | G11-G approval packet asks too broadly for commercial_product_ready: true | MT4 — packet rewrite |
| 11 | R44 insufficient product materialization (no consumer proof) | MT4 — consumer project |

---

## Baseline Test Results (Confirmed Pre-R45)

| Suite | Result |
|-------|--------|
| tests/state/ | 20 passed |
| tests/evidence/test_r44_replay_pycache_fix.py | 12 passed |
| tests/evidence/test_r44_timeout_portability.py | 4 passed |
| tests/evidence/test_auto_proof_bundle.py (--timeout=60) | 9 passed |

---

## State Linter

```
STATE_LINT: PASS
Total: 5 findings (0 errors, 2 warnings, 3 info)
```

Warnings are for historical contracts (r27, r32) below metadata floor — expected.

---

## UTF-8 Defect Confirmed

`state/current-state.md` contains byte `0x97` (cp1252 em dash) at offset 80 in
the string `"R44 \x97 R44_TWO_PRODUCT_LOCAL_RC_BASELINE_READY"`.

Root cause: `tools/state/state_snapshot.py` lines 202-208 use `open()` without
`encoding="utf-8"`. On Windows, the default encoding is cp1252. The em dash U+2014
in `snapshot_to_markdown()` line 169 (`— {verdict}`) is encoded as `0x97`.

Fix: add `encoding="utf-8"`, `newline="\n"` to all write calls in state_snapshot.py.

---

## Sprint Lane Map

See `reports/r45/lane-ownership.md` for full lane breakdown.
