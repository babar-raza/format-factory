# R51 Preflight Report

**Sprint:** FORMAT-FACTORY-R51-INSTALLED-ARTIFACT-BASELINE-AND-AI-ACCELERATION-001
**Run:** R51
**Date:** 2026-05-22

---

## Environment

| Item | Value |
|------|-------|
| Branch | main |
| HEAD | 0ffa14d |
| Git status | clean |
| Python | 3.13.2 |
| dotnet SDK | 10.0.204 |
| .git exists | yes |

## AI / Telemetry Environment

| Variable | Status |
|----------|--------|
| GPT_OSS_ENDPOINT | SET (35 chars) |
| GPT_OSS_API_KEY | SET (25 chars) |
| GPT_OSS_MODEL | NOT_SET (will use `recommended` via model discovery) |
| AGENT_METRICS_ENDPOINT | SET (112 chars) |
| AGENT_METRICS_TOKEN | SET (14 chars) |
| AGENT_METRICS_API_KEY | NOT_SET (use AGENT_METRICS_TOKEN instead) |

## R50 Defects Found (Lane 1A inputs)

| Defect | Severity | Classification |
|--------|----------|----------------|
| Bundle proof file: `PLACEHOLDER — will be replaced after candidate validation` | CRITICAL | Validator missed — patterns lacked PLACEHOLDER/will-be-replaced |
| FODS wheel missing `fods/csv_exporter.py` | CRITICAL | Wheel built before source added |
| Contract `require_clean_git: false` | HIGH | Clean-closure contract must require clean git |
| Missing reports (5) | HIGH | ai-acceleration-pilot, ai-usage-telemetry-proof, llm-provider-summary, object-model-poc-hardening-summary, artifact-manifest-integrity |
| No Python sdists in bundle | MEDIUM | Policy unclear — wheels-only POC not formally documented |
| .NET consumer proof not relogged in agent environment | LOW | Reported but not freshly replayed in R51 |

## R50 Progress Preserved

- Artifact manifest hashes: VERIFIED (3/5 repaired, all 5 correct in .local/r50-metadata)
- YAML `sha256:` parsing fix: VERIFIED
- Proof-file placeholder patterns extended (but PLACEHOLDER itself missed)
- FODS CSV source code + 19 tests: VERIFIED
- AI live call (274 tokens): VERIFIED from ledger
- Agent Metrics posting: VERIFIED from proof
- Preservation taskcards TC-0054 to TC-0060: VERIFIED
- Phase Audit 3 correction + PA4 kickoff: VERIFIED

## Test Baselines (R51 Start)

| Suite | Result |
|-------|--------|
| Python fods/fodt tests | 402 passed, 4 skipped |
| Evidence + invariants | 57 passed |
| Package tests | 19 passed |
| .NET FODS | 157 passed |
| .NET FODT | 145 passed |

## Run Number Detection

Checked: reports/, contracts/, state/, memory/, git log.
Highest used run: R50. **Next free: R51.**

## State Snapshot

- Latest sprint: R50 — R50_EVIDENCE_CLOSEOUT_REPAIR_AND_OBJECT_MODEL_HARDENING_COMPLETE
- Gate 11 approved: False
- commercial_product_ready: False
- Production blockers: 3 (G11-G_NOT_STARTED, GATE8_AWAITING_HUMAN_APPROVAL, PACKAGE_NOT_PUSHED)

## State Lint

- R27/R32 LEGACY_PRE_FLOOR_30 warnings (expected, no remediation needed)
- STATE_LINT: PASS (0 errors, 2 warnings, 3 info)

## R50 IV Correct Status

`R50_PRODUCT_PROGRESS_REAL_BUT_CLOSEOUT_AND_INSTALLED_ARTIFACT_GAPS_REMAIN`
