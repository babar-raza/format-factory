# R73 Work-Ahead Policy

**Sprint:** FORMAT-FACTORY-R73-DELIVERY-PACKAGE-TRUTH-PRODUCT-ADVANCEMENT-GATE-READINESS-MEGA-TRAIN-001
**Date:** 2026-05-29

---

## Principle

Work-ahead in R73 means real product advancement, not status documentation. For each format track:

- **RELEASE_CANDIDATE_BACKED_BY_TESTS**: install/import/smoke from wheel; new tests if advancing
- **PACKAGE_ONLY_PROBE**: do not claim gate advancement; document accurately
- **GATE8_BLOCKED**: prepare review packet; do not approve
- **GATE11_BLOCKED**: prepare approval packet; do not approve

## Forbidden Work-Ahead Actions

- Changing registry gate status without test evidence
- Claiming format "advanced" without actual source/test changes
- Claiming Gate 8/11 approval without human external approval
- Adding "commercial_product_ready: true" to any format
- Rebuilding package artifacts without SHA update in manifest (creates SHA drift)

## Required Work-Ahead Tracking

For R74:
1. Gate 8 human review for ODS/ODT/QOI/XCF/DIF/PPM (blocked on external approval)
2. Gate 11 Babar Raza approval for FODS and FODT (blocked on external approval)
3. Python OSS publication for 10 packages (blocked on external upload approval)
4. .NET NuGet publication for 2 packages (blocked on external upload + Gate 11)
5. Git push (blocked on external authorization)
6. CSV/TSV Gate 9 normalization (can start in R74)
