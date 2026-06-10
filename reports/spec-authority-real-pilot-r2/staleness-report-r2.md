# Staleness Report — R2
Pilot: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-REAL-PILOT-R2-001
Generated: 2026-06-05

## Results

All 4 real sources are FRESH. Synthetic stale correctly detected for all 4.

| Source | Current SHA | Fresh Check | Synthetic Stale Detected |
|--------|------------|-------------|--------------------------|
| ZST | 8ee6be03... | NOT_STALE | YES |
| Netpbm | 0077171016... | NOT_STALE | YES |
| DIF | (empirical) | NOT_STALE | YES |
| FODS | (scoped) | NOT_STALE | YES |

## Method

- Fresh check: `check_staleness(sid, current_sha256, artifacts_dir)` — compares stored digest SHA vs current
- Synthetic stale: `check_staleness(sid, "deadbeef" * 8, artifacts_dir)` — mutated SHA forces stale=True

## R1 Carry-Forward

D-STALE-001 (auto-recomputation queue trigger) remains not implemented.
Detection of staleness is proven; auto-trigger deferred to R3 per R1 recommendation.
