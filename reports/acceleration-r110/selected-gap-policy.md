# Selected-Gap Policy — Acceleration R110

## Policy
Acceleration stream does NOT consume selected-product-gaps.json. That file is for Mainstream product work.

## Stale R98 Gaps
- R109 added `classify_gap_freshness()` which classifies R98 vs R109 as "archived" (11+ sprints behind)
- R109 added `detect_stale_gaps()` which flags archived gaps as violations
- SEVERITY_MAP["stale_gaps"] = "critical" — blocks continuation

## R110 Verification
- No stale R98 gaps active in acceleration state
- Acceleration next-work-items contain only `acceleration-forward` source items
- No `product-factory` source items in acceleration NWI
- classify_gap_freshness("R98", "R110") = "archived" (confirmed in R109 tests)

## Conclusion
Selected-gap freshness policy is ENFORCED. Acceleration correctly generates its own forward work from STREAM_FORWARD_WORK, not from product gaps.
