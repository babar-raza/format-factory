# R107 Preflight Baseline

**Sprint:** FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001
**Date:** 2026-06-03
**Git HEAD:** 3a86a05295cb4b82ed40a3408b0612a90f93643c (uncommitted R105+R106 work)

## Test Baseline
| Track | Tests | Status |
|-------|-------|--------|
| Python (all) | 2903 | PASS |
| FODS .NET | 375 | PASS |
| FODT .NET | 363 | PASS |
| Netpbm .NET | 291 | PASS |
| **.NET Total** | **1029** | PASS |
| **Grand Total** | **3932** | PASS |

## API Baseline
| Format | Public Methods | Properties |
|--------|---------------|------------|
| FODS | 32+ | 5 |
| FODT | 26+ | 8 |
| Netpbm | 26+ | 5 |

## R106 Status
- Autonomous-cycle: exit 0, 20/20 ACCEPTED
- Review package SHA: bd9ed03707f7c39d2b4e70b120af7097ffda55f92b701c1d48e5ec45d1447adc

## Evidence Governance Defects (from R107 prompt)
1. context-pack-contamination-check.md — exists locally but reported missing in package
2. Skill transcripts — exist locally (12 files) but may not be in review package
3. Source diffs — exist locally (6 files) but may not be in review package
4. Context-pack latest_sprint points to Skills R103
5. Supervisor evidence-review reviews Skills R103 inside Mainstream R106 package
6. state/selected-product-gaps.json is stale R98
7. Work-item grades are path-existence based

## Governance
- Skill registry: 13 active skills
- Product-code ledger: 87 entries, all validated
- Gate status: FODS/FODT/Netpbm G1-G10 PASS, G11 NOT_STARTED
