# R50 Preflight

**Sprint:** FORMAT-FACTORY-R50-EVIDENCE-CLOSEOUT-AND-OBJECT-MODEL-HARDENING-001
**Run:** R50
**Date:** 2026-05-22

---

## Environment

| Item | Value |
|------|-------|
| Branch | main |
| HEAD | 0cd1cee |
| Git status | CLEAN |
| Python | 3.13.2 |
| .NET SDK | 10.0.204 |
| .git present | YES |

## Prior Sprint

R49 verdict: `R49_EDITABLE_OBJECT_MODEL_POC_BASELINE_COMPLETE`
R50 corrected R49 classification: `R49_EDITABLE_OBJECT_MODEL_POC_REAL_BUT_CLOSEOUT_EVIDENCE_STALE`

## R49 Evidence Problems Found

1. **Stale proof file** — `bundle-metadata/final-bundle-validation-proof.txt` contains:
   - `SHA-256: (computed after pass 2 build)`
   - `Entries: (computed after pass 2 build)`
   - `Size: (computed after pass 2 build)`
   - `Validation: (computed after pass 2 build)`
   - `pass 2 SHA to follow`
   These are unresolved placeholders. R49 validator missed them (patterns not in guard list).

2. **Artifact manifest hash mismatches** (3/5):
   - FODT wheel: manifest `33cd5a3cae3a0600...92b6c6...` vs actual `33cd5a3cae3a0600...20244751...` — MISMATCH
   - FODS nupkg: manifest `f6e08951...7b47ac68...` vs actual `f6e08951...5fe99a9b...` — MISMATCH
   - FODT nupkg: manifest `6fd23756...6e26e3a6...` vs actual `6fd23756...ebde707d...` — MISMATCH
   - FODS wheel: MATCH
   - ZST wheel: MATCH
   Root cause: manifest was generated from truncated hashes (first 32 chars only).

3. **Validator missed lowercase `sha256:` YAML fields** — `check_artifact_inventory()` only parses `SHA-256:` format.

4. **Validation command log stale** — contained `STATE_SNAPSHOT: PASS (R49 no_final_verdict)` as if final.

5. **No preservation gap taskcards** — TC-FORMULA-001 through TC-PARASTYLE-001 referenced in prose but no taskcard files exist.

6. **No sdists in artifact manifest** — only wheels listed; policy not explicit.

## R50 Run Number Rationale

Next free run number after R49 confirmed: R50

- reports/r49/: EXISTS
- reports/r50/: NEW (this sprint)
- contracts/r49-*: EXISTS
- contracts/r50-*: NEW

## AI Environment

| Variable | Status |
|----------|--------|
| GPT_OSS_ENDPOINT | SET |
| GPT_OSS_API_KEY | SET |
| GPT_OSS_MODEL | NOT_SET |
| PROFESSIONALIZE_API_KEY | SET |
| AGENT_METRICS_ENDPOINT | SET |
| AGENT_METRICS_API_KEY | NOT_SET |

AI endpoint available — controlled pilot possible.
Agent Metrics posting requires AGENT_METRICS_API_KEY — classify AGENT_METRICS_POSTING_ENV_PARTIAL.

## Baseline Test Results

| Suite | Result |
|-------|--------|
| Python FODS + FODT | 383 passed, 4 skipped |
| Evidence/archive/invariants (55 tests) | 55 passed |
| .NET FODS | 157 passed |
| .NET FODT | 145 passed |

STATE_LINT: PASS (2 warnings R27/R32, 3 info)
STATE_SNAPSHOT: PASS
