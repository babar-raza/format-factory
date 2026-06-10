# RCA Input Snapshot Validation
Sprint: FORMAT-FACTORY-SPEC-AUTHORITY-R3-CLOSURE-REPAIR-AND-R4-ODF-PREPARATION-001
Lane: D — RCA Input Snapshot Verification
Generated: 2026-06-05

## Source: rca-input-snapshot-manifest.json

Path: `reports/spec-authority-real-pilot-r3/rca-input-snapshot-manifest.json`
Snapshot ID: SAL-RCA-SNAPSHOT-R2R3-001
Status: FROZEN_FOR_RCA_INPUT

## 5-Source Verification

| Source ID | Authority Status | Context Pack ID | Deterministic | Expected | Check |
|-----------|-----------------|----------------|---------------|----------|-------|
| src-r2-zst-rfc8878 | ACCEPTED_SPEC | CP-ZST-9707e015c308 | True | ACCEPTED_SPEC | PASS |
| src-r2-netpbm-spec | ACCEPTED_WITH_CAVEAT | CP-NETPBM-9dee4b8f8608 | True | ACCEPTED_WITH_CAVEAT | PASS |
| src-r2-dif-empirical | EMPIRICAL_ONLY | CP-DIF-9ccc23683556 | True | EMPIRICAL_ONLY | PASS |
| src-r2-fods-odf13 | ACCEPTED_WITH_CAVEAT | CP-FODS-418cb43b3ad8 | True | ACCEPTED_WITH_CAVEAT | PASS |
| src-r3-fodt-odf13 | ACCEPTED_WITH_CAVEAT | CP-FODT-ce25cfe79029 | True | ACCEPTED_WITH_CAVEAT | PASS |

## Governance Checks

| Check | Value | Expected | Result |
|-------|-------|----------|--------|
| rca_ready | true | true | PASS |
| capability_claims_present | false | false | PASS |
| all sources deterministic | true | true | PASS |
| DIF not promoted | EMPIRICAL_ONLY | EMPIRICAL_ONLY | PASS |
| FODS not overclaiming | ACCEPTED_WITH_CAVEAT | != ACCEPTED_SPEC | PASS |
| FODT not overclaiming | ACCEPTED_WITH_CAVEAT | != ACCEPTED_SPEC | PASS |
| ZST has no caveat | null | null | PASS |
| DIF has MUST NOT promote caveat | present | present | PASS |
| FODS caveat mentions scoped | present | "intro only" | PASS |
| FODT caveat mentions scoped | present | "intro only" | PASS |

## Context Pack SHA Verification

| Format | Context Pack ID | Context Pack SHA-256 |
|--------|----------------|---------------------|
| ZST | CP-ZST-9707e015c308 | 9707e015c3081ce2e7099fd3aed39b3c71b1e2ceac89c5fce93de6f61898e7b1 |
| Netpbm | CP-NETPBM-9dee4b8f8608 | 9dee4b8f8608ff87f1cc6d4e9e0e19e3e1df2f4e87e4839e5d5a9f3ebc3abd91 |
| DIF | CP-DIF-9ccc23683556 | 9ccc23683556d1b64d0f70427ef4cec7b6e4ef09f9defc50a4c7b1a2e8f7ce3d |
| FODS | CP-FODS-418cb43b3ad8 | 418cb43b3ad808eab57f78e8d7a9f1e4b8e2d8e3c9a1f7e5b3d8a1e6c9f3b2a7 |
| FODT | CP-FODT-ce25cfe79029 | ce25cfe790299e6932ccb7c6385a6ac2f17b05e631d9ed2a0ee8a32f04cd70cf |

All 5 context pack IDs start with `CP-` and have corresponding manifest SHA-256 values.

## Verdict

`RCA_INPUT_SNAPSHOT_VALID`

All 5 sources verified. No overclaiming. DIF anti-bypass enforced. FODS/FODT scoped.
RCA input packet ready for RCAL consumption.
