# Package Identity Validator — R105

## Tool
tools/supervisor/validate_package_identity.py

## Checks
| # | File | Check | Fails If |
|---|------|-------|----------|
| 1 | evidence/evidence-declaration.yaml | run_id | Does not match expected |
| 2 | evidence/evidence-declaration.yaml | sprint_id | Does not match expected |
| 3 | supervisor/latest-cycle-summary.md | stream_identity | Different stream detected |
| 4 | supervisor/evidence-review.md | stream_identity | Different stream detected |
| 5 | supervisor/contradictions.md | stream_identity | Different stream detected |
| 6 | state/context-pack.yaml | latest_sprint_stream | Different stream detected |
| 7 | state/selected-product-gaps.json | freshness | Sprint mismatch (stale) |

## Behavior
- Returns `valid: true` only if zero violations
- WRONG_STREAM and STALE count as violations
- UNVERIFIABLE does not fail (file missing or unparseable)
- MATCH is positive confirmation

## Tests (16)
- Helper unit tests: sprint extraction, stream detection
- Clean package passes (7+ checks all MATCH)
- Contaminated package fails (5+ violations detected)
- Individual wrong-stream detection: cycle summary, evidence-review, contradictions, context-pack
- Stale gaps detection
- Declaration convenience wrapper
- Missing ZIP handling
